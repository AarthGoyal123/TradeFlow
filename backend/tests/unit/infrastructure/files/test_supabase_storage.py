from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.errors import StorageError
from app.infrastructure.files.supabase_storage import SupabaseUploadedFileStorage


@pytest.fixture
def mock_settings():
    with patch("app.core.settings.get_settings") as mock_get_settings:
        settings = MagicMock()
        settings.resolved_upload_dir = Path("mock_uploads")
        mock_get_settings.return_value = settings
        yield settings


@pytest.fixture
def mock_supabase_client():
    with patch("app.infrastructure.files.supabase_storage.create_client") as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        yield mock_client


@pytest.fixture
def storage(mock_supabase_client):
    return SupabaseUploadedFileStorage(
        supabase_url="http://mock",
        supabase_key="mock_key",
        bucket_name="test-bucket",
    )


def test_path_for_downloads_and_returns_xlsx(
    storage, mock_settings, mock_supabase_client, tmp_path
):
    import openpyxl

    # Create a real, valid excel file in memory to mock download bytes
    wb = openpyxl.Workbook()
    wb.active["A1"] = "Test"
    from io import BytesIO

    buf = BytesIO()
    wb.save(buf)
    mock_bytes = buf.getvalue()

    # Setup
    mock_settings.resolved_upload_dir = tmp_path
    stored_filename = "uploads/123/123.xlsx"
    mock_supabase_client.storage.from_().download.return_value = mock_bytes

    # Execution
    local_path = storage.path_for(stored_filename)

    # Verification
    assert local_path.exists()
    assert local_path.suffix == ".xlsx"
    assert local_path.name == "123.xlsx"
    assert local_path.read_bytes() == mock_bytes
    mock_supabase_client.storage.from_().download.assert_called_once_with("uploads/123/123.xlsx")

    # Verify OpenPyXL can open the returned file
    opened_wb = openpyxl.load_workbook(local_path)
    assert opened_wb.active["A1"].value == "Test"


def test_path_for_does_not_download_if_already_exists(
    storage, mock_settings, mock_supabase_client, tmp_path
):
    # Setup
    mock_settings.resolved_upload_dir = tmp_path
    stored_filename = "uploads/123/123.xlsx"
    local_path = tmp_path / "123.xlsx"
    local_path.write_bytes(b"existing bytes")

    # Execution
    returned_path = storage.path_for(stored_filename)

    # Verification
    assert returned_path == local_path
    assert returned_path.read_bytes() == b"existing bytes"
    mock_supabase_client.storage.from_().download.assert_not_called()


def test_path_for_raises_storage_error_on_missing_file_and_cleans_tmp(
    storage, mock_settings, mock_supabase_client, tmp_path
):
    # Setup
    mock_settings.resolved_upload_dir = tmp_path
    stored_filename = "uploads/123/123.xlsx"

    # Mock download to raise an exception
    mock_supabase_client.storage.from_().download.side_effect = Exception("Not found")

    # Execution
    with pytest.raises(StorageError) as exc_info:
        storage.path_for(stored_filename)

    # Verification
    assert "Failed to download upload" in str(exc_info.value)

    # Verify no tmp files remain
    files_in_dir = list(tmp_path.glob("*"))
    assert len(files_in_dir) == 0


def test_delete_upload_removes_both_local_and_remote(
    storage, mock_settings, mock_supabase_client, tmp_path
):
    # Setup
    mock_settings.resolved_upload_dir = tmp_path
    stored_filename = "uploads/123/123.xlsx"

    # Create local cached file
    local_path = tmp_path / "123.xlsx"
    local_path.write_bytes(b"cached")
    assert local_path.exists()

    # Execution
    storage.delete_upload(stored_filename)

    # Verification
    assert not local_path.exists()
    mock_supabase_client.storage.from_().remove.assert_called_once_with(["uploads/123/123.xlsx"])


def test_delete_upload_succeeds_even_if_local_file_missing(
    storage, mock_settings, mock_supabase_client, tmp_path
):
    # Setup
    mock_settings.resolved_upload_dir = tmp_path
    stored_filename = "uploads/123/123.xlsx"
    local_path = tmp_path / "123.xlsx"
    assert not local_path.exists()

    # Execution
    storage.delete_upload(stored_filename)

    # Verification
    mock_supabase_client.storage.from_().remove.assert_called_once_with(["uploads/123/123.xlsx"])
