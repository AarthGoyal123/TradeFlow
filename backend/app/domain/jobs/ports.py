"""Ports for job persistence and file storage."""

from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Protocol

from app.domain.jobs.models import CreateJob, Job, JobStatus


class JobRepository(Protocol):
    """Persist and retrieve jobs."""

    def create_job(self, job: CreateJob) -> Job:
        """Create a persisted job."""
        ...

    def get_job(self, job_id: str) -> Job:
        """Return one job by identifier."""
        ...

    def update_status(self, job_id: str, status: JobStatus) -> Job:
        """Update job status and return the updated job."""
        ...

    def get_terminal_jobs_older_than(self, threshold: datetime) -> list[Job]:
        """Return jobs in terminal states (completed/failed) older than the threshold."""
        ...


class UploadedFileStorage(Protocol):
    """Store uploaded workbook files."""

    def save(self, *, file: BinaryIO, original_filename: str, job_id: str) -> str:
        """Save an uploaded file and return the stored filename."""
        ...

    def path_for(self, stored_filename: str) -> Path:
        """Return the absolute path for a stored file."""
        ...

    def delete_upload(self, stored_filename: str) -> None:
        """Delete an uploaded file if it exists."""
        ...


class JobExecutor(Protocol):
    """Protocol for asynchronous background job execution."""

    def submit_job(self, job_id: str) -> None:
        """Submit a job for background processing."""
        ...
