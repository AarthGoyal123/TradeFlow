import io
from pathlib import Path
from unittest.mock import MagicMock

from app.domain.datasets.models import DatasetCell, DatasetRow, IntermediateDataset
from app.domain.outputs.models import OutputArtifact, OutputType
from app.domain.outputs.ports import OutputStorage
from app.domain.rules.models import RuleExecutionReport
from app.infrastructure.excel.output_builder import OpenPyXLOutputWorkbookBuilder
from app.infrastructure.files.local_outputs import LocalOutputStorage


def test_output_builder_saves_to_bytesio_and_calls_save_output():
    builder = OpenPyXLOutputWorkbookBuilder()
    mock_storage = MagicMock(spec=OutputStorage)

    # Mock save_output to return a dummy artifact
    def mock_save_output(job_id, output_type, file_obj):
        assert isinstance(file_obj, io.BytesIO)
        assert file_obj.tell() == 0  # Buffer must be seek(0)'d

        # Verify it's a valid zip/xlsx file by reading signature
        data = file_obj.read(4)
        assert data == b"PK\x03\x04"
        file_obj.seek(0)

        return OutputArtifact(output_type=output_type, filename="test.xlsx", path=Path("test.xlsx"))

    mock_storage.save_output.side_effect = mock_save_output

    dataset = IntermediateDataset(
        template_id="test",
        sheet_name="Data",
        rows=(
            DatasetRow(
                source_row_number=1,
                cells=(DatasetCell("col1", "col1", "A"), DatasetCell("col2", "col2", "B")),
            ),
        ),
    )
    rule_report = RuleExecutionReport(
        template_id="test",
        row_count=1,
        rules_evaluated=0,
        matches=tuple(),
        routed_rows=tuple(),
        validation_findings=tuple(),
        classifications=tuple(),
        transformations=tuple(),
    )

    artifacts = builder.build(
        job_id="job123", dataset=dataset, rule_report=rule_report, output_storage=mock_storage
    )

    assert len(artifacts) == 4
    assert mock_storage.save_output.call_count == 4

    # Ensure no output_path is called
    assert not hasattr(mock_storage, "output_path") or not mock_storage.output_path.called


def test_local_output_storage_save_output(tmp_path):
    storage = LocalOutputStorage(output_dir=tmp_path)

    buf = io.BytesIO(b"dummy data")
    artifact = storage.save_output("job1", OutputType.CLEAN_DATA, buf)

    assert artifact.output_type == OutputType.CLEAN_DATA
    assert artifact.filename == "Clean_Data.xlsx"

    expected_path = tmp_path / "job1" / "Clean_Data.xlsx"
    assert artifact.path == expected_path
    assert expected_path.exists()
    assert expected_path.read_bytes() == b"dummy data"
