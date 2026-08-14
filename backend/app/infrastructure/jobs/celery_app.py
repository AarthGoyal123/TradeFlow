"""Celery application and task definitions."""

import logging

from celery import Celery

from app.core.settings import get_settings
from app.domain.jobs.models import JobStatus

logger = logging.getLogger(__name__)

settings = get_settings()

celery_app = Celery(
    "tradeflow",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

@celery_app.task(bind=True, max_retries=3)
def process_job_task(self, job_id: str) -> dict:
    """Execute the processing pipeline for a job."""
    from app.api.dependencies import get_job_service, get_processing_service
    from app.core.errors import WorkbookValidationError
    
    logger.info(f"Celery task started for job_id={job_id}")
    
    job_service = get_job_service()
    job = job_service.get_job(job_id)
    
    # Idempotency check
    if job.status == JobStatus.COMPLETED:
        logger.info(f"Job {job_id} already completed, skipping.")
        return {"status": "completed", "job_id": job_id}
        
    try:
        processing_service = get_processing_service()
        result = processing_service.process_job(job_id)
        
        # In case process_job handles errors and returns them instead of raising
        if result.errors:
            # Job is technically FAILED business-wise
            job_service.job_repository.update_status(job_id, JobStatus.FAILED)
            return {"status": "failed", "job_id": job_id, "errors": [e.message for e in result.errors]}
            
        return {"status": "completed", "job_id": job_id}
        
    except WorkbookValidationError as e:
        # Permanent validation failure
        logger.error(f"Validation error for job {job_id}: {str(e)}")
        job_service.job_repository.update_status(job_id, JobStatus.FAILED)
        return {"status": "failed", "job_id": job_id, "error": str(e)}
        
    except Exception as e:
        logger.exception(f"Unexpected error processing job {job_id}")
        job_service.job_repository.update_status(job_id, JobStatus.FAILED)
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
