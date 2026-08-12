"""Rule evaluator for intermediate dataset rows."""

from app.domain.datasets.models import DatasetRow
from app.domain.rules.models import (
    CellTransformation,
    RowClassification,
    RuleDefinition,
    RuleMatch,
    RuleType,
    ValidationFinding,
)
from app.domain.rules.operators import RuleOperatorRegistry
from app.domain.workbooks.models import CellValue


class RuleEvaluator:
    """Evaluate rule definitions against dataset rows."""

    def __init__(self, operator_registry: RuleOperatorRegistry | None = None) -> None:
        self._operator_registry = operator_registry or RuleOperatorRegistry()

    def evaluate_row(
        self,
        *,
        row: DatasetRow,
        rule: RuleDefinition,
    ) -> tuple[
        RuleMatch | None,
        RowClassification | None,
        CellTransformation | None,
        ValidationFinding | None,
    ]:
        """Evaluate one rule against one dataset row."""
        if not rule.enabled:
            return None, None, None, None

        value = row.value_for(rule.condition.field)
        operator = self._operator_registry.get(rule.condition.operator)
        if not operator.matches(value, rule.condition):
            return None, None, None, None

        message = rule.message or f"Rule matched field '{rule.condition.field}'"
        match = RuleMatch(
            rule_id=rule.rule_id,
            rule_name=rule.name,
            rule_type=rule.rule_type,
            row_number=row.source_row_number,
            field=rule.condition.field,
            original_value=value,
            confidence=rule.confidence,
            message=message,
            metadata=rule.metadata,
        )
        return (
            match,
            self._classification(row=row, rule=rule, message=message),
            self._transformation(row=row, rule=rule, value=value, message=message),
            self._validation_finding(row=row, rule=rule, message=message),
        )

    @staticmethod
    def _classification(
        *,
        row: DatasetRow,
        rule: RuleDefinition,
        message: str,
    ) -> RowClassification | None:
        if rule.rule_type != RuleType.ROW_CLASSIFICATION or rule.classification is None:
            return None
        return RowClassification(
            rule_id=rule.rule_id,
            row_number=row.source_row_number,
            classification=rule.classification,
            severity=rule.severity,
            message=message,
        )

    @staticmethod
    def _transformation(
        *,
        row: DatasetRow,
        rule: RuleDefinition,
        value: CellValue,
        message: str,
    ) -> CellTransformation | None:
        if rule.rule_type != RuleType.CELL_TRANSFORMATION:
            return None
        return CellTransformation(
            rule_id=rule.rule_id,
            row_number=row.source_row_number,
            field=rule.condition.field,
            original_value=value,
            transformed_value=rule.transform_to,
            message=message,
        )

    @staticmethod
    def _validation_finding(
        *,
        row: DatasetRow,
        rule: RuleDefinition,
        message: str,
    ) -> ValidationFinding | None:
        if rule.rule_type != RuleType.VALIDATION:
            return None
        return ValidationFinding(
            rule_id=rule.rule_id,
            row_number=row.source_row_number,
            field=rule.condition.field,
            severity=rule.severity,
            message=message,
        )
