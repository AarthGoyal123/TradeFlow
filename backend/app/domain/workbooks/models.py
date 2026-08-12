"""Workbook domain models."""

from dataclasses import dataclass
from pathlib import Path

type CellValue = str | int | float | bool | None


@dataclass(frozen=True, slots=True)
class WorkbookRow:
    """One worksheet row with its original worksheet row number."""

    row_number: int
    values: tuple[CellValue, ...]


@dataclass(frozen=True, slots=True)
class HeaderCell:
    """One normalized header cell position."""

    column_number: int
    value: str


@dataclass(frozen=True, slots=True)
class WorksheetHeader:
    """Header row extracted from a worksheet."""

    row_number: int
    cells: tuple[HeaderCell, ...]


@dataclass(frozen=True, slots=True)
class MappedColumn:
    """Resolved template field to worksheet column mapping."""

    field: str
    required: bool
    source_header: str
    column_number: int
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class WorkbookValidationIssue:
    """Structured workbook validation issue."""

    code: str
    message: str
    details: dict[str, object]


@dataclass(frozen=True, slots=True)
class WorkbookValidationResult:
    """Result of validating a workbook against a processing template."""

    template_id: str
    workbook_path: Path
    valid: bool
    sheet_name: str | None
    available_sheets: tuple[str, ...]
    header: WorksheetHeader | None
    mapped_columns: tuple[MappedColumn, ...]
    issues: tuple[WorkbookValidationIssue, ...]
