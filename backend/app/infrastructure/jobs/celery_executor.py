"""Celery implementation of the JobExecutor port."""

import logging

from app.domain.jobs.ports import JobExecutor
from app.infrastructure.jobs.celery_app import process_job_task

logger = logging.getLogger(__name__)


class CeleryJobExecutor(JobExecutor):
    """Executes jobs asynchronously using Celery workers."""

    def submit_job(self, job_id: str) -> None:
        """Enqueue the job for asynchronous processing."""
        from app.api.dependencies import get_job_service
        from app.domain.jobs.models import JobStatus

        logger.info(f"Submitting job {job_id} to celery")

        # Enqueue the background task
        task = process_job_task.delay(job_id)

        # Update job status to queued
        job_service = get_job_service()
        job_service._job_repository.update_status(job_id, JobStatus.QUEUED)

        logger.info(f"Job {job_id} successfully queued with task_id {task.id}")
