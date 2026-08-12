from pathlib import Path

from openpyxl import Workbook

from app.application.processing.cleaning_service import DataCleaningService
from app.application.processing.dataset_builder import IntermediateDatasetBuilder
from app.application.processing.service import ProcessingService
from app.application.processing.stages import ColumnRemovalStage, NormalizationStage
from app.application.rules.service import RuleEvaluationService
from app.application.rules.transformations import RuleTransformationApplier
from app.application.workbooks.column_mapper import TemplateColumnMapper
from app.application.workbooks.validation import WorkbookValidationService
from app.domain.jobs.models import CreateJob, JobStatus
from app.domain.outputs.models import OutputArtifact
from app.domain.outputs.ports import (
    OutputStorage,
)
from app.domain.rules.models import RulePackDefinition
from app.domain.templates.models import (
    ColumnsConfig,
    OutputConfig,
    OutputFiles,
    PipelineConfig,
    RulePack,
    TemplateConfig,
    TemplateDefinition,
    WorkbookConfig,
)
from app.infrastructure.excel.openpyxl_loader import OpenPyXLWorkbookLoader
from app.infrastructure.files.local_outputs import LocalOutputStorage
from app.infrastructure.files.local_uploads import LocalUploadedFileStorage
from app.infrastructure.persistence.sqlite_jobs import SQLiteJobRepository


def test_processing_service_creates_normalized_intermediate_dataset(tmp_path) -> None:
    service, job_repository = _processing_service(tmp_path, _template(remove_columns=["port"]))
    job = _create_job_with_workbook(
        tmp_path,
        job_repository,
        rows=[
            ["Consignee", "Port", "Carrier"],
            ["  ACME   EXPORTS ", "Mundra", " MAERSK  LINE "],
        ],
    )

    result = service.process_job(job.job_id)
    updated_job = job_repository.get_job(job.job_id)

    assert result.dataset is not None
    assert result.dataset.row_count == 1
    assert result.dataset.fields == ("consignee_name", "shipping_company")
    assert result.dataset.rows[0].source_row_number == 2
    assert result.dataset.rows[0].value_for("consignee_name") == "ACME EXPORTS"
    assert result.dataset.rows[0].value_for("shipping_company") == "MAERSK LINE"
    assert [entry.stage for entry in result.progress] == [
        "job",
        "validation",
        "dataset",
        "column_removal",
        "normalization",
        "rules",
        "transformations",
        "outputs",
        "job",
    ]
    assert updated_job.status == JobStatus.COMPLETED


def test_processing_service_marks_job_failed_for_invalid_workbook(tmp_path) -> None:
    service, job_repository = _processing_service(tmp_path, _template(remove_columns=[]))
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    stored_filename = "job-1.xlsx"
    (upload_dir / stored_filename).write_bytes(b"not a workbook")
    job = job_repository.create_job(
        CreateJob(
            job_id="job-1",
            template_id="indian_rice_exports",
            original_filename="broken.xlsx",
            stored_filename=stored_filename,
        )
    )

    result = service.process_job(job.job_id)
    updated_job = job_repository.get_job(job.job_id)

    assert result.dataset is None
    assert result.errors[0].code == "workbook_validation_error"
    assert result.errors[0].message == "Workbook validation failed"
    assert updated_job.status == JobStatus.FAILED


def _processing_service(
    tmp_path,
    template: TemplateDefinition,
) -> tuple[ProcessingService, SQLiteJobRepository]:
    template_repository = _TemplateRepository(template)
    workbook_loader = OpenPyXLWorkbookLoader()
    job_repository = SQLiteJobRepository(tmp_path / "tradeflow.sqlite")
    return ProcessingService(
        job_repository=job_repository,
        template_repository=template_repository,
        uploaded_file_storage=LocalUploadedFileStorage(tmp_path / "uploads", 50),
        workbook_loader=workbook_loader,
        workbook_validation_service=WorkbookValidationService(
            template_repository=template_repository,
            workbook_loader=workbook_loader,
            column_mapper=TemplateColumnMapper(),
        ),
        dataset_builder=IntermediateDatasetBuilder(),
        cleaning_service=DataCleaningService(),
        column_removal_stage=ColumnRemovalStage(),
        normalization_stage=NormalizationStage(),
        rule_evaluation_service=RuleEvaluationService(
            rule_pack_repository=_RulePackRepository(),
        ),
        transformation_applier=RuleTransformationApplier(),
        output_workbook_builder=_StubOutputWorkbookBuilder(),
        output_storage=LocalOutputStorage(tmp_path / "outputs"),
        processing_report_repository=job_repository,
    ), job_repository


class _RulePackRepository:
    def list_rule_packs(self, template_id: str) -> tuple[RulePackDefinition, ...]:
        return ()


class _StubOutputWorkbookBuilder:
    def build(
        self,
        *,
        job_id: str,
        dataset: object,
        rule_report: object,
        output_storage: OutputStorage,
    ) -> tuple[OutputArtifact, ...]:
        return ()


def _create_job_with_workbook(
    tmp_path,
    job_repository: SQLiteJobRepository,
    *,
    rows: list[list[str]],
):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    stored_filename = "job-1.xlsx"
    workbook_path = upload_dir / stored_filename
    _create_workbook(workbook_path, rows=rows)
    return job_repository.create_job(
        CreateJob(
            job_id="job-1",
            template_id="indian_rice_exports",
            original_filename="shipment.xlsx",
            stored_filename=stored_filename,
        )
    )


def _create_workbook(path: Path, *, rows: list[list[str]]) -> None:
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Shipments"
    for row in rows:
        worksheet.append(row)
    workbook.save(path)


def _template(*, remove_columns: list[str]) -> TemplateDefinition:
    return TemplateDefinition(
        config=TemplateConfig(
            id="indian_rice_exports",
            name="Indian Rice Export Shipments",
            version="0.1.0",
            workbook=WorkbookConfig(sheet_strategy="first_sheet"),
            enabled_modules=["validation"],
        ),
        columns=ColumnsConfig.model_validate(
            {
                "required_fields": [
                    {"field": "consignee_name", "aliases": ["Consignee"]},
                    {"field": "port", "aliases": ["Port"]},
                ],
                "optional_fields": [
                    {"field": "shipping_company", "aliases": ["Carrier"]},
                ],
                "remove_columns": remove_columns,
            }
        ),
        pipeline=PipelineConfig(steps=["validation"]),
        output=OutputConfig(files=OutputFiles(), review_threshold=0.75),
        keyword_rules=RulePack(),
        regex_rules=RulePack(),
        fuzzy_matches=RulePack(),
    )


class _TemplateRepository:
    def __init__(self, template: TemplateDefinition) -> None:
        self._template = template

    def list_templates(self) -> list[TemplateDefinition]:
        return [self._template]

    def get_template(self, template_id: str) -> TemplateDefinition:
        return self._template
