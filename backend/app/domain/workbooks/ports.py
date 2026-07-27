"""Ports for workbook loading and sheet reading."""

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

from app.domain.workbooks.models import WorkbookRow, WorksheetHeader


class WorksheetReader(Protocol):
    """Read worksheet structure without exposing a specific Excel library."""

    @property
    def name(self) -> str:
        """Return worksheet name."""
        ...

    def read_header(self, row_number: int = 1) -> WorksheetHeader:
        """Return the configured header row."""
        ...

    def iter_rows(self, *, min_row: int = 1) -> Iterator[WorkbookRow]:
        """Yield worksheet rows while preserving row numbers."""
        ...


class WorkbookDocument(Protocol):
    """Workbook abstraction used outside Excel-specific infrastructure."""

    @property
    def sheet_names(self) -> tuple[str, ...]:
        """Return workbook sheet names."""
        ...

    def first_sheet(self) -> WorksheetReader:
        """Return the first worksheet."""
        ...

    def sheet_by_name(self, sheet_name: str) -> WorksheetReader | None:
        """Return a worksheet by name if present."""
        ...


class WorkbookLoader(Protocol):
    """Load workbooks from storage."""

    def load(self, workbook_path: Path) -> WorkbookDocument:
        """Load a workbook document."""
        ...

