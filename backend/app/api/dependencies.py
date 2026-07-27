"""FastAPI dependency providers."""

from app.application.jobs.service import JobService
from app.application.templates.service import TemplateService
from app.application.workbooks.column_mapper import TemplateColumnMapper
from app.application.workbooks.validation import WorkbookValidationService
from app.core.settings import get_settings
from app.infrastructure.excel.openpyxl_loader import OpenPyXLWorkbookLoader
from app.infrastructure.files.local_uploads import LocalUploadedFileStorage
from app.infrastructure.persistence.sqlite_jobs import SQLiteJobRepository
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository


def get_template_service() -> TemplateService:
    """Build the template application service."""
    settings = get_settings()
    repository = FileSystemTemplateRepository(settings.resolved_template_root)
    return TemplateService(repository)


def get_job_service() -> JobService:
    """Build the job application service."""
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


def get_workbook_validation_service() -> WorkbookValidationService:
    """Build the workbook validation application service."""
    settings = get_settings()
    template_repository = FileSystemTemplateRepository(settings.resolved_template_root)
    return WorkbookValidationService(
        template_repository=template_repository,
        workbook_loader=OpenPyXLWorkbookLoader(),
        column_mapper=TemplateColumnMapper(),
    )
