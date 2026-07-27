from app.core.errors import JobNotFoundError
from app.domain.jobs.models import CreateJob, JobStatus
from app.infrastructure.persistence.sqlite_jobs import SQLiteJobRepository


def test_sqlite_repository_creates_and_retrieves_job(tmp_path) -> None:
    repository = SQLiteJobRepository(tmp_path / "tradeflow.sqlite")

    created = repository.create_job(
        CreateJob(
            job_id="job-1",
            template_id="indian_rice_exports",
            original_filename="input.xlsx",
            stored_filename="job-1.xlsx",
        )
    )
    retrieved = repository.get_job("job-1")

    assert created == retrieved
    assert retrieved.status == JobStatus.UPLOADED
    assert retrieved.created_at == retrieved.updated_at


def test_sqlite_repository_missing_job_raises_not_found(tmp_path) -> None:
    repository = SQLiteJobRepository(tmp_path / "tradeflow.sqlite")

    try:
        repository.get_job("missing-job")
    except JobNotFoundError as exc:
        assert exc.details == {"job_id": "missing-job"}
    else:
        raise AssertionError("Expected JobNotFoundError")

