"""Job API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.api.dependencies import get_job_service
from app.api.schemas.jobs import JobDetailsResponse, JobUploadResponse
from app.application.jobs.service import JobService
from app.domain.jobs.models import Job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobUploadResponse)
def create_job(
    template_id: Annotated[str, Form()],
    file: Annotated[UploadFile, File()],
    job_service: Annotated[JobService, Depends(get_job_service)],
) -> JobUploadResponse:
    """Accept an uploaded workbook and create an uploaded job."""
    original_filename = file.filename or ""
    job = job_service.create_uploaded_job(
        template_id=template_id,
        original_filename=original_filename,
        file=file.file,
    )
    return JobUploadResponse(
        job_id=job.job_id,
        status=job.status,
        template_id=job.template_id,
        filename=job.original_filename,
    )


@router.get("/{job_id}", response_model=JobDetailsResponse)
def get_job(
    job_id: str,
    job_service: Annotated[JobService, Depends(get_job_service)],
) -> JobDetailsResponse:
    """Return job metadata and current status."""
    return _to_job_details_response(job_service.get_job(job_id))


def _to_job_details_response(job: Job) -> JobDetailsResponse:
    return JobDetailsResponse(
        job_id=job.job_id,
        template_id=job.template_id,
        original_filename=job.original_filename,
        stored_filename=job.stored_filename,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
    )

