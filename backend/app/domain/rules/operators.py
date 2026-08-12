"""Built-in rule operators."""

import re
from typing import Protocol

from app.domain.rules.models import RuleCondition, RuleOperatorName
from app.domain.workbooks.models import CellValue


class RuleOperator(Protocol):
    """Evaluates a rule condition against a scalar value."""

    name: RuleOperatorName

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        """Return whether the condition matches the value."""
        ...


class ExistsOperator:
    """Match when a value is present."""

    name = RuleOperatorName.EXISTS

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        return value is not None


class IsEmptyOperator:
    """Match when a value is absent."""

    name = RuleOperatorName.IS_EMPTY

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        return value is None


class EqualsOperator:
    """Match exact scalar values."""

    name = RuleOperatorName.EQUALS

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        return _normalize(value, condition.case_sensitive) == _normalize(
            condition.expected_value,
            condition.case_sensitive,
        )


class NotEqualsOperator:
    """Match when scalar values are not equal."""

    name = RuleOperatorName.NOT_EQUALS

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        return not EqualsOperator().matches(value, condition)


class ContainsOperator:
    """Match when a string contains another string."""

    name = RuleOperatorName.CONTAINS

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        actual = _normalize(value, condition.case_sensitive)
        expected = _normalize(condition.expected_value, condition.case_sensitive)
        return bool(expected) and expected in actual


class StartsWithOperator:
    """Match when a string starts with another string."""

    name = RuleOperatorName.STARTS_WITH

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        actual = _normalize(value, condition.case_sensitive)
        expected = _normalize(condition.expected_value, condition.case_sensitive)
        return bool(expected) and actual.startswith(expected)


class EndsWithOperator:
    """Match when a string ends with another string."""

    name = RuleOperatorName.ENDS_WITH

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        actual = _normalize(value, condition.case_sensitive)
        expected = _normalize(condition.expected_value, condition.case_sensitive)
        return bool(expected) and actual.endswith(expected)


class RegexOperator:
    """Match when a regex pattern matches a value."""

    name = RuleOperatorName.REGEX

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        pattern = _normalize_pattern(condition.expected_value)
        if not pattern:
            return False
        flags = 0 if condition.case_sensitive else re.IGNORECASE
        return re.search(pattern, _normalize(value, case_sensitive=True), flags=flags) is not None


class GreaterThanOperator:
    """Match when a numeric value is greater than expected."""

    name = RuleOperatorName.GREATER_THAN

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        actual = _to_float(value)
        expected = _to_float(condition.expected_value)
        return actual is not None and expected is not None and actual > expected


class LessThanOperator:
    """Match when a numeric value is less than expected."""

    name = RuleOperatorName.LESS_THAN

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        actual = _to_float(value)
        expected = _to_float(condition.expected_value)
        return actual is not None and expected is not None and actual < expected


class InOperator:
    """Match when a normalized value is in an expected set."""

    name = RuleOperatorName.IN

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        actual = _normalize(value, condition.case_sensitive)
        expected_values = {
            _normalize(expected_value, condition.case_sensitive)
            for expected_value in condition.expected_values
        }
        return actual in expected_values


class NotInOperator:
    """Match when a normalized value is not in an expected set."""

    name = RuleOperatorName.NOT_IN

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        return not InOperator().matches(value, condition)


class RuleOperatorRegistry:
    """Registry for built-in and future custom rule operators."""

    def __init__(self, operators: tuple[RuleOperator, ...] | None = None) -> None:
        self._operators: dict[RuleOperatorName, RuleOperator] = {}
        for operator in operators or default_operators():
            self.register(operator)

    def register(self, operator: RuleOperator) -> None:
        """Register an operator implementation."""
        self._operators[operator.name] = operator

    def get(self, name: RuleOperatorName) -> RuleOperator:
        """Return an operator by name."""
        return self._operators[name]


def default_operators() -> tuple[RuleOperator, ...]:
    """Return built-in rule operators."""
    return (
        ExistsOperator(),
        IsEmptyOperator(),
        EqualsOperator(),
        NotEqualsOperator(),
        ContainsOperator(),
        StartsWithOperator(),
        EndsWithOperator(),
        RegexOperator(),
        GreaterThanOperator(),
        LessThanOperator(),
        InOperator(),
        NotInOperator(),
    )


def _normalize(value: CellValue, case_sensitive: bool) -> str:
    if value is None:
        return ""
    normalized = " ".join(str(value).strip().split())
    return normalized if case_sensitive else normalized.casefold()


def _normalize_pattern(value: CellValue) -> str:
    if value is None:
        return ""
    return str(value)


def _to_float(value: CellValue) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
