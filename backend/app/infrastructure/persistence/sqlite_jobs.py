"""SQLite job repository."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from sqlite3 import Connection

from app.core.errors import JobNotFoundError, StorageError
from app.domain.jobs.models import CreateJob, Job, JobStatus


class SQLiteJobRepository:
    """Persist jobs in SQLite."""

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
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        job.job_id,
                        job.template_id,
                        job.original_filename,
                        job.stored_filename,
                        job.status.value,
                        now.isoformat(),
                        now.isoformat(),
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
                        updated_at
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
                        updated_at TEXT NOT NULL
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
        return Job(
            job_id=row["job_id"],
            template_id=row["template_id"],
            original_filename=row["original_filename"],
            stored_filename=row["stored_filename"],
            status=JobStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

