from app.domain.datasets.models import DatasetCell, DatasetRow
from app.domain.rules.evaluator import RuleEvaluator
from app.domain.rules.models import (
    RuleCondition,
    RuleDefinition,
    RuleOperatorName,
    RuleSeverity,
    RuleType,
)


def test_rule_evaluator_returns_row_classification() -> None:
    row = DatasetRow(
        source_row_number=2,
        cells=(DatasetCell("consignee_name", "Consignee", "STATE BANK OF INDIA"),),
    )
    rule = RuleDefinition(
        rule_id="bank_rule",
        name="Bank detector",
        rule_type=RuleType.ROW_CLASSIFICATION,
        condition=RuleCondition(
            field="consignee_name",
            operator=RuleOperatorName.CONTAINS,
            expected_value="bank",
        ),
        classification="bank",
        severity=RuleSeverity.WARNING,
        message="Consignee appears to be a bank",
    )

    match, classification, transformation, validation_finding = RuleEvaluator().evaluate_row(
        row=row,
        rule=rule,
    )

    assert match is not None
    assert classification is not None
    assert classification.classification == "bank"
    assert classification.row_number == 2
    assert transformation is None
    assert validation_finding is None


def test_rule_evaluator_returns_cell_transformation_without_mutating_row() -> None:
    row = DatasetRow(
        source_row_number=2,
        cells=(DatasetCell("consignee_name", "Consignee", "TO THE ORDER"),),
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
        message="Normalize placeholder consignee",
    )

    _, _, transformation, _ = RuleEvaluator().evaluate_row(row=row, rule=rule)

    assert transformation is not None
    assert transformation.original_value == "TO THE ORDER"
    assert transformation.transformed_value == "TO ORDER"
    assert row.value_for("consignee_name") == "TO THE ORDER"


def test_rule_evaluator_returns_validation_finding() -> None:
    row = DatasetRow(source_row_number=2, cells=(DatasetCell("port", "Port", None),))
    rule = RuleDefinition(
        rule_id="port_required",
        name="Port required",
        rule_type=RuleType.VALIDATION,
        condition=RuleCondition(field="port", operator=RuleOperatorName.IS_EMPTY),
        severity=RuleSeverity.ERROR,
        message="Port is required",
    )

    _, _, _, validation_finding = RuleEvaluator().evaluate_row(row=row, rule=rule)

    assert validation_finding is not None
    assert validation_finding.severity == RuleSeverity.ERROR
    assert validation_finding.message == "Port is required"


def test_disabled_rule_does_not_match() -> None:
    row = DatasetRow(source_row_number=2, cells=(DatasetCell("port", "Port", None),))
    rule = RuleDefinition(
        rule_id="disabled",
        name="Disabled",
        rule_type=RuleType.VALIDATION,
        condition=RuleCondition(field="port", operator=RuleOperatorName.IS_EMPTY),
        enabled=False,
    )

    assert RuleEvaluator().evaluate_row(row=row, rule=rule) == (None, None, None, None)

