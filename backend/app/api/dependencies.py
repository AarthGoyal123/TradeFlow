"""FastAPI dependency providers."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.auth.google import GoogleOAuthProvider
from app.application.auth.service import AuthService
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
from app.domain.auth.ports import AuthRepository
from app.domain.jobs.ports import JobExecutor, UploadedFileStorage
from app.domain.outputs.ports import OutputStorage, ProcessingReportRepository
from app.domain.rules.evaluator import RuleEvaluator
from app.domain.rules.operators import RuleOperatorRegistry, default_operators
from app.domain.workbooks.synonyms import GlobalSynonymDictionary, IndustrySynonymDictionary
from app.infrastructure.database import SQLAlchemyJobRepository, get_session_factory
from app.infrastructure.database.auth_repository import SQLAlchemyAuthRepository
from app.infrastructure.excel.openpyxl_loader import OpenPyXLWorkbookLoader
from app.infrastructure.excel.output_builder import OpenPyXLOutputWorkbookBuilder
from app.infrastructure.files.local_outputs import LocalOutputStorage
from app.infrastructure.files.local_uploads import LocalUploadedFileStorage
from app.infrastructure.files.s3_storage import S3OutputStorage, S3UploadedFileStorage
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


def _get_uploaded_file_storage() -> UploadedFileStorage:
    settings = get_settings()
    if settings.storage_backend == "s3":
        if not all(
            [
                settings.s3_endpoint_url,
                settings.s3_access_key,
                settings.s3_secret_key,
                settings.s3_bucket_name,
            ]
        ):
            raise ValueError("S3 storage requested but S3 configuration is incomplete.")
        return S3UploadedFileStorage(
            endpoint_url=settings.s3_endpoint_url or "",
            access_key=settings.s3_access_key or "",
            secret_key=settings.s3_secret_key or "",
            bucket_name=settings.s3_bucket_name or "",
            region=settings.s3_region or "us-east-1",
            max_size_mb=settings.max_upload_size_mb,
            allowed_extensions=settings.allowed_extensions,
        )
    elif settings.storage_backend == "supabase":
        from app.infrastructure.files.supabase_storage import SupabaseUploadedFileStorage

        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("Supabase storage requested but configuration is incomplete.")
        return SupabaseUploadedFileStorage(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_key,
            bucket_name=settings.supabase_bucket_name,
        )
    return LocalUploadedFileStorage(
        settings.resolved_upload_dir,
        settings.max_upload_size_mb,
    )


def _get_output_storage() -> OutputStorage:
    settings = get_settings()
    if settings.storage_backend == "s3":
        if not all(
            [
                settings.s3_endpoint_url,
                settings.s3_access_key,
                settings.s3_secret_key,
                settings.s3_bucket_name,
            ]
        ):
            raise ValueError("S3 storage requested but S3 configuration is incomplete.")
        return S3OutputStorage(
            endpoint_url=settings.s3_endpoint_url or "",
            access_key=settings.s3_access_key or "",
            secret_key=settings.s3_secret_key or "",
            bucket_name=settings.s3_bucket_name or "",
            region=settings.s3_region or "us-east-1",
        )
    elif settings.storage_backend == "supabase":
        from app.infrastructure.files.supabase_storage import SupabaseOutputStorage

        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("Supabase storage requested but configuration is incomplete.")
        return SupabaseOutputStorage(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_key,
            bucket_name=settings.supabase_bucket_name,
        )
    return LocalOutputStorage(settings.resolved_output_dir)


def get_db_session() -> Generator[Session, None, None]:
    """Dependency provider for SQLAlchemy session."""
    session_factory = get_session_factory()
    with session_factory() as session:
        yield session


def get_auth_repository(
    session: Session = Depends(get_db_session),  # noqa: B008
) -> AuthRepository:
    """Dependency provider for AuthRepository."""
    return SQLAlchemyAuthRepository(session)


def get_auth_service(
    auth_repository: AuthRepository = Depends(get_auth_repository),  # noqa: B008
) -> AuthService:
    """Dependency provider for AuthService."""
    return AuthService(auth_repository)


def get_google_oauth_provider() -> GoogleOAuthProvider:
    """Dependency provider for GoogleOAuthProvider."""
    return GoogleOAuthProvider()


def get_job_service() -> JobService:
    settings = get_settings()
    template_repository = FileSystemTemplateRepository(settings.resolved_template_root)
    job_repository = SQLAlchemyJobRepository(get_session_factory())
    uploaded_file_storage = _get_uploaded_file_storage()
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
        template_repository,
        OpenPyXLWorkbookLoader(),
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
    job_repository = SQLAlchemyJobRepository(get_session_factory())
    rule_pack_repository = FileSystemRulePackRepository(
        template_root=settings.resolved_template_root,
        template_repository=template_repository,
    )
    return ProcessingService(
        job_repository=job_repository,
        template_repository=template_repository,
        uploaded_file_storage=_get_uploaded_file_storage(),
        workbook_loader=workbook_loader,
        workbook_validation_service=_build_workbook_validation_service(
            template_repository,
            workbook_loader,
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
        output_storage=_get_output_storage(),
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
    return SQLAlchemyJobRepository(get_session_factory())


def get_output_storage() -> OutputStorage:
    return _get_output_storage()


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


ProcessingServiceDependency = Annotated[ProcessingService, Depends(get_processing_service)]


def get_job_executor(
    processing_service: ProcessingServiceDependency,
) -> JobExecutor:
    settings = get_settings()

    if settings.job_executor == "celery":
        from app.infrastructure.jobs.celery_executor import CeleryJobExecutor

        return CeleryJobExecutor()
    else:
        from app.infrastructure.jobs.local_executor import SynchronousJobExecutor

        return SynchronousJobExecutor(processing_service)
