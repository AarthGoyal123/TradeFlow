"""Local filesystem storage for uploaded workbooks."""

from pathlib import Path
from typing import BinaryIO

from app.core.errors import StorageError, UploadValidationError


class LocalUploadedFileStorage:
    """Store uploaded files in a local directory."""

    def __init__(self, upload_dir: Path, max_upload_size_mb: int) -> None:
        self._upload_dir = upload_dir
        self._max_upload_size_bytes = max_upload_size_mb * 1024 * 1024

    def save(self, *, file: BinaryIO, original_filename: str, job_id: str) -> str:
        """Save an uploaded file and return the stored filename."""
        extension = Path(original_filename).suffix.lower()
        stored_filename = f"{job_id}{extension}"
        self._upload_dir.mkdir(parents=True, exist_ok=True)
        target_path = self.path_for(stored_filename)
        if target_path.exists():
            raise StorageError(
                "Stored upload filename already exists",
                details={"stored_filename": stored_filename},
            )

        total_bytes = 0
        try:
            with target_path.open("xb") as output:
                while chunk := file.read(1024 * 1024):
                    total_bytes += len(chunk)
                    if total_bytes > self._max_upload_size_bytes:
                        raise UploadValidationError(
                            "Uploaded file exceeds the configured maximum size",
                            details={"max_upload_size_bytes": self._max_upload_size_bytes},
                        )
                    output.write(chunk)
        except Exception:
            if target_path.exists():
                target_path.unlink()
            raise
        return stored_filename

    def path_for(self, stored_filename: str) -> Path:
        """Return the absolute path for a stored file."""
        return (self._upload_dir / stored_filename).resolve()

    def delete_upload(self, stored_filename: str) -> None:
        """Delete an uploaded file if it exists."""
        target_path = self.path_for(stored_filename)
        if target_path.exists():
            try:
                target_path.unlink()
            except OSError:
                pass
