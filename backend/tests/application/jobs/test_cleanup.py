from datetime import UTC, datetime, timedelta
from unittest.mock import Mock

from app.application.jobs.cleanup import CleanupService
from app.domain.jobs.models import Job, JobStatus


def test_cleanup_old_jobs() -> None:
    job_repo = Mock()
    upload_storage = Mock()
    output_storage = Mock()

    service = CleanupService(
        job_repository=job_repo,
        upload_storage=upload_storage,
        output_storage=output_storage,
        retention_days=7,
    )

    now = datetime.now(UTC)
    old_job = Job(
        job_id="job-1",
        template_id="tpl-1",
        original_filename="test.xlsx",
        stored_filename="job-1.xlsx",
        status=JobStatus.COMPLETED,
        created_at=now - timedelta(days=10),
        updated_at=now - timedelta(days=10),
    )

    job_repo.get_terminal_jobs_older_than.return_value = [old_job]

    processed = service.cleanup_old_jobs()

    assert processed == 1
    job_repo.get_terminal_jobs_older_than.assert_called_once()
    args = job_repo.get_terminal_jobs_older_than.call_args[0][0]
    assert isinstance(args, datetime)

    upload_storage.delete_upload.assert_called_once_with("job-1.xlsx")
    output_storage.delete_job_outputs.assert_called_once_with("job-1")

def test_cleanup_handles_storage_errors() -> None:
    job_repo = Mock()
    upload_storage = Mock()
    output_storage = Mock()

    service = CleanupService(
        job_repository=job_repo,
        upload_storage=upload_storage,
        output_storage=output_storage,
        retention_days=7,
    )

    old_job1 = Job(
        job_id="job-1",
        template_id="tpl-1",
        original_filename="test1.xlsx",
        stored_filename="job-1.xlsx",
        status=JobStatus.COMPLETED,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    old_job2 = Job(
        job_id="job-2",
        template_id="tpl-1",
        original_filename="test2.xlsx",
        stored_filename="job-2.xlsx",
        status=JobStatus.FAILED,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    job_repo.get_terminal_jobs_older_than.return_value = [old_job1, old_job2]
    
    # First deletion fails
    upload_storage.delete_upload.side_effect = [Exception("Storage error"), None]

    processed = service.cleanup_old_jobs()

    assert processed == 1 # Second job should succeed
    assert upload_storage.delete_upload.call_count == 2
    assert output_storage.delete_job_outputs.call_count == 1 # Only called for job-2
