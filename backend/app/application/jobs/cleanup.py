"""Service for cleaning up old job artifacts."""

import logging
from datetime import UTC, datetime, timedelta

from app.domain.jobs.ports import JobRepository, UploadedFileStorage
from app.domain.outputs.ports import OutputStorage

logger = logging.getLogger(__name__)


class CleanupService:
    """Service to clean up expired artifacts for old jobs."""

    def __init__(
        self,
        job_repository: JobRepository,
        upload_storage: UploadedFileStorage,
        output_storage: OutputStorage,
        retention_days: int,
    ) -> None:
        """Initialize the cleanup service."""
        self._job_repository = job_repository
        self._upload_storage = upload_storage
        self._output_storage = output_storage
        self._retention_days = retention_days

    def cleanup_old_jobs(self) -> int:
        """Find old terminal jobs and delete their artifacts. Return number of jobs processed."""
        threshold = datetime.now(UTC) - timedelta(days=self._retention_days)
        old_jobs = self._job_repository.get_terminal_jobs_older_than(threshold)

        processed = 0
        for job in old_jobs:
            try:
                # We intentionally don't delete the database records for compliance/audit.
                # Just remove the files to save space.
                self._upload_storage.delete_upload(job.stored_filename)
                self._output_storage.delete_job_outputs(job.job_id)
                processed += 1
                logger.info("cleaned_up_job_artifacts", extra={"job_id": job.job_id})
            except Exception as e:
                logger.error("failed_to_cleanup_job", extra={"job_id": job.job_id, "error": str(e)})

        return processed
