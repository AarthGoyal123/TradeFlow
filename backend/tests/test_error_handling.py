from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.errors import register_exception_handlers
from app.core.errors import JobNotFoundError, StorageError, WorkbookValidationError

app = FastAPI()
register_exception_handlers(app)


@app.get("/error/storage")
def route_storage_error() -> None:
    raise StorageError("Disk full", details={"path": "/tmp/secret/file.txt"})


@app.get("/error/validation")
def route_validation_error() -> None:
    raise WorkbookValidationError("Invalid headers", details={"missing": ["date"]})


@app.get("/error/job-not-found")
def route_not_found() -> None:
    raise JobNotFoundError("Job 123 missing", details={"job_id": "123"})


client = TestClient(app)


def test_storage_error_is_sanitized() -> None:
    response = client.get("/error/storage")
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "storage_error"
    # The message is sanitized and details are stripped
    assert data["error"]["message"] == "An internal system error occurred."
    assert data["error"]["details"] == {}
    assert "secret/file" not in response.text


def test_validation_error_is_returned_fully() -> None:
    response = client.get("/error/validation")
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "workbook_validation_error"
    assert data["error"]["message"] == "Invalid headers"
    assert data["error"]["details"] == {"missing": ["date"]}


def test_not_found_error_is_404() -> None:
    response = client.get("/error/job-not-found")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "job_not_found"
    assert data["error"]["message"] == "Job 123 missing"
    assert data["error"]["details"] == {"job_id": "123"}
