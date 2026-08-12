import io
import pytest
from pathlib import Path

from app.application.jobs.service import JobService
from app.core.errors import StorageError
from app.domain.outputs.models import OutputType
from app.infrastructure.files.local_outputs import LocalOutputStorage

def test_original_filename_sanitized(mocker) -> None:
    job_repo = mocker.Mock()
    job_repo.create_job.return_value = mocker.Mock(job_id="1", template_id="t1")
    template_repo = mocker.Mock()
    file_storage = mocker.Mock()
    file_storage.save.return_value = "saved.xlsx"

    service = JobService(
        job_repository=job_repo,
        template_repository=template_repo,
        uploaded_file_storage=file_storage,
        allowed_extensions=(".xlsx",)
    )

    malicious_filename = "../../../etc/passwd.xlsx"
    service.create_uploaded_job(
        template_id="t1",
        original_filename=malicious_filename,
        file=io.BytesIO(b"dummy")
    )
    
    # Assert filename is sanitized
    file_storage.save.assert_called_once()
    assert file_storage.save.call_args[1]["original_filename"] == "passwd.xlsx"


def test_local_output_storage_path_traversal(tmp_path: Path) -> None:
    storage = LocalOutputStorage(tmp_path)
    
    # job_id with path traversal
    with pytest.raises(StorageError, match="Invalid output path"):
        storage.get_output(job_id="../../etc", output_type=OutputType.CLEAN_DATA)
