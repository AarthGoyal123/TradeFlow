"""Job domain models."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class JobStatus(StrEnum):
    """Supported processing job statuses."""

    UPLOADED = "uploaded"
    QUEUED = "queued"
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
    user_id: str | None = None
    tenant_id: str | None = None

    def transition_to(self, new_status: JobStatus, timestamp: datetime) -> "Job":
        """Return a new Job instance with the updated status if the transition is valid."""
        from app.core.errors import InvalidStateTransitionError

        valid_transitions = {
            JobStatus.UPLOADED: {JobStatus.QUEUED, JobStatus.PROCESSING, JobStatus.FAILED},
            JobStatus.QUEUED: {JobStatus.PROCESSING, JobStatus.FAILED},
            JobStatus.PROCESSING: {JobStatus.COMPLETED, JobStatus.FAILED},
            JobStatus.COMPLETED: set(),  # Terminal state
            JobStatus.FAILED: {JobStatus.QUEUED},  # Allow retry
        }

        if new_status not in valid_transitions[self.status]:
            raise InvalidStateTransitionError(
                f"Cannot transition job {self.job_id} from {self.status} to {new_status}"
            )

        return Job(
            job_id=self.job_id,
            template_id=self.template_id,
            original_filename=self.original_filename,
            stored_filename=self.stored_filename,
            status=new_status,
            created_at=self.created_at,
            updated_at=timestamp,
            user_id=self.user_id,
            tenant_id=self.tenant_id,
        )


@dataclass(frozen=True, slots=True)
class CreateJob:
    """Data required to create a job."""

    job_id: str
    template_id: str
    original_filename: str
    stored_filename: str
    user_id: str | None = None
    tenant_id: str | None = None
    status: JobStatus = JobStatus.UPLOADED
