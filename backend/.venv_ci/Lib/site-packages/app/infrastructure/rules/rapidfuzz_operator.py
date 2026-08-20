"""RapidFuzz-backed rule operators."""

from rapidfuzz import fuzz

from app.domain.rules.models import RuleCondition, RuleOperatorName
from app.domain.workbooks.models import CellValue


class RapidFuzzEqualsOperator:
    """Match when RapidFuzz similarity reaches the configured threshold."""

    name = RuleOperatorName.FUZZY_EQUALS

    def matches(self, value: CellValue, condition: RuleCondition) -> bool:
        """Return whether normalized values meet the similarity threshold."""
        threshold = condition.threshold if condition.threshold is not None else 90.0
        actual = _normalize(value, condition.case_sensitive)
        expected = _normalize(condition.expected_value, condition.case_sensitive)
        if not actual or not expected:
            return False
        return fuzz.ratio(actual, expected) >= threshold


def _normalize(value: CellValue, case_sensitive: bool) -> str:
    if value is None:
        return ""
    normalized = " ".join(str(value).strip().split())
    return normalized if case_sensitive else normalized.casefold()
