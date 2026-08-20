"""S3-compatible storage adapters."""

import os
from pathlib import Path
from typing import Any, BinaryIO

import boto3
from botocore.exceptions import ClientError

from app.core.errors import StorageError
from app.domain.jobs.ports import UploadedFileStorage
from app.domain.outputs.models import OutputArtifact, OutputType
from app.domain.outputs.ports import OutputStorage


class S3OutputStorage(OutputStorage):
    """S3-compatible implementation for output artifact storage."""

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        region: str = "us-east-1",
    ) -> None:
        """Initialize S3 client."""
        self._bucket_name = bucket_name
        self._s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

    def save_output(
        self, job_id: str, output_type: OutputType, file_obj: BinaryIO
    ) -> OutputArtifact:
        """Save a generated output file to S3."""
        filename = f"{output_type.value.capitalize()}.xlsx"
        object_key = f"outputs/{job_id}/{filename}"

        try:
            self._s3.upload_fileobj(
                file_obj,
                self._bucket_name,
                object_key,
                ExtraArgs={
                    "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # noqa: E501
                },
            )
        except ClientError as exc:
            raise StorageError(
                "Failed to save output to S3",
                details={"job_id": job_id, "output_type": output_type.value},
            ) from exc

        return OutputArtifact(
            output_type=output_type,
            filename=filename,
            path=Path(object_key),  # The abstract path is the object key
        )

    def get_output(self, *, job_id: str, output_type: OutputType) -> BinaryIO:  # type: ignore
        """Retrieve an output file from S3."""
        import tempfile

        filename = f"{output_type.value.capitalize()}.xlsx"
        object_key = f"outputs/{job_id}/{filename}"

        try:
            # We must return a readable file object. We download to a SpooledTemporaryFile.
            tmp: Any = tempfile.SpooledTemporaryFile(max_size=10_000_000, mode="w+b")
            self._s3.download_fileobj(self._bucket_name, object_key, tmp)
            tmp.seek(0)
            return tmp  # type: ignore
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code == "404" or error_code == "NoSuchKey":
                raise StorageError(
                    "Output file not found in S3",
                    details={"job_id": job_id, "output_type": output_type.value},
                ) from exc
            raise StorageError(
                "Failed to retrieve output from S3",
                details={"job_id": job_id, "output_type": output_type.value},
            ) from exc

    def delete_job_outputs(self, job_id: str) -> None:
        """Delete all outputs for a given job if they exist."""
        prefix = f"outputs/{job_id}/"
        try:
            paginator = self._s3.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self._bucket_name, Prefix=prefix)

            for page in pages:
                if "Contents" in page:
                    objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
                    self._s3.delete_objects(
                        Bucket=self._bucket_name, Delete={"Objects": objects, "Quiet": True}
                    )
        except ClientError:
            pass


class S3UploadedFileStorage(UploadedFileStorage):
    def path_for(self, stored_filename: str) -> Path:
        return Path()

    def save(self, *, file: BinaryIO, original_filename: str, job_id: str) -> str:
        return str(self.save_upload(job_id, original_filename, file))

    """S3-compatible implementation for uploaded workbook storage."""

    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        max_size_mb: int = 50,
        allowed_extensions: tuple[str, ...] = (".xlsx", ".xls"),
        region: str = "us-east-1",
    ) -> None:
        """Initialize S3 client."""
        self._bucket_name = bucket_name
        self._max_size_bytes = max_size_mb * 1024 * 1024
        self._allowed_extensions = allowed_extensions
        self._s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region,
        )

    def save_upload(self, job_id: str, original_filename: str, file_obj: BinaryIO) -> Path:
        """Save an uploaded workbook to S3."""
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
            self._s3.upload_fileobj(
                file_obj,
                self._bucket_name,
                object_key,
                ExtraArgs={
                    "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"  # noqa: E501
                },
            )
        except ClientError as exc:
            raise StorageError(
                "Failed to save upload to S3",
                details={"job_id": job_id},
            ) from exc

        # Return the object key as a Path so that Celery gets a valid string identifier
        return Path(object_key)

    def get_upload(self, stored_path: Path) -> BinaryIO:
        """Retrieve an uploaded workbook from S3."""
        import tempfile

        object_key = str(stored_path).replace("\\", "/")  # Ensure forward slashes for S3

        try:
            tmp: Any = tempfile.SpooledTemporaryFile(max_size=50_000_000, mode="w+b")
            self._s3.download_fileobj(self._bucket_name, object_key, tmp)
            tmp.seek(0)
            return tmp  # type: ignore
        except ClientError as exc:
            error_code = exc.response.get("Error", {}).get("Code", "")
            if error_code == "404" or error_code == "NoSuchKey":
                raise StorageError(
                    "Uploaded file not found in S3",
                    details={"path": str(stored_path)},
                ) from exc
            raise StorageError(
                "Failed to retrieve upload from S3",
                details={"path": str(stored_path)},
            ) from exc

    def delete_upload(self, stored_filename: str) -> None:
        """Delete an uploaded file if it exists."""
        object_key = f"uploads/{stored_filename.split('.')[0]}/{stored_filename}"
        try:
            self._s3.delete_object(Bucket=self._bucket_name, Key=object_key)
        except ClientError:
            pass
