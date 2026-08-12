"""Workbook Analyzer — structure, sheet, header, and data sampling."""


from app.domain.workbooks.intelligence import (
    DataSampleAnalysis,
    FileMetadata,
    HeaderAnalysis,
    SheetInfo,
    StructureAnalysis,
)
from app.domain.workbooks.ports import WorkbookDocument, WorksheetReader


class WorkbookAnalyzer:
    """Analyze workbook structure before any validation."""

    def analyze(self, workbook: WorkbookDocument) -> StructureAnalysis:
        sheet_infos: list[SheetInfo] = []
        sheet_readers: dict[str, WorksheetReader] = {}

        for name in workbook.sheet_names:
            try:
                sheet = workbook.sheet_by_name(name)
                if sheet is None:
                    continue
                sheet_readers[name] = sheet
                rows = list(sheet.iter_rows(min_row=1))[:5]
                col_count = max((len(r.values) for r in rows if r.values), default=0)
                total = len(list(sheet.iter_rows(min_row=1)))
                sheet_infos.append(SheetInfo(
                    name=name,
                    row_count=total,
                    column_count=col_count,
                    is_likely_data_sheet=False,
                ))
            except Exception:
                continue

        sheets = tuple(sheet_infos)
        likely = self._find_likely_data_sheet(sheets)
        sheet_reader = sheet_readers.get(likely.name) if likely else None

        header = self._detect_header(sheet_reader, likely) if sheet_reader and likely else HeaderAnalysis(
            detected_row=1, confidence=0.0, cells=(), detection_method="none",
        )
        data_sample = self._sample_data(sheet_reader, header.detected_row) if sheet_reader else DataSampleAnalysis(
            column_count=0, estimated_data_rows=0, estimated_empty_rows=0,
            has_title_rows=False, title_row_count=0, column_types={},
        )

        file_meta = FileMetadata(
            size_bytes=0, filename="", extension=".xlsx", sheet_count=len(sheets),
        )

        conf = 0.0
        if header.detection_method == "row_1":
            conf = 0.95
        elif header.detection_method == "heuristic":
            conf = 0.85
        elif header.detection_method == "content_based":
            conf = 0.75

        return StructureAnalysis(
            file_metadata=file_meta,
            sheets=sheets,
            likely_data_sheet=likely,
            header=header,
            data_sample=data_sample,
            structure_confidence=conf,
        )

    @staticmethod
    def _find_likely_data_sheet(sheets: tuple[SheetInfo, ...]) -> SheetInfo | None:
        for s in sheets:
            if s.row_count > 5 and s.column_count >= 3:
                return s
        return sheets[0] if sheets else None

    @staticmethod
    def _detect_header(sheet: WorksheetReader, info: SheetInfo) -> HeaderAnalysis:
        header = sheet.read_header(1)
        cells = tuple(c.value for c in header.cells if c.value)
        return HeaderAnalysis(
            detected_row=header.row_number,
            confidence=0.95,
            cells=cells,
            detection_method="row_1",
        )

    @staticmethod
    def _sample_data(sheet: WorksheetReader, header_row: int) -> DataSampleAnalysis:
        data_rows = list(sheet.iter_rows(min_row=header_row + 1))
        header = sheet.read_header(header_row)
        col_count = len([c for c in header.cells if c.value])

        empty_rows = 0
        col_types: dict[str, str] = {}
        for cell in header.cells:
            if not cell.value:
                continue
            values = [
                str(r.values[cell.column_number - 1]).strip()
                for r in data_rows[:20]
                if r.values and len(r.values) >= cell.column_number
                and r.values[cell.column_number - 1] is not None
            ]
            if values:
                numeric = sum(1 for v in values if _is_numeric(v))
                col_types[cell.value] = "numeric" if numeric > len(values) * 0.6 else "text"

        for r in data_rows[:20]:
            if all(v is None or str(v).strip() == "" for v in (r.values or [])):
                empty_rows += 1

        return DataSampleAnalysis(
            column_count=col_count,
            estimated_data_rows=len(data_rows),
            estimated_empty_rows=empty_rows,
            has_title_rows=header_row > 1,
            title_row_count=header_row - 1,
            column_types=col_types,
        )


def _is_numeric(v: str) -> bool:
    try:
        float(v.replace(",", ""))
        return True
    except ValueError:
        return False