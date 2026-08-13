"""SQLAlchemy repositories for data persistence."""

from datetime import UTC, datetime
from typing import Dict, List, Optional
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.core.errors import JobNotFoundError, StorageError
from app.domain.jobs.models import CreateJob, Job, JobStatus
from app.domain.outputs.models import OutputArtifact, OutputType, ProcessingSummary
from app.domain.jobs.ports import JobRepository
from app.domain.outputs.ports import ProcessingReportRepository

from app.infrastructure.database.models import JobModel, JobReportModel, OutputArtifactModel


class SQLAlchemyJobRepository(JobRepository, ProcessingReportRepository):
    """SQLAlchemy implementation of JobRepository and ProcessingReportRepository."""

    def __init__(self, session_factory) -> None:
        """Initialize with a session factory."""
        self._session_factory = session_factory

    def create_job(self, job: CreateJob) -> Job:
        """Create a persisted job."""
        now = datetime.now(UTC)
        try:
            with self._session_factory() as session:
                job_model = JobModel(
                    job_id=job.job_id,
                    template_id=job.template_id,
                    original_filename=job.original_filename,
                    stored_filename=job.stored_filename,
                    status=job.status.value,
                    created_at=now,
                    updated_at=now,
                    user_id=job.user_id,
                    tenant_id=job.tenant_id,
                )
                session.add(job_model)
                session.commit()
        except SQLAlchemyError as exc:
            raise StorageError(
                "Failed to create job",
                details={"job_id": job.job_id},
            ) from exc
        return self.get_job(job.job_id)

    def get_job(self, job_id: str) -> Job:
        """Return one job by identifier."""
        try:
            with self._session_factory() as session:
                stmt = select(JobModel).where(JobModel.job_id == job_id)
                row = session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError as exc:
            raise StorageError(
                "Failed to retrieve job",
                details={"job_id": job_id},
            ) from exc

        if row is None:
            raise JobNotFoundError("Job not found", details={"job_id": job_id})
        return self._model_to_job(row)

    def update_status(self, job_id: str, status: JobStatus) -> Job:
        """Update job status ensuring valid transitions."""
        now = datetime.now(UTC)
        try:
            with self._session_factory() as session:
                stmt = select(JobModel).where(JobModel.job_id == job_id)
                row = session.execute(stmt).scalar_one_or_none()
                
                if row is None:
                    raise JobNotFoundError("Job not found", details={"job_id": job_id})
                
                current_status = JobStatus(row.status)
                # Ensure status transitions are valid
                if status == JobStatus.QUEUED:
                    if current_status not in (JobStatus.UPLOADED, JobStatus.FAILED):
                        raise StorageError("Invalid state transition", details={"from": current_status.value, "to": status.value})
                elif status == JobStatus.PROCESSING:
                    if current_status not in (JobStatus.UPLOADED, JobStatus.QUEUED):
                        raise StorageError("Invalid state transition", details={"from": current_status.value, "to": status.value})
                elif status in (JobStatus.COMPLETED, JobStatus.FAILED):
                    if current_status not in (JobStatus.PROCESSING, JobStatus.QUEUED):
                        raise StorageError("Invalid state transition", details={"from": current_status.value, "to": status.value})

                row.status = status.value
                row.updated_at = now
                session.commit()
                
        except JobNotFoundError:
            raise
        except SQLAlchemyError as exc:
            raise StorageError(
                "Failed to update job status",
                details={"job_id": job_id, "status": status.value},
            ) from exc
        return self.get_job(job_id)

    def save_summary(self, summary: ProcessingSummary) -> ProcessingSummary:
        """Save a processing summary and link generated artifacts."""
        try:
            with self._session_factory() as session:
                # Upsert processing report
                stmt = select(JobReportModel).where(JobReportModel.job_id == summary.job_id)
                report = session.execute(stmt).scalar_one_or_none()
                
                if report is None:
                    report = JobReportModel(
                        job_id=summary.job_id,
                        template_id=summary.template_id,
                    )
                    session.add(report)

                report.total_rows = summary.total_rows
                report.clean_rows = summary.clean_rows
                report.removed_rows = summary.removed_rows
                report.needs_review_rows = summary.needs_review_rows
                report.rule_matches = summary.rule_matches
                report.validation_findings = summary.validation_findings
                
                # Delete existing outputs manually just in case, though cascade="all, delete-orphan" handles some
                for out in report.outputs:
                    session.delete(out)
                report.outputs = []
                
                # Insert outputs
                for artifact in summary.outputs:
                    out_model = OutputArtifactModel(
                        job_id=summary.job_id,
                        output_type=artifact.output_type.value,
                        filename=artifact.filename,
                        path=str(artifact.path),
                    )
                    report.outputs.append(out_model)
                
                session.commit()
                
        except SQLAlchemyError as exc:
            raise StorageError(
                "Failed to save processing summary",
                details={"job_id": summary.job_id},
            ) from exc
        return self.get_summary(summary.job_id)

    def get_summary(self, job_id: str) -> ProcessingSummary:
        """Return a processing summary by job id."""
        try:
            with self._session_factory() as session:
                stmt = select(JobReportModel).where(JobReportModel.job_id == job_id)
                report = session.execute(stmt).scalar_one_or_none()
                
                if report is None:
                    raise StorageError("Processing report not found", details={"job_id": job_id})
                
                outputs = tuple(
                    OutputArtifact(
                        output_type=OutputType(out.output_type),
                        filename=out.filename,
                        path=Path(out.path),
                    )
                    for out in report.outputs
                )
                
                return ProcessingSummary(
                    job_id=report.job_id,
                    template_id=report.template_id,
                    total_rows=report.total_rows,
                    clean_rows=report.clean_rows,
                    removed_rows=report.removed_rows,
                    needs_review_rows=report.needs_review_rows,
                    rule_matches=report.rule_matches,
                    validation_findings=report.validation_findings,
                    outputs=outputs,
                )
                
        except StorageError:
            raise
        except SQLAlchemyError as exc:
            raise StorageError(
                "Failed to retrieve processing summary",
                details={"job_id": job_id},
            ) from exc

    def _model_to_job(self, row: JobModel) -> Job:
        # Pydantic models expect UTC datetime. If DB doesn't store tzinfo, attach it
        created_at = row.created_at.replace(tzinfo=UTC) if row.created_at.tzinfo is None else row.created_at
        updated_at = row.updated_at.replace(tzinfo=UTC) if row.updated_at.tzinfo is None else row.updated_at
        
        return Job(
            job_id=row.job_id,
            template_id=row.template_id,
            original_filename=row.original_filename,
            stored_filename=row.stored_filename,
            status=JobStatus(row.status),
            created_at=created_at,
            updated_at=updated_at,
            user_id=row.user_id,
            tenant_id=row.tenant_id,
        )
