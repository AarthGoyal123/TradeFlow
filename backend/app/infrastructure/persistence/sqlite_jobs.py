"""SQLite job repository."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from sqlite3 import Connection

from app.core.errors import JobNotFoundError, StorageError
from app.domain.jobs.models import CreateJob, Job, JobStatus
from app.domain.outputs.models import OutputArtifact, OutputType, ProcessingSummary


class SQLiteJobRepository:
    """Persist jobs, processing summaries, and output metadata in SQLite."""

    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path
        self._initialize()

    def create_job(self, job: CreateJob) -> Job:
        """Create a persisted job."""
        now = datetime.now(UTC)
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT INTO jobs (
                        job_id,
                        template_id,
                        original_filename,
                        stored_filename,
                        status,
                        created_at,
                        updated_at,
                        user_id,
                        tenant_id
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job.job_id,
                        job.template_id,
                        job.original_filename,
                        job.stored_filename,
                        job.status.value,
                        now.isoformat(),
                        now.isoformat(),
                        job.user_id,
                        job.tenant_id,
                    ),
                )
        except sqlite3.Error as exc:
            raise StorageError(
                "Failed to create job",
                details={"job_id": job.job_id},
            ) from exc
        return self.get_job(job.job_id)

    def get_job(self, job_id: str) -> Job:
        """Return one job by identifier."""
        try:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT
                        job_id,
                        template_id,
                        original_filename,
                        stored_filename,
                        status,
                        created_at,
                        updated_at,
                        user_id,
                        tenant_id
                    FROM jobs
                    WHERE job_id = ?
                    """,
                    (job_id,),
                ).fetchone()
        except sqlite3.Error as exc:
            raise StorageError(
                "Failed to retrieve job",
                details={"job_id": job_id},
            ) from exc

        if row is None:
            raise JobNotFoundError("Job not found", details={"job_id": job_id})
        return self._row_to_job(row)

    def update_status(self, job_id: str, status: JobStatus) -> Job:
        """Update job status ensuring valid transitions."""
        now = datetime.now(UTC)
        try:
            with self._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM jobs WHERE job_id = ?", (job_id,)
                ).fetchone()
                
                if row is None:
                    raise JobNotFoundError("Job not found", details={"job_id": job_id})
                    
                job = self._row_to_job(row)
                job = job.transition_to(status, now)

                connection.execute(
                    """
                    UPDATE jobs
                    SET status = ?, updated_at = ?
                    WHERE job_id = ?
                    """,
                    (job.status.value, job.updated_at.isoformat(), job_id),
                )
        except sqlite3.Error as exc:
            raise StorageError(
                "Failed to update job status",
                details={"job_id": job_id, "status": status.value},
            ) from exc
        return job

    def save_summary(self, summary: ProcessingSummary) -> ProcessingSummary:
        """Persist a processing summary and its outputs."""
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO processing_reports (
                        job_id,
                        template_id,
                        total_rows,
                        clean_rows,
                        removed_rows,
                        needs_review_rows,
                        rule_matches,
                        validation_findings,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        summary.job_id,
                        summary.template_id,
                        summary.total_rows,
                        summary.clean_rows,
                        summary.removed_rows,
                        summary.needs_review_rows,
                        summary.rule_matches,
                        summary.validation_findings,
                        datetime.now(UTC).isoformat(),
                    ),
                )
                connection.execute(
                    "DELETE FROM processing_outputs WHERE job_id = ?",
                    (summary.job_id,),
                )
                connection.executemany(
                    """
                    INSERT INTO processing_outputs (
                        job_id,
                        output_type,
                        filename,
                        path
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    [
                        (
                            summary.job_id,
                            artifact.output_type.value,
                            artifact.filename,
                            str(artifact.path),
                        )
                        for artifact in summary.outputs
                    ],
                )
        except sqlite3.Error as exc:
            raise StorageError(
                "Failed to save processing summary",
                details={"job_id": summary.job_id},
            ) from exc
        return self.get_summary(summary.job_id)

    def get_summary(self, job_id: str) -> ProcessingSummary:
        """Return a processing summary by job id."""
        try:
            with self._connect() as connection:
                report = connection.execute(
                    """
                    SELECT
                        job_id,
                        template_id,
                        total_rows,
                        clean_rows,
                        removed_rows,
                        needs_review_rows,
                        rule_matches,
                        validation_findings
                    FROM processing_reports
                    WHERE job_id = ?
                    """,
                    (job_id,),
                ).fetchone()
                output_rows = connection.execute(
                    """
                    SELECT output_type, filename, path
                    FROM processing_outputs
                    WHERE job_id = ?
                    ORDER BY output_type
                    """,
                    (job_id,),
                ).fetchall()
        except sqlite3.Error as exc:
            raise StorageError(
                "Failed to retrieve processing summary",
                details={"job_id": job_id},
            ) from exc
        if report is None:
            raise StorageError("Processing report not found", details={"job_id": job_id})
        outputs = tuple(
            OutputArtifact(
                output_type=OutputType(row["output_type"]),
                filename=row["filename"],
                path=Path(row["path"]),
            )
            for row in output_rows
        )
        return ProcessingSummary(
            job_id=report["job_id"],
            template_id=report["template_id"],
            total_rows=report["total_rows"],
            clean_rows=report["clean_rows"],
            removed_rows=report["removed_rows"],
            needs_review_rows=report["needs_review_rows"],
            rule_matches=report["rule_matches"],
            validation_findings=report["validation_findings"],
            outputs=outputs,
        )

    def _initialize(self) -> None:
        self._database_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with self._connect() as connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS jobs (
                        job_id TEXT PRIMARY KEY,
                        template_id TEXT NOT NULL,
                        original_filename TEXT NOT NULL,
                        stored_filename TEXT NOT NULL UNIQUE,
                        status TEXT NOT NULL CHECK (
                            status IN ('uploaded', 'processing', 'completed', 'failed')
                        ),
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        user_id TEXT,
                        tenant_id TEXT
                    )
                    """
                )
                
                # Non-destructive migration for existing tables
                try:
                    connection.execute("ALTER TABLE jobs ADD COLUMN user_id TEXT")
                except sqlite3.OperationalError:
                    pass
                try:
                    connection.execute("ALTER TABLE jobs ADD COLUMN tenant_id TEXT")
                except sqlite3.OperationalError:
                    pass

                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS processing_reports (
                        job_id TEXT PRIMARY KEY,
                        template_id TEXT NOT NULL,
                        total_rows INTEGER NOT NULL,
                        clean_rows INTEGER NOT NULL,
                        removed_rows INTEGER NOT NULL,
                        needs_review_rows INTEGER NOT NULL,
                        rule_matches INTEGER NOT NULL,
                        validation_findings INTEGER NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS processing_outputs (
                        job_id TEXT NOT NULL,
                        output_type TEXT NOT NULL,
                        filename TEXT NOT NULL,
                        path TEXT NOT NULL,
                        PRIMARY KEY (job_id, output_type)
                    )
                    """
                )
        except sqlite3.Error as exc:
            raise StorageError("Failed to initialize job database") from exc

    def _connect(self) -> Connection:
        connection = sqlite3.connect(self._database_path)
        connection.row_factory = sqlite3.Row
        return connection

    @staticmethod
    def _row_to_job(row: sqlite3.Row) -> Job:
        keys = row.keys()
        return Job(
            job_id=row["job_id"],
            template_id=row["template_id"],
            original_filename=row["original_filename"],
            stored_filename=row["stored_filename"],
            status=JobStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            user_id=row["user_id"] if "user_id" in keys else None,
            tenant_id=row["tenant_id"] if "tenant_id" in keys else None,
        )
