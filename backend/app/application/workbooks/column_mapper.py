"""Template column mapping for workbook headers."""

from app.domain.templates.models import ColumnMapping, TemplateDefinition
from app.domain.workbooks.models import (
    HeaderCell,
    MappedColumn,
    WorkbookValidationIssue,
    WorksheetHeader,
)


class TemplateColumnMapper:
    """Map template conceptual columns to worksheet header columns."""

    def map_columns(
        self,
        *,
        template: TemplateDefinition,
        header: WorksheetHeader,
    ) -> tuple[tuple[MappedColumn, ...], tuple[WorkbookValidationIssue, ...]]:
        """Resolve required and optional template fields against a worksheet header."""
        header_lookup = {
            self._normalize_header(cell.value): cell for cell in header.cells if cell.value
        }
        mapped_columns: list[MappedColumn] = []
        issues: list[WorkbookValidationIssue] = []

        for column in template.columns.required_fields:
            mapped_column = self._map_column(
                column=column,
                header_lookup=header_lookup,
                required=True,
            )
            if mapped_column is None:
                issues.append(
                    WorkbookValidationIssue(
                        code="missing_required_column",
                        message=f"Missing required column for field '{column.field}'",
                        details={"field": column.field, "aliases": column.aliases},
                    )
                )
            else:
                mapped_columns.append(mapped_column)

        for column in template.columns.optional_fields:
            mapped_column = self._map_column(
                column=column,
                header_lookup=header_lookup,
                required=False,
            )
            if mapped_column is not None:
                mapped_columns.append(mapped_column)

        return tuple(mapped_columns), tuple(issues)

    def _map_column(
        self,
        *,
        column: ColumnMapping,
        header_lookup: dict[str, HeaderCell],
        required: bool,
    ) -> MappedColumn | None:
        for alias in column.aliases:
            matched_cell = header_lookup.get(self._normalize_header(alias))
            if matched_cell is not None:
                return MappedColumn(
                    field=column.field,
                    required=required,
                    source_header=matched_cell.value,
                    column_number=matched_cell.column_number,
                )
        return None

    @staticmethod
    def _normalize_header(value: str) -> str:
        return " ".join(value.strip().casefold().split())
