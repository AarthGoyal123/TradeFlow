"""Job domain models."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class JobStatus(StrEnum):
    """Supported processing job statuses."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class Job:
    """Persisted upload or processing job."""

    job_id: str
    template_id: str
    original_filename: str
    stored_filename: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class CreateJob:
    """Data required to create a job."""

    job_id: str
    template_id: str
    original_filename: str
    stored_filename: str
    status: JobStatus = JobStatus.UPLOADED

