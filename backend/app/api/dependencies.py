"""FastAPI dependency providers."""

from app.application.jobs.service import JobService
from app.application.processing.cleaning_service import DataCleaningService
from app.application.processing.dataset_builder import IntermediateDatasetBuilder
from app.application.processing.service import ProcessingService
from app.application.processing.stages import ColumnRemovalStage, NormalizationStage
from app.application.rules.service import RuleEvaluationService
from app.application.rules.transformations import RuleTransformationApplier
from app.application.templates.service import TemplateService
from app.application.workbooks.column_mapper import TemplateColumnMapper
from app.application.workbooks.intelligence_service import WorkbookIntelligenceService
from app.application.workbooks.validation import WorkbookValidationService
from app.core.settings import get_settings
from app.domain.outputs.ports import OutputStorage, ProcessingReportRepository
from app.domain.rules.evaluator import RuleEvaluator
from app.domain.rules.operators import RuleOperatorRegistry, default_operators
from app.domain.workbooks.synonyms import GlobalSynonymDictionary, IndustrySynonymDictionary
from app.infrastructure.excel.openpyxl_loader import OpenPyXLWorkbookLoader
from app.infrastructure.excel.output_builder import OpenPyXLOutputWorkbookBuilder
from app.infrastructure.files.local_outputs import LocalOutputStorage
from app.infrastructure.files.local_uploads import LocalUploadedFileStorage
from app.infrastructure.persistence.sqlite_jobs import SQLiteJobRepository
from app.infrastructure.rules.filesystem import FileSystemRulePackRepository
from app.infrastructure.rules.rapidfuzz_operator import RapidFuzzEqualsOperator
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository

_global_dict: GlobalSynonymDictionary | None = None
_industry_dict: IndustrySynonymDictionary | None = None


def _get_global_dict() -> GlobalSynonymDictionary:
    global _global_dict
    if _global_dict is None:
        _global_dict = GlobalSynonymDictionary()
    return _global_dict


def _get_industry_dict() -> IndustrySynonymDictionary:
    global _industry_dict
    if _industry_dict is None:
        _industry_dict = IndustrySynonymDictionary(_get_global_dict())
    return _industry_dict


def get_template_service() -> TemplateService:
    settings = get_settings()
    repository = FileSystemTemplateRepository(settings.resolved_template_root)
    return TemplateService(repository)


def get_job_service() -> JobService:
    settings = get_settings()
    template_repository = FileSystemTemplateRepository(settings.resolved_template_root)
    job_repository = SQLiteJobRepository(settings.resolved_database_path)
    uploaded_file_storage = LocalUploadedFileStorage(
        settings.resolved_upload_dir,
        settings.max_upload_size_mb,
    )
    return JobService(
        job_repository=job_repository,
        template_repository=template_repository,
        uploaded_file_storage=uploaded_file_storage,
        allowed_extensions=settings.allowed_extensions,
    )


def _build_workbook_validation_service(
    template_repository: FileSystemTemplateRepository,
    workbook_loader: OpenPyXLWorkbookLoader,
) -> WorkbookValidationService:
    return WorkbookValidationService(
        template_repository=template_repository,
        workbook_loader=workbook_loader,
        column_mapper=TemplateColumnMapper(
            global_dict=_get_global_dict(),
            industry_dict=_get_industry_dict(),
        ),
        global_dict=_get_global_dict(),
        industry_dict=_get_industry_dict(),
    )


def get_workbook_validation_service() -> WorkbookValidationService:
    settings = get_settings()
    template_repository = FileSystemTemplateRepository(settings.resolved_template_root)
    return _build_workbook_validation_service(
        template_repository, OpenPyXLWorkbookLoader(),
    )


def get_intelligence_service() -> WorkbookIntelligenceService:
    return WorkbookIntelligenceService(
        workbook_loader=OpenPyXLWorkbookLoader(),
        column_mapper=TemplateColumnMapper(
            global_dict=_get_global_dict(),
            industry_dict=_get_industry_dict(),
        ),
        global_dict=_get_global_dict(),
    )


def get_processing_service() -> ProcessingService:
    settings = get_settings()
    template_repository = FileSystemTemplateRepository(settings.resolved_template_root)
    workbook_loader = OpenPyXLWorkbookLoader()
    job_repository = SQLiteJobRepository(settings.resolved_database_path)
    rule_pack_repository = FileSystemRulePackRepository(
        template_root=settings.resolved_template_root,
        template_repository=template_repository,
    )
    return ProcessingService(
        job_repository=job_repository,
        template_repository=template_repository,
        uploaded_file_storage=LocalUploadedFileStorage(
            settings.resolved_upload_dir,
            settings.max_upload_size_mb,
        ),
        workbook_loader=workbook_loader,
        workbook_validation_service=_build_workbook_validation_service(
            template_repository, workbook_loader,
        ),
        cleaning_service=DataCleaningService(),
        dataset_builder=IntermediateDatasetBuilder(),
        column_removal_stage=ColumnRemovalStage(),
        normalization_stage=NormalizationStage(),
        rule_evaluation_service=_build_rule_evaluation_service(
            rule_pack_repository=rule_pack_repository,
        ),
        transformation_applier=RuleTransformationApplier(),
        output_workbook_builder=OpenPyXLOutputWorkbookBuilder(),
        output_storage=LocalOutputStorage(settings.resolved_output_dir),
        processing_report_repository=job_repository,
    )


def get_rule_evaluation_service() -> RuleEvaluationService:
    settings = get_settings()
    template_repository = FileSystemTemplateRepository(settings.resolved_template_root)
    rule_pack_repository = FileSystemRulePackRepository(
        template_root=settings.resolved_template_root,
        template_repository=template_repository,
    )
    return _build_rule_evaluation_service(rule_pack_repository=rule_pack_repository)


def get_processing_report_repository() -> ProcessingReportRepository:
    settings = get_settings()
    return SQLiteJobRepository(settings.resolved_database_path)


def get_output_storage() -> OutputStorage:
    settings = get_settings()
    return LocalOutputStorage(settings.resolved_output_dir)


def _build_rule_evaluation_service(
    *,
    rule_pack_repository: FileSystemRulePackRepository,
) -> RuleEvaluationService:
    return RuleEvaluationService(
        rule_evaluator=RuleEvaluator(
            RuleOperatorRegistry(
                operators=(*default_operators(), RapidFuzzEqualsOperator()),
            )
        ),
        rule_pack_repository=rule_pack_repository,
    )