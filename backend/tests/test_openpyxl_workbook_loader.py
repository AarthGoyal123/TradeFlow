from openpyxl import Workbook

from app.core.errors import WorkbookValidationError
from app.infrastructure.excel.openpyxl_loader import OpenPyXLWorkbookLoader


def test_openpyxl_loader_reads_headers_rows_and_empty_cells(tmp_path) -> None:
    workbook_path = tmp_path / "shipment.xlsx"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Shipments"
    worksheet.append(["Consignee", "", "Port"])
    worksheet.append(["ACME EXPORTS", "", "Mundra"])
    workbook.save(workbook_path)

    document = OpenPyXLWorkbookLoader().load(workbook_path)
    sheet = document.first_sheet()

    header = sheet.read_header()
    rows = list(sheet.iter_rows(min_row=2))

    assert document.sheet_names == ("Shipments",)
    assert header.row_number == 1
    assert [(cell.column_number, cell.value) for cell in header.cells] == [
        (1, "Consignee"),
        (3, "Port"),
    ]
    assert rows[0].row_number == 2
    assert rows[0].values == ("ACME EXPORTS", None, "Mundra")


def test_openpyxl_loader_rejects_unsupported_extension(tmp_path) -> None:
    workbook_path = tmp_path / "shipment.xls"
    workbook_path.write_bytes(b"not an xlsx workbook")

    try:
        OpenPyXLWorkbookLoader().load(workbook_path)
    except WorkbookValidationError as exc:
        assert exc.code == "workbook_validation_error"
        assert exc.details["supported_extensions"] == [".xlsx"]
    else:
        raise AssertionError("Expected WorkbookValidationError")

