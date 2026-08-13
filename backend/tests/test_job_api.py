from pathlib import Path

from fastapi.testclient import TestClient

from app.api.dependencies import get_job_service
from app.application.jobs.service import JobService
from app.infrastructure.files.local_uploads import LocalUploadedFileStorage
from app.infrastructure.persistence.sqlite_jobs import SQLiteJobRepository
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository
from app.main import create_app
from tests.helpers.auth import create_test_user, override_auth


def test_upload_job_saves_file_creates_job_and_allows_retrieval(tmp_path) -> None:
    client, upload_dir = _client_with_temp_job_service(tmp_path)

    response = client.post(
        "/jobs",
        data={"template_id": "indian_rice_exports"},
        files={
            "file": (
                "shipment.xlsx",
                b"placeholder workbook bytes",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "uploaded"
    assert body["template_id"] == "indian_rice_exports"
    assert body["filename"] == "shipment.xlsx"
    assert body["job_id"]

    stored_path = upload_dir / f"{body['job_id']}.xlsx"
    assert stored_path.exists()
    assert stored_path.read_bytes() == b"placeholder workbook bytes"

    job_response = client.get(f"/jobs/{body['job_id']}")
    assert job_response.status_code == 200
    job_body = job_response.json()
    assert job_body["job_id"] == body["job_id"]
    assert job_body["template_id"] == "indian_rice_exports"
    assert job_body["original_filename"] == "shipment.xlsx"
    assert job_body["stored_filename"] == f"{body['job_id']}.xlsx"
    assert job_body["status"] == "uploaded"
    assert job_body["created_at"]
    assert job_body["updated_at"]


def test_upload_creates_upload_directory(tmp_path) -> None:
    client, upload_dir = _client_with_temp_job_service(tmp_path)
    assert not upload_dir.exists()

    response = client.post(
        "/jobs",
        data={"template_id": "indian_rice_exports"},
        files={"file": ("shipment.xls", b"bytes", "application/vnd.ms-excel")},
    )

    assert response.status_code == 200
    assert upload_dir.exists()


def test_upload_invalid_extension_returns_400(tmp_path) -> None:
    client, _ = _client_with_temp_job_service(tmp_path)

    response = client.post(
        "/jobs",
        data={"template_id": "indian_rice_exports"},
        files={"file": ("shipment.csv", b"bytes", "text/csv")},
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "upload_validation_error"


def test_upload_missing_template_returns_404(tmp_path) -> None:
    client, _ = _client_with_temp_job_service(tmp_path)

    response = client.post(
        "/jobs",
        data={"template_id": "missing_template"},
        files={
            "file": (
                "shipment.xlsx",
                b"bytes",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "template_not_found"


def test_upload_oversized_file_returns_400(tmp_path) -> None:
    client, _ = _client_with_temp_job_service(tmp_path, max_upload_size_mb=1)

    response = client.post(
        "/jobs",
        data={"template_id": "indian_rice_exports"},
        files={
            "file": (
                "shipment.xlsx",
                b"x" * (1024 * 1024 + 1),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "upload_validation_error"


def test_get_missing_job_returns_404(tmp_path) -> None:
    client, _ = _client_with_temp_job_service(tmp_path)

    response = client.get("/jobs/missing-job")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "job_not_found"


def _client_with_temp_job_service(
    tmp_path,
    *,
    max_upload_size_mb: int = 50,
) -> tuple[TestClient, Path]:
    upload_dir = tmp_path / "uploads"
    database_path = tmp_path / "tradeflow.sqlite"
    template_repository = FileSystemTemplateRepository(Path("../templates"))
    job_repository = SQLiteJobRepository(database_path)
    uploaded_file_storage = LocalUploadedFileStorage(upload_dir, max_upload_size_mb)
    job_service = JobService(
        job_repository=job_repository,
        template_repository=template_repository,
        uploaded_file_storage=uploaded_file_storage,
        allowed_extensions=(".xlsx", ".xls"),
    )
    app = create_app()
    app.dependency_overrides[get_job_service] = lambda: job_service
    
    # Override auth to simulate logged in user
    user = create_test_user()
    override_auth(app, user, tenant_id="test_tenant")
    
    return TestClient(app), upload_dir
