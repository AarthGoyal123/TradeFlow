"""Local filesystem storage for generated output workbooks."""

from pathlib import Path
from typing import BinaryIO

from app.core.errors import StorageError
from app.domain.outputs.models import OutputArtifact, OutputType


class LocalOutputStorage:
    """Store generated output workbooks in a per-job directory."""

    def __init__(self, output_dir: Path) -> None:
        self._output_dir = output_dir

    def save_output(
        self, job_id: str, output_type: OutputType, file_obj: "BinaryIO"
    ) -> OutputArtifact:
        """Save a generated output file from a file-like object."""
        filenames = {
            OutputType.CLEAN_DATA: "Clean_Data.xlsx",
            OutputType.REMOVED_ROWS: "Removed_Rows.xlsx",
            OutputType.NEEDS_REVIEW: "Needs_Review.xlsx",
            OutputType.PROCESSING_REPORT: "Processing_Report.xlsx",
        }
        filename = filenames[output_type]

        job_dir = self._output_dir / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        path = (job_dir / filename).resolve()
        if not str(path).startswith(str(job_dir.resolve())):
            raise StorageError("Output path escaped job output directory")

        path.write_bytes(file_obj.read())
        return OutputArtifact(output_type=output_type, filename=filename, path=path)

    def get_output(
        self, *, job_id: str, output_type: OutputType
    ) -> tuple[OutputArtifact, BinaryIO]:
        """Return output metadata and a readable binary stream."""
        filenames = {
            OutputType.CLEAN_DATA: "Clean_Data.xlsx",
            OutputType.REMOVED_ROWS: "Removed_Rows.xlsx",
            OutputType.NEEDS_REVIEW: "Needs_Review.xlsx",
            OutputType.PROCESSING_REPORT: "Processing_Report.xlsx",
        }
        filename = filenames[output_type]
        path = (self._output_dir / job_id / filename).resolve()

        # Prevent path traversal via job_id
        if not str(path).startswith(str(self._output_dir.resolve())):
            raise StorageError("Invalid output path")

        if not path.exists():
            raise StorageError(
                "Output file not found",
                details={"job_id": job_id, "output_type": output_type.value},
            )

        artifact = OutputArtifact(output_type=output_type, filename=filename, path=path)
        return artifact, path.open("rb")

    def delete_job_outputs(self, job_id: str) -> None:
        """Delete all outputs for a given job if they exist."""
        import shutil

        job_dir = (self._output_dir / job_id).resolve()
        if not str(job_dir).startswith(str(self._output_dir.resolve())):
            return
        if job_dir.exists() and job_dir.is_dir():
            shutil.rmtree(job_dir, ignore_errors=True)
