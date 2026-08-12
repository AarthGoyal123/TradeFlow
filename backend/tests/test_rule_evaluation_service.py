from app.application.rules.service import RuleEvaluationService
from app.domain.datasets.models import DatasetCell, DatasetRow, IntermediateDataset
from app.domain.rules.models import (
    RuleCondition,
    RuleDefinition,
    RuleOperatorName,
    RuleSeverity,
    RuleType,
)
from app.domain.rules.ports import RulePackRepository


def test_rule_evaluation_service_returns_complete_report() -> None:
    dataset = IntermediateDataset(
        template_id="indian_rice_exports",
        sheet_name="Shipments",
        rows=(
            DatasetRow(
                source_row_number=2,
                cells=(
                    DatasetCell("consignee_name", "Consignee", "STATE BANK OF INDIA"),
                    DatasetCell("port", "Port", None),
                ),
            ),
        ),
    )
    rules = (
        RuleDefinition(
            rule_id="validation_port_required",
            name="Port required",
            rule_type=RuleType.VALIDATION,
            condition=RuleCondition(field="port", operator=RuleOperatorName.IS_EMPTY),
            severity=RuleSeverity.ERROR,
            priority=20,
            message="Port is required",
        ),
        RuleDefinition(
            rule_id="classification_bank",
            name="Bank classification",
            rule_type=RuleType.ROW_CLASSIFICATION,
            condition=RuleCondition(
                field="consignee_name",
                operator=RuleOperatorName.CONTAINS,
                expected_value="bank",
            ),
            classification="bank",
            priority=10,
            message="Consignee appears to be a bank",
        ),
        RuleDefinition(
            rule_id="disabled_rule",
            name="Disabled",
            rule_type=RuleType.VALIDATION,
            condition=RuleCondition(field="port", operator=RuleOperatorName.IS_EMPTY),
            enabled=False,
        ),
    )

    report = RuleEvaluationService().evaluate(dataset=dataset, rules=rules)

    assert report.template_id == "indian_rice_exports"
    assert report.row_count == 1
    assert report.rules_evaluated == 2
    assert [match.rule_id for match in report.matches] == [
        "classification_bank",
        "validation_port_required",
    ]
    assert report.classifications[0].classification == "bank"
    assert report.validation_findings[0].message == "Port is required"


def test_rule_evaluation_service_reports_transformations() -> None:
    dataset = IntermediateDataset(
        template_id="indian_rice_exports",
        sheet_name="Shipments",
        rows=(
            DatasetRow(
                source_row_number=2,
                cells=(DatasetCell("consignee_name", "Consignee", "TO THE ORDER"),),
            ),
        ),
    )
    rule = RuleDefinition(
        rule_id="normalize_to_order",
        name="Normalize To Order",
        rule_type=RuleType.CELL_TRANSFORMATION,
        condition=RuleCondition(
            field="consignee_name",
            operator=RuleOperatorName.EQUALS,
            expected_value="to the order",
        ),
        transform_to="TO ORDER",
    )

    report = RuleEvaluationService().evaluate(dataset=dataset, rules=(rule,))

    assert report.transformations[0].field == "consignee_name"
    assert report.transformations[0].transformed_value == "TO ORDER"


def test_rule_evaluation_service_loads_enabled_rule_packs() -> None:
    dataset = IntermediateDataset(
        template_id="indian_rice_exports",
        sheet_name="Shipments",
        rows=(
            DatasetRow(
                source_row_number=2,
                cells=(DatasetCell("consignee_name", "Consignee", "STATE BANK OF INDIA"),),
            ),
        ),
    )
    rule = RuleDefinition(
        rule_id="classification_bank",
        name="Bank classification",
        rule_type=RuleType.ROW_CLASSIFICATION,
        condition=RuleCondition(
            field="consignee_name",
            operator=RuleOperatorName.CONTAINS,
            expected_value="bank",
        ),
        classification="bank",
    )

    report = RuleEvaluationService(
        rule_pack_repository=_RulePackRepository(rule),
    ).evaluate_template_rules(dataset=dataset)

    assert report.rules_evaluated == 1
    assert report.classifications[0].classification == "bank"


class _RulePackRepository(RulePackRepository):
    def __init__(self, rule: RuleDefinition) -> None:
        self._rule = rule

    def list_rule_packs(self, template_id: str):
        from app.domain.rules.models import RulePackDefinition

        return (
            RulePackDefinition(
                pack_id="pack",
                name="Pack",
                version="1.0.0",
                enabled=True,
                rules=(self._rule,),
            ),
        )
