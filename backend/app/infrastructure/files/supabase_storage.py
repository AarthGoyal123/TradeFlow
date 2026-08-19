"""Supabase-compatible storage adapters."""

import os
from pathlib import Path
from typing import Any, BinaryIO

from supabase import Client, create_client

from app.core.errors import StorageError
from app.domain.jobs.ports import UploadedFileStorage
from app.domain.outputs.models import OutputArtifact, OutputType
from app.domain.outputs.ports import OutputStorage


class SupabaseOutputStorage(OutputStorage):
    """Supabase implementation for output artifact storage."""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        bucket_name: str,
    ) -> None:
        """Initialize Supabase client."""
        self._bucket_name = bucket_name
        self._client: Client = create_client(supabase_url, supabase_key)

    def output_path(self, *, job_id: str, output_type: OutputType, filename: str) -> Path:
        return Path()

    def save_output(
        self, job_id: str, output_type: OutputType, file_obj: BinaryIO
    ) -> OutputArtifact:
        """Save a generated output file to Supabase."""
        filename = f"{output_type.value.capitalize()}.xlsx"
        object_key = f"outputs/{job_id}/{filename}"

        try:
            file_obj.seek(0)
            content = file_obj.read()
            self._client.storage.from_(self._bucket_name).upload(
                object_key,
                content,
                file_options={
                    "content-type": (
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                },
            )
        except Exception as exc:
            raise StorageError(
                "Failed to save output to Supabase",
                details={"job_id": job_id, "output_type": output_type.value},
            ) from exc

        return OutputArtifact(
            output_type=output_type,
            filename=filename,
            path=Path(object_key),  # The abstract path is the object key
        )

    def get_output(self, *, job_id: str, output_type: OutputType) -> BinaryIO:  # type: ignore
        """Retrieve an output file from Supabase."""
        import tempfile

        filename = f"{output_type.value.capitalize()}.xlsx"
        object_key = f"outputs/{job_id}/{filename}"

        try:
            res = self._client.storage.from_(self._bucket_name).download(object_key)
            # We must return a readable file object. We download to a SpooledTemporaryFile.
            tmp: Any = tempfile.SpooledTemporaryFile(max_size=10_000_000, mode="w+b")
            tmp.write(res)
            tmp.seek(0)
            return tmp  # type: ignore
        except Exception as exc:
            raise StorageError(
                "Failed to retrieve output from Supabase",
                details={"job_id": job_id, "output_type": output_type.value},
            ) from exc

    def delete_job_outputs(self, job_id: str) -> None:
        """Delete all outputs for a given job if they exist."""
        prefix = f"outputs/{job_id}/"
        try:
            # List files with prefix
            files = self._client.storage.from_(self._bucket_name).list(prefix)
            if files:
                file_paths = [f"{prefix}{f['name']}" for f in files if f.get("name")]
                if file_paths:
                    self._client.storage.from_(self._bucket_name).remove(file_paths)
        except Exception:
            pass


class SupabaseUploadedFileStorage(UploadedFileStorage):
    """Supabase implementation for uploaded workbook storage."""

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        bucket_name: str,
        max_size_mb: int = 50,
        allowed_extensions: tuple[str, ...] = (".xlsx", ".xls"),
    ) -> None:
        """Initialize Supabase client."""
        self._bucket_name = bucket_name
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._allowed_extensions = allowed_extensions
        self._client: Client = create_client(supabase_url, supabase_key)

    def path_for(self, stored_filename: str) -> Path:
        import uuid

        from app.core.settings import get_settings

        object_key = stored_filename.replace("\\", "/")
        local_path = get_settings().resolved_upload_dir / Path(object_key).name

        if local_path.exists():
            return local_path

        local_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = local_path.with_name(f"{local_path.name}.{uuid.uuid4().hex}.tmp")

        try:
            res = self._client.storage.from_(self._bucket_name).download(object_key)
            tmp_path.write_bytes(res)
            tmp_path.replace(local_path)
        except Exception as exc:
            if tmp_path.exists():
                try:
                    tmp_path.unlink()
                except OSError:
                    pass
            from app.core.errors import StorageError

            raise StorageError(
                "Failed to download upload from Supabase",
                details={"path": object_key},
            ) from exc

        return local_path

    def save(self, *, file: BinaryIO, original_filename: str, job_id: str) -> str:
        return str(self.save_upload(job_id, original_filename, file))

    def save_upload(self, job_id: str, original_filename: str, file_obj: BinaryIO) -> Path:
        """Save an uploaded workbook to Supabase."""
        ext = Path(original_filename).suffix.lower()
        if ext not in self._allowed_extensions:
            raise StorageError("Invalid file extension", details={"extension": ext})

        file_obj.seek(0, os.SEEK_END)
        size = file_obj.tell()
        if size > self._max_size_bytes:
            raise StorageError("File exceeds size limit", details={"size": size})
        file_obj.seek(0)

        # Deterministic, safe object key
        stored_filename = f"{job_id}{ext}"
        object_key = f"uploads/{job_id}/{stored_filename}"

        try:
            content = file_obj.read()
            self._client.storage.from_(self._bucket_name).upload(
                object_key,
                content,
                file_options={
                    "content-type": (
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                },
            )
        except Exception as exc:
            raise StorageError(
                "Failed to save upload to Supabase",
                details={"job_id": job_id},
            ) from exc

        # Return the object key as a Path so that Celery gets a valid string identifier
        return Path(object_key)

    def get_upload(self, stored_path: Path) -> BinaryIO:
        """Retrieve an uploaded workbook from Supabase."""
        import tempfile

        object_key = str(stored_path).replace("\\", "/")  # Ensure forward slashes for S3

        try:
            res = self._client.storage.from_(self._bucket_name).download(object_key)
            tmp: Any = tempfile.SpooledTemporaryFile(max_size=50_000_000, mode="w+b")
            tmp.write(res)
            tmp.seek(0)
            return tmp  # type: ignore
        except Exception as exc:
            raise StorageError(
                "Failed to retrieve upload from Supabase",
                details={"path": str(stored_path)},
            ) from exc

    def delete_upload(self, stored_filename: str) -> None:
        """Delete an uploaded file if it exists."""
        object_key = stored_filename.replace("\\", "/")

        from app.core.settings import get_settings

        local_path = get_settings().resolved_upload_dir / Path(object_key).name
        try:
            if local_path.exists():
                local_path.unlink()
        except OSError:
            pass

        try:
            self._client.storage.from_(self._bucket_name).remove([object_key])
        except Exception:
            pass
