"""Application service for upload jobs."""

import logging
from pathlib import Path
from typing import BinaryIO
from uuid import uuid4

from app.core.errors import UploadValidationError
from app.core.logging import log_extra
from app.domain.jobs.models import CreateJob, Job, JobStatus
from app.domain.jobs.ports import JobRepository, UploadedFileStorage
from app.domain.templates.ports import TemplateRepository

logger = logging.getLogger(__name__)


class JobService:
    """Coordinate job upload and retrieval use cases."""

    def __init__(
        self,
        *,
        job_repository: JobRepository,
        template_repository: TemplateRepository,
        uploaded_file_storage: UploadedFileStorage,
        allowed_extensions: tuple[str, ...],
    ) -> None:
        self._job_repository = job_repository
        self._template_repository = template_repository
        self._uploaded_file_storage = uploaded_file_storage
        self._allowed_extensions = tuple(extension.lower() for extension in allowed_extensions)

    def create_uploaded_job(
        self,
        *,
        template_id: str,
        original_filename: str,
        file: BinaryIO,
        tenant_id: str | None = None,
        user_id: str | None = None,
    ) -> Job:
        """Validate and store an uploaded workbook, then persist its job record."""
        self._template_repository.get_template(template_id)
        
        import os
        safe_filename = os.path.basename(original_filename)
        if not safe_filename:
            safe_filename = "unnamed_upload.xlsx"
            
        self._validate_extension(safe_filename)

        job_id = str(uuid4())
        stored_filename = self._uploaded_file_storage.save(
            file=file,
            original_filename=safe_filename,
            job_id=job_id,
        )
        job = self._job_repository.create_job(
            CreateJob(
                job_id=job_id,
                template_id=template_id,
                original_filename=safe_filename,
                stored_filename=stored_filename,
                status=JobStatus.UPLOADED,
                tenant_id=tenant_id,
                user_id=user_id,
            )
        )
        logger.info(
            "job_uploaded",
            extra=log_extra(job_id=job.job_id, template_id=job.template_id),
        )
        return job

    def get_job(self, job_id: str, tenant_id: str | None = None) -> Job:
        """Return job metadata by identifier, ensuring it belongs to the tenant."""
        from app.core.errors import JobNotFoundError
        job = self._job_repository.get_job(job_id)
        if tenant_id and job.tenant_id != tenant_id:
            raise JobNotFoundError(f"Job {job_id} not found in tenant")
        return job

    def _validate_extension(self, filename: str) -> None:
        extension = Path(filename).suffix.lower()
        if not extension or extension not in self._allowed_extensions:
            raise UploadValidationError(
                "Uploaded file extension is not allowed",
                details={
                    "filename": filename,
                    "allowed_extensions": list(self._allowed_extensions),
                },
            )
