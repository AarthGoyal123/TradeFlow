"""Processing stages for intermediate dataset preparation."""

from app.domain.datasets.models import DatasetCell, DatasetRow, IntermediateDataset
from app.domain.templates.models import TemplateDefinition
from app.domain.workbooks.models import CellValue


class ColumnRemovalStage:
    """Remove template-configured fields or source headers from a dataset."""

    def run(
        self,
        *,
        dataset: IntermediateDataset,
        template: TemplateDefinition,
    ) -> IntermediateDataset:
        """Return a dataset without configured removed columns."""
        removals = {
            self._normalize_key(column_name)
            for column_name in template.columns.remove_columns
        }
        if not removals:
            return dataset

        rows = tuple(
            DatasetRow(
                source_row_number=row.source_row_number,
                cells=tuple(
                    cell
                    for cell in row.cells
                    if self._normalize_key(cell.field) not in removals
                    and self._normalize_key(cell.source_header) not in removals
                ),
                confidence=row.confidence,
            )
            for row in dataset.rows
        )
        removed_fields = tuple(
            field
            for field in dataset.fields
            if self._normalize_key(field) in removals
        )
        return IntermediateDataset(
            template_id=dataset.template_id,
            sheet_name=dataset.sheet_name,
            rows=rows,
            removed_fields=removed_fields,
        )

    @staticmethod
    def _normalize_key(value: str) -> str:
        return " ".join(value.strip().casefold().split())


class NormalizationStage:
    """Normalize scalar values for consistent downstream processing."""

    def run(self, *, dataset: IntermediateDataset) -> IntermediateDataset:
        """Return a normalized dataset."""
        return IntermediateDataset(
            template_id=dataset.template_id,
            sheet_name=dataset.sheet_name,
            rows=tuple(self._normalize_row(row) for row in dataset.rows),
            removed_fields=dataset.removed_fields,
        )

    def _normalize_row(self, row: DatasetRow) -> DatasetRow:
        return DatasetRow(
            source_row_number=row.source_row_number,
            cells=tuple(
                DatasetCell(
                    field=cell.field,
                    source_header=cell.source_header,
                    value=self._normalize_value(cell.value),
                )
                for cell in row.cells
            ),
            confidence=row.confidence,
        )

    @staticmethod
    def _normalize_value(value: CellValue) -> CellValue:
        if isinstance(value, str):
            normalized = " ".join(value.strip().split())
            return normalized if normalized else None
        return value

