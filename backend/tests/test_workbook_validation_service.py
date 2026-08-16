from pathlib import Path
from typing import Literal

from openpyxl import Workbook

from app.application.workbooks.column_mapper import TemplateColumnMapper
from app.application.workbooks.validation import WorkbookValidationService
from app.domain.templates.models import (
    ColumnsConfig,
    OutputConfig,
    OutputFiles,
    PipelineConfig,
    RulePack,
    TemplateConfig,
    TemplateDefinition,
    WorkbookConfig,
)
from app.infrastructure.excel.openpyxl_loader import OpenPyXLWorkbookLoader


def test_validation_service_maps_required_and_optional_columns(tmp_path) -> None:
    workbook_path = _create_workbook(tmp_path, headers=["Consignee", "POD", "Carrier"])
    service = _validation_service(build_test_template())

    result = service.validate(template_id="indian_rice_exports", workbook_path=workbook_path)

    assert result.valid is True
    assert result.sheet_name == "Shipments"
    mapped_columns = [
        (column.field, column.source_header, column.column_number)
        for column in result.mapped_columns
    ]
    assert mapped_columns == [
        ("consignee_name", "Consignee", 1),
        ("port", "POD", 2),
        ("shipping_company", "Carrier", 3),
    ]
    assert result.issues == ()


def test_validation_service_reports_missing_required_columns(tmp_path) -> None:
    workbook_path = _create_workbook(tmp_path, headers=["Consignee", "Carrier"])
    service = _validation_service(build_test_template())

    result = service.validate(template_id="indian_rice_exports", workbook_path=workbook_path)

    assert result.valid is False
    assert result.issues[0].code == "missing_required_column"
    assert result.issues[0].details["field"] == "port"


def test_validation_service_reports_missing_named_sheet(tmp_path) -> None:
    workbook_path = _create_workbook(tmp_path, headers=["Consignee", "POD"])
    service = _validation_service(build_test_template(sheet_strategy="named_sheet", sheet_name="Missing"))

    result = service.validate(template_id="indian_rice_exports", workbook_path=workbook_path)

    assert result.valid is False
    assert result.sheet_name is None
    assert result.issues[0].code == "required_sheet_missing"
    assert result.issues[0].details["required_sheet"] == "Missing"


def test_validation_service_returns_structured_issue_for_unreadable_workbook(tmp_path) -> None:
    workbook_path = tmp_path / "broken.xlsx"
    workbook_path.write_bytes(b"not a workbook")
    service = _validation_service(build_test_template())

    result = service.validate(template_id="indian_rice_exports", workbook_path=workbook_path)

    assert result.valid is False
    assert result.issues[0].code == "workbook_validation_error"


def _create_workbook(tmp_path, *, headers: list[str]) -> Path:
    workbook_path = tmp_path / "shipment.xlsx"
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Shipments"
    worksheet.append(headers)
    worksheet.append(["value"])
    workbook.save(workbook_path)
    return workbook_path


def _validation_service(template: TemplateDefinition) -> WorkbookValidationService:
    return WorkbookValidationService(
        template_repository=_TemplateRepository(template),
        workbook_loader=OpenPyXLWorkbookLoader(),
        column_mapper=TemplateColumnMapper(),
    )


def build_test_template(
    sheet_strategy: Literal["first_sheet", "named_sheet"] = "first_sheet",
    sheet_name: str | None = None,
) -> TemplateDefinition:
    return TemplateDefinition(
        config=TemplateConfig(
            id="indian_rice_exports",
            name="Indian Rice Export Shipments",
            version="0.1.0",
            description="Test template",
            workbook=WorkbookConfig(sheet_strategy=sheet_strategy, sheet_name=sheet_name),
            enabled_modules=["validation"],
        ),
        columns=ColumnsConfig.model_validate(
            {
                "required_fields": [
                    {
                        "field": "consignee_name",
                        "aliases": ["Consignee", "Importer"],
                    },
                    {
                        "field": "port",
                        "aliases": ["Port", "POD"],
                    },
                ],
                "optional_fields": [
                    {
                        "field": "shipping_company",
                        "aliases": ["Shipping Line", "Carrier"],
                    }
                ],
                "remove_columns": [],
            }
        ),
        pipeline=PipelineConfig(steps=["validation"]),
        output=OutputConfig(files=OutputFiles(), review_threshold=0.75),
        keyword_rules=RulePack(),
        regex_rules=RulePack(),
        fuzzy_matches=RulePack(),
    )


class _TemplateRepository:
    def __init__(self, template: TemplateDefinition) -> None:
        self._template = template

    def list_templates(self) -> list[TemplateDefinition]:
        return [self._template]

    def get_template(self, template_id: str) -> TemplateDefinition:
        return self._template
