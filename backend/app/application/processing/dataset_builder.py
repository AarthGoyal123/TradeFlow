"""Build intermediate datasets from validated workbook rows."""

from app.domain.datasets.models import DatasetCell, DatasetRow, IntermediateDataset
from app.domain.workbooks.models import CellValue, MappedColumn, WorkbookValidationResult
from app.domain.workbooks.ports import WorksheetReader


class IntermediateDatasetBuilder:
    """Build an intermediate dataset from mapped worksheet columns."""

    def build(
        self,
        *,
        validation_result: WorkbookValidationResult,
        worksheet: WorksheetReader,
    ) -> IntermediateDataset:
        """Create an intermediate dataset from worksheet rows."""
        mapped_columns = validation_result.mapped_columns
        rows = tuple(
            self._build_row(
                row_number=row.row_number,
                values=row.values,
                mapped_columns=mapped_columns,
            )
            for row in worksheet.iter_rows(min_row=2)
            if self._has_any_value(row.values)
        )
        return IntermediateDataset(
            template_id=validation_result.template_id,
            sheet_name=validation_result.sheet_name or worksheet.name,
            rows=rows,
        )

    @staticmethod
    def _build_row(
        *,
        row_number: int,
        values: tuple[CellValue, ...],
        mapped_columns: tuple[MappedColumn, ...],
    ) -> DatasetRow:
        cells = tuple(
            DatasetCell(
                field=column.field,
                source_header=column.source_header,
                value=values[column.column_number - 1]
                if column.column_number <= len(values)
                else None,
            )
            for column in mapped_columns
        )
        row_confidence = (
            sum(c.confidence for c in mapped_columns) / len(mapped_columns)
            if mapped_columns else 0.0
        )
        return DatasetRow(source_row_number=row_number, cells=cells, confidence=row_confidence)

    @staticmethod
    def _has_any_value(values: tuple[CellValue, ...]) -> bool:
        return any(value is not None for value in values)
