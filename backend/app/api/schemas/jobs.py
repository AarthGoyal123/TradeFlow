"""Job API schemas."""

from datetime import datetime

from pydantic import BaseModel

from app.domain.jobs.models import JobStatus


class JobUploadResponse(BaseModel):
    """Response returned when a file upload is accepted."""

    job_id: str
    status: JobStatus
    template_id: str
    filename: str


class JobDetailsResponse(BaseModel):
    """Persisted job metadata returned by the API."""

    job_id: str
    template_id: str
    original_filename: str
    stored_filename: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime

