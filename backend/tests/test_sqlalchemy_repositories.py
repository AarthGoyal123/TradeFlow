"""Tests for SQLAlchemy repositories."""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.errors import JobNotFoundError, StorageError
from app.domain.jobs.models import CreateJob, JobStatus
from app.domain.outputs.models import OutputArtifact, OutputType, ProcessingSummary
from app.infrastructure.database.models import Base
from app.infrastructure.database.repositories import SQLAlchemyJobRepository


@pytest.fixture
def session_factory():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def repository(session_factory):
    """Return a SQLAlchemyJobRepository bound to the in-memory DB."""
    return SQLAlchemyJobRepository(session_factory)


def test_create_and_get_job(repository):
    """Test job creation and retrieval."""
    job_cmd = CreateJob(
        job_id="job-123",
        template_id="tpl-456",
        original_filename="test.xlsx",
        stored_filename="stored_test.xlsx",
        status=JobStatus.UPLOADED,
    )

    job = repository.create_job(job_cmd)

    assert job.job_id == "job-123"
    assert job.template_id == "tpl-456"
    assert job.status == JobStatus.UPLOADED

    # Retrieve
    fetched = repository.get_job("job-123")
    assert fetched.job_id == "job-123"


def test_update_status(repository):
    """Test valid and invalid status updates."""
    job_cmd = CreateJob(
        job_id="job-2",
        template_id="tpl-1",
        original_filename="test.xlsx",
        stored_filename="stored2.xlsx",
        status=JobStatus.UPLOADED,
    )
    repository.create_job(job_cmd)

    # Valid transition
    job = repository.update_status("job-2", JobStatus.QUEUED)
    assert job.status == JobStatus.QUEUED

    job = repository.update_status("job-2", JobStatus.PROCESSING)
    assert job.status == JobStatus.PROCESSING

    job = repository.update_status("job-2", JobStatus.COMPLETED)
    assert job.status == JobStatus.COMPLETED

    # Invalid transition
    with pytest.raises(StorageError):
        repository.update_status("job-2", JobStatus.QUEUED)


def test_get_nonexistent_job(repository):
    with pytest.raises(JobNotFoundError):
        repository.get_job("missing-job")


def test_save_and_get_summary(repository):
    """Test processing summary persistence."""
    job_cmd = CreateJob(
        job_id="job-3",
        template_id="tpl-3",
        original_filename="test.xlsx",
        stored_filename="stored3.xlsx",
        status=JobStatus.UPLOADED,
    )
    repository.create_job(job_cmd)

    outputs = (
        OutputArtifact(
            output_type=OutputType.CLEAN_DATA, filename="clean.xlsx", path=Path("/tmp/clean.xlsx")
        ),
    )

    summary = ProcessingSummary(
        job_id="job-3",
        template_id="tpl-3",
        total_rows=10,
        clean_rows=8,
        removed_rows=2,
        needs_review_rows=0,
        rule_matches={"rule1": 2},
        validation_findings=[{"row": 1, "msg": "err"}],
        outputs=outputs,
    )

    saved = repository.save_summary(summary)
    assert saved.job_id == "job-3"
    assert saved.total_rows == 10
    assert len(saved.outputs) == 1

    # Retrieve
    fetched = repository.get_summary("job-3")
    assert fetched.clean_rows == 8
    assert len(fetched.outputs) == 1
    assert fetched.outputs[0].filename == "clean.xlsx"
