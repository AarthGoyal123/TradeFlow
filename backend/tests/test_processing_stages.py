from app.application.processing.stages import ColumnRemovalStage, NormalizationStage
from app.domain.datasets.models import DatasetCell, DatasetRow, IntermediateDataset
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


def test_column_removal_stage_removes_configured_fields() -> None:
    dataset = IntermediateDataset(
        template_id="template",
        sheet_name="Sheet1",
        rows=(
            DatasetRow(
                source_row_number=2,
                cells=(
                    DatasetCell("consignee_name", "Consignee", "ACME"),
                    DatasetCell("port", "Port", "Mundra"),
                ),
            ),
        ),
    )

    result = ColumnRemovalStage().run(dataset=dataset, template=_template(remove_columns=["port"]))

    assert result.fields == ("consignee_name",)
    assert result.removed_fields == ("port",)


def test_normalization_stage_normalizes_string_values() -> None:
    dataset = IntermediateDataset(
        template_id="template",
        sheet_name="Sheet1",
        rows=(
            DatasetRow(
                source_row_number=2,
                cells=(DatasetCell("consignee_name", "Consignee", "  ACME   EXPORTS  "),),
            ),
        ),
    )

    result = NormalizationStage().run(dataset=dataset)

    assert result.rows[0].value_for("consignee_name") == "ACME EXPORTS"


def _template(*, remove_columns: list[str]) -> TemplateDefinition:
    return TemplateDefinition(
        config=TemplateConfig(
            id="template",
            name="Template",
            version="0.1.0",
            workbook=WorkbookConfig(sheet_strategy="first_sheet"),
            enabled_modules=["validation"],
        ),
        columns=ColumnsConfig.model_validate(
            {
                "required_fields": [{"field": "consignee_name", "aliases": ["Consignee"]}],
                "optional_fields": [{"field": "port", "aliases": ["Port"]}],
                "remove_columns": remove_columns,
            }
        ),
        pipeline=PipelineConfig(steps=["validation"]),
        output=OutputConfig(files=OutputFiles(), review_threshold=0.75),
        keyword_rules=RulePack(),
        regex_rules=RulePack(),
        fuzzy_matches=RulePack(),
    )
