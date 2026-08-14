"""Tests for S3 storage adapters."""

import io
from pathlib import Path

import pytest
from botocore.exceptions import ClientError

from app.core.errors import StorageError
from app.domain.outputs.models import OutputType
from app.infrastructure.files.s3_storage import S3OutputStorage, S3UploadedFileStorage


@pytest.fixture
def mock_s3_client(mocker):
    """Mock boto3 client."""
    mock_boto3 = mocker.patch("app.infrastructure.files.s3_storage.boto3")
    mock_client = mocker.MagicMock()
    mock_boto3.client.return_value = mock_client
    return mock_client


def test_s3_output_storage_save(mock_s3_client):
    """Test saving output to S3."""
    storage = S3OutputStorage(
        endpoint_url="http://localhost:9000",
        access_key="test",
        secret_key="test",
        bucket_name="test-bucket",
    )

    file_obj = io.BytesIO(b"test data")
    result = storage.save_output("job-123", OutputType.CLEAN_DATA, file_obj)

    assert result.filename == "Clean_data.xlsx"
    assert result.path.as_posix() == "outputs/job-123/Clean_data.xlsx"

    mock_s3_client.upload_fileobj.assert_called_once_with(
        file_obj,
        "test-bucket",
        "outputs/job-123/Clean_data.xlsx",
        ExtraArgs={
            "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
    )


def test_s3_output_storage_save_error(mock_s3_client):
    """Test saving output error handling."""
    storage = S3OutputStorage("http://localhost", "a", "s", "bucket")

    mock_s3_client.upload_fileobj.side_effect = ClientError(
        {"Error": {"Code": "500", "Message": "Internal Error"}}, "PutObject"
    )

    with pytest.raises(StorageError, match="Failed to save output to S3"):
        storage.save_output("job-1", OutputType.REMOVED_ROWS, io.BytesIO(b"data"))


def test_s3_output_storage_get(mock_s3_client, mocker):
    """Test retrieving output from S3."""
    storage = S3OutputStorage("http://localhost", "a", "s", "bucket")

    def mock_download(bucket, key, fileobj):
        fileobj.write(b"retrieved data")

    mock_s3_client.download_fileobj.side_effect = mock_download

    result = storage.get_output(job_id="job-123", output_type=OutputType.NEEDS_REVIEW)
    assert result.read() == b"retrieved data"

    mock_s3_client.download_fileobj.assert_called_once()
    args, _ = mock_s3_client.download_fileobj.call_args
    assert args[0] == "bucket"
    assert args[1] == "outputs/job-123/Needs_review.xlsx"


def test_s3_output_storage_get_not_found(mock_s3_client):
    """Test retrieving non-existent output."""
    storage = S3OutputStorage("http://localhost", "a", "s", "bucket")

    mock_s3_client.download_fileobj.side_effect = ClientError(
        {"Error": {"Code": "404", "Message": "Not Found"}}, "GetObject"
    )

    with pytest.raises(StorageError, match="Output file not found in S3"):
        storage.get_output(job_id="job-1", output_type=OutputType.CLEAN_DATA)


def test_s3_uploaded_storage_save(mock_s3_client):
    """Test saving uploaded file to S3."""
    storage = S3UploadedFileStorage("http://localhost", "a", "s", "bucket")

    file_obj = io.BytesIO(b"upload data")
    path = storage.save_upload("job-456", "test.xlsx", file_obj)

    assert path.as_posix() == "uploads/job-456/job-456.xlsx"

    mock_s3_client.upload_fileobj.assert_called_once_with(
        file_obj,
        "bucket",
        "uploads/job-456/job-456.xlsx",
        ExtraArgs={
            "ContentType": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        },
    )


def test_s3_uploaded_storage_save_invalid_ext(mock_s3_client):
    """Test saving invalid extension."""
    storage = S3UploadedFileStorage("http://localhost", "a", "s", "bucket")

    with pytest.raises(StorageError, match="Invalid file extension"):
        storage.save_upload("job-1", "test.txt", io.BytesIO(b"data"))


def test_s3_uploaded_storage_save_too_large(mock_s3_client):
    """Test saving file that exceeds limit."""
    storage = S3UploadedFileStorage("http://localhost", "a", "s", "bucket", max_size_mb=1)

    file_obj = io.BytesIO(b"a" * (2 * 1024 * 1024))  # 2MB
    with pytest.raises(StorageError, match="File exceeds size limit"):
        storage.save_upload("job-1", "test.xlsx", file_obj)


def test_s3_uploaded_storage_get(mock_s3_client):
    """Test retrieving upload from S3."""
    storage = S3UploadedFileStorage("http://localhost", "a", "s", "bucket")

    def mock_download(bucket, key, fileobj):
        fileobj.write(b"retrieved upload")

    mock_s3_client.download_fileobj.side_effect = mock_download

    result = storage.get_upload(Path("uploads/job-456/job-456.xlsx"))
    assert result.read() == b"retrieved upload"

    mock_s3_client.download_fileobj.assert_called_once()
    args, _ = mock_s3_client.download_fileobj.call_args
    assert args[0] == "bucket"
    assert args[1] == "uploads/job-456/job-456.xlsx"


def test_s3_uploaded_storage_get_not_found(mock_s3_client):
    """Test retrieving non-existent upload."""
    storage = S3UploadedFileStorage("http://localhost", "a", "s", "bucket")

    mock_s3_client.download_fileobj.side_effect = ClientError(
        {"Error": {"Code": "NoSuchKey", "Message": "Not Found"}}, "GetObject"
    )

    with pytest.raises(StorageError, match="Uploaded file not found in S3"):
        storage.get_upload(Path("uploads/job-1/missing.xlsx"))
