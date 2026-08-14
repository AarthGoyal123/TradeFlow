from datetime import UTC, datetime

import pytest

from app.core.errors import InvalidStateTransitionError
from app.domain.jobs.models import Job, JobStatus


def test_job_valid_transitions():
    now = datetime.now(UTC)
    job = Job(
        job_id="1",
        template_id="t1",
        original_filename="a.xlsx",
        stored_filename="a.xlsx",
        status=JobStatus.UPLOADED,
        created_at=now,
        updated_at=now,
    )
    
    # Valid: UPLOADED -> PROCESSING
    new_now = datetime.now(UTC)
    job2 = job.transition_to(JobStatus.PROCESSING, new_now)
    assert job2.status == JobStatus.PROCESSING
    assert job2.updated_at == new_now
    
    # Valid: PROCESSING -> COMPLETED
    job3 = job2.transition_to(JobStatus.COMPLETED, new_now)
    assert job3.status == JobStatus.COMPLETED
    
    # Valid: PROCESSING -> FAILED
    job4 = job2.transition_to(JobStatus.FAILED, new_now)
    assert job4.status == JobStatus.FAILED

def test_job_invalid_transitions():
    now = datetime.now(UTC)
    job = Job(
        job_id="1",
        template_id="t1",
        original_filename="a.xlsx",
        stored_filename="a.xlsx",
        status=JobStatus.COMPLETED,
        created_at=now,
        updated_at=now,
    )
    
    # Invalid: COMPLETED -> PROCESSING
    with pytest.raises(InvalidStateTransitionError):
        job.transition_to(JobStatus.PROCESSING, now)

    # Invalid: FAILED -> COMPLETED
    failed_job = Job(
        job_id="2",
        template_id="t1",
        original_filename="b.xlsx",
        stored_filename="b.xlsx",
        status=JobStatus.FAILED,
        created_at=now,
        updated_at=now,
    )
    with pytest.raises(InvalidStateTransitionError):
        failed_job.transition_to(JobStatus.COMPLETED, now)
        
    # Valid: FAILED -> QUEUED (Retry)
    retried_job = failed_job.transition_to(JobStatus.QUEUED, now)
    assert retried_job.status == JobStatus.QUEUED
