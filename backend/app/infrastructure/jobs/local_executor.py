from app.application.processing.service import ProcessingService
from app.domain.jobs.ports import JobExecutor


class SynchronousJobExecutor(JobExecutor):
    """Executes jobs synchronously in the current thread."""

    def __init__(self, processing_service: ProcessingService) -> None:
        self._processing_service = processing_service

    def submit_job(self, job_id: str) -> None:
        self._processing_service.process_job(job_id)
