"""Synchronous processing workflow to an intermediate dataset."""

import logging
import traceback
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.jobs.models import Job
    from app.domain.templates.models import Template
    from app.domain.processing.dataset import IntermediateDataset

from app.application.processing.cleaning_service import DataCleaningService
from app.application.processing.dataset_builder import IntermediateDatasetBuilder
from app.application.processing.stages import ColumnRemovalStage, NormalizationStage
from app.application.rules.service import RuleEvaluationService
from app.application.rules.transformations import RuleTransformationApplier
from app.application.workbooks.validation import WorkbookValidationService
from app.core.errors import WorkbookValidationError
from app.core.logging import log_extra
from app.domain.jobs.models import JobStatus
from app.domain.jobs.ports import JobRepository, UploadedFileStorage
from app.domain.outputs.models import OutputArtifact, ProcessingSummary
from app.domain.outputs.ports import (
    OutputStorage,
    OutputWorkbookBuilder,
    ProcessingReportRepository,
)
from app.domain.processing.models import ProcessingIssue, ProcessingProgress, ProcessingResult
from app.domain.rules.models import RuleExecutionReport
from app.domain.templates.ports import TemplateRepository
from app.domain.workbooks.cleaning import DatasetCleaningConfig, FieldCleaningRule
from app.domain.workbooks.models import WorkbookValidationResult
from app.domain.workbooks.ports import WorkbookLoader, WorksheetReader

logger = logging.getLogger(__name__)


class ProcessingService:
    """Process an uploaded job into a normalized intermediate dataset."""

    def __init__(
        self,
        *,
        job_repository: JobRepository,
        template_repository: TemplateRepository,
        uploaded_file_storage: UploadedFileStorage,
        workbook_loader: WorkbookLoader,
        workbook_validation_service: WorkbookValidationService,
        dataset_builder: IntermediateDatasetBuilder,
        cleaning_service: DataCleaningService,
        column_removal_stage: ColumnRemovalStage,
        normalization_stage: NormalizationStage,
        rule_evaluation_service: RuleEvaluationService,
        transformation_applier: RuleTransformationApplier,
        output_workbook_builder: OutputWorkbookBuilder,
        output_storage: OutputStorage,
        processing_report_repository: ProcessingReportRepository,
    ) -> None:
        self._job_repository = job_repository
        self._template_repository = template_repository
        self._uploaded_file_storage = uploaded_file_storage
        self._workbook_loader = workbook_loader
        self._workbook_validation_service = workbook_validation_service
        self._dataset_builder = dataset_builder
        self._cleaning_service = cleaning_service
        self._column_removal_stage = column_removal_stage
        self._normalization_stage = normalization_stage
        self._rule_evaluation_service = rule_evaluation_service
        self._transformation_applier = transformation_applier
        self._output_workbook_builder = output_workbook_builder
        self._output_storage = output_storage
        self._processing_report_repository = processing_report_repository

    def process_job(self, job_id: str) -> ProcessingResult:
        """Run synchronous processing from uploaded workbook to intermediate dataset."""
        progress: list[ProcessingProgress] = []
        job = self._job_repository.get_job(job_id)
        template = self._template_repository.get_template(job.template_id)
        workbook_path = self._uploaded_file_storage.path_for(job.stored_filename)
        rule_report: RuleExecutionReport | None = None
        summary: ProcessingSummary | None = None

        self._job_repository.update_status(job_id, JobStatus.PROCESSING)
        self._record(progress, "job", "processing", "Job processing started")

        try:
            dataset, rule_report = self._execute_pipeline(job, template, workbook_path, progress)

            artifacts = self._output_workbook_builder.build(
                job_id=job_id,
                dataset=dataset,
                rule_report=rule_report,
                output_storage=self._output_storage,
            )
            summary = self._processing_report_repository.save_summary(
                self._build_summary(
                    job_id=job_id,
                    template_id=job.template_id,
                    rule_report=rule_report,
                    artifacts=artifacts,
                )
            )
            self._record(progress, "outputs", "completed", "Output workbooks generated")

        except WorkbookValidationError as exc:
            self._job_repository.update_status(job_id, JobStatus.FAILED)
            logger.info(
                "job_processing_failed",
                extra=log_extra(job_id=job_id, template_id=job.template_id),
            )
            return ProcessingResult(
                job_id=job_id,
                template_id=job.template_id,
                dataset=None,
                progress=tuple(progress),
                errors=(
                    ProcessingIssue(
                        code=exc.code,
                        message=exc.message,
                        details=exc.details,
                    ),
                ),
            )
        except Exception as exc:
            traceback.print_exc()
            print("\nACTUAL ERROR:", repr(exc), "\n")

            self._job_repository.update_status(job_id, JobStatus.FAILED)

            logger.exception(
                "job_processing_failed",
                extra=log_extra(job_id=job_id, template_id=job.template_id),
            )

            raise

        self._job_repository.update_status(job_id, JobStatus.COMPLETED)
        self._record(progress, "job", "completed", "Job processing completed")
        logger.info(
            "job_processing_completed",
            extra=log_extra(job_id=job_id, template_id=job.template_id),
        )
        return ProcessingResult(
            job_id=job_id,
            template_id=job.template_id,
            dataset=dataset,
            progress=tuple(progress),
            rule_report=rule_report,
            summary=summary,
        )

    def _execute_pipeline(
        self,
        job: "Job",
        template: "Template",
        workbook_path: Path,
        progress: list[ProcessingProgress],
    ) -> tuple["IntermediateDataset", RuleExecutionReport]:
        validation_result = self._workbook_validation_service.validate(
            template_id=job.template_id,
            workbook_path=workbook_path,
        )
        if self._is_fatal_validation_result(validation_result):
            self._record(progress, "validation", "failed", "Workbook validation failed")
            raise WorkbookValidationError(
                "Workbook validation failed",
                details={"issues": [asdict(issue) for issue in validation_result.issues]},
            )
        self._record(
            progress,
            "validation",
            "completed" if validation_result.valid else "partial",
            "Workbook validation completed"
            if validation_result.valid
            else f"Workbook validation completed with {len(validation_result.issues)} issue(s)",
        )

        worksheet = self._select_validated_worksheet(
            workbook_path=workbook_path,
            sheet_name=validation_result.sheet_name,
        )
        dataset = self._dataset_builder.build(
            validation_result=validation_result,
            worksheet=worksheet,
        )
        self._record(progress, "dataset", "completed", "Intermediate dataset created")

        dataset = self._column_removal_stage.run(dataset=dataset, template=template)
        self._record(progress, "column_removal", "completed", "Configured columns removed")

        dataset = self._normalization_stage.run(dataset=dataset)
        self._record(progress, "normalization", "completed", "Dataset values normalized")

        rule_report = self._rule_evaluation_service.evaluate_template_rules(
            dataset=dataset,
            review_threshold=template.output.review_threshold,
        )
        self._record(progress, "rules", "completed", "Template rules evaluated")

        dataset = self._transformation_applier.apply(
            dataset=dataset,
            rule_report=rule_report,
        )
        self._record(progress, "transformations", "completed", "Rule transformations applied")

        if template.output.column_order:
            dataset = dataset.reorder(tuple(template.output.column_order))
            self._record(progress, "order", "completed", "Columns reordered per template")

        if template.output.cleaning:
            cleaning_config = DatasetCleaningConfig(
                field_rules={
                    field: FieldCleaningRule(
                        remove_phrases=tuple(spec.remove_phrases),
                        bank_keywords=tuple(spec.bank_keywords),
                        trim=spec.trim,
                        collapse_whitespace=spec.collapse_whitespace,
                    )
                    for field, spec in template.output.cleaning.items()
                }
            )
            dataset = self._cleaning_service.clean(
                dataset=dataset,
                cleaning_config=cleaning_config,
            )
            self._record(progress, "cleaning", "completed", "Field values cleaned per template")
            
        return dataset, rule_report

    def _select_validated_worksheet(
        self,
        *,
        workbook_path: Path,
        sheet_name: str | None,
    ) -> WorksheetReader:
        workbook = self._workbook_loader.load(workbook_path)
        if sheet_name is None:
            return workbook.first_sheet()
        sheet = workbook.sheet_by_name(sheet_name)
        if sheet is None:
            raise WorkbookValidationError(
                "Validated worksheet could not be reloaded",
                details={"sheet_name": sheet_name},
            )
        return sheet

    @staticmethod
    def _record(
        progress: list[ProcessingProgress],
        stage: str,
        status: str,
        message: str,
    ) -> None:
        progress.append(ProcessingProgress(stage=stage, status=status, message=message))

    @staticmethod
    def _is_fatal_validation_result(result: "WorkbookValidationResult") -> bool:
        fatal_codes = {"workbook_validation_error", "required_sheet_missing", "missing_sheet_name"}
        return any(issue.code in fatal_codes for issue in result.issues)

    @staticmethod
    def _build_summary(
        *,
        job_id: str,
        template_id: str,
        rule_report: RuleExecutionReport,
        artifacts: tuple[OutputArtifact, ...],
    ) -> ProcessingSummary:
        routes = [routed_row.route for routed_row in rule_report.routed_rows]
        return ProcessingSummary(
            job_id=job_id,
            template_id=template_id,
            total_rows=rule_report.row_count,
            clean_rows=routes.count("clean"),
            removed_rows=routes.count("removed"),
            needs_review_rows=routes.count("needs_review"),
            rule_matches=len(rule_report.matches),
            validation_findings=len(rule_report.validation_findings),
            outputs=artifacts,
        )
