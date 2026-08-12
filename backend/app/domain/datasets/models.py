"""Domain-owned intermediate dataset models."""

from dataclasses import dataclass

from app.domain.workbooks.models import CellValue


@dataclass(frozen=True, slots=True)
class DatasetCell:
    """One mapped and normalized intermediate dataset value."""

    field: str
    source_header: str
    value: CellValue


@dataclass(frozen=True, slots=True)
class DatasetRow:
    """One intermediate dataset row linked to the source worksheet row."""

    source_row_number: int
    cells: tuple[DatasetCell, ...]
    confidence: float = 0.0

    def value_for(self, field: str) -> CellValue:
        """Return a cell value by conceptual field."""
        for cell in self.cells:
            if cell.field == field:
                return cell.value
        return None


@dataclass(frozen=True, slots=True)
class IntermediateDataset:
    """Normalized intermediate dataset used by future processing stages."""

    template_id: str
    sheet_name: str
    rows: tuple[DatasetRow, ...]
    removed_fields: tuple[str, ...] = ()

    @property
    def row_count(self) -> int:
        """Return the number of data rows."""
        return len(self.rows)

    @property
    def fields(self) -> tuple[str, ...]:
        """Return the dataset fields in row order."""
        if not self.rows:
            return ()
        return tuple(cell.field for cell in self.rows[0].cells)

    def reorder(self, column_order: tuple[str, ...]) -> "IntermediateDataset":
        """Return a new dataset with columns reordered and filtered to the given order."""
        current_fields = self.fields
        index_of = {f: i for i, f in enumerate(current_fields)}
        keep = [f for f in column_order if f in index_of]
        if not keep or keep == list(current_fields):
            return self
        new_rows = tuple(
            DatasetRow(
                source_row_number=row.source_row_number,
                cells=tuple(row.cells[index_of[f]] for f in keep),
                confidence=row.confidence,
            )
            for row in self.rows
        )
        return IntermediateDataset(
            template_id=self.template_id,
            sheet_name=self.sheet_name,
            rows=new_rows,
            removed_fields=self.removed_fields,
        )
