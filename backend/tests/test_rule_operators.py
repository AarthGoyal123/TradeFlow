from app.domain.rules.models import RuleCondition, RuleOperatorName
from app.domain.rules.operators import RuleOperatorRegistry
from app.infrastructure.rules.rapidfuzz_operator import RapidFuzzEqualsOperator


def test_builtin_rule_operators_match_expected_values() -> None:
    registry = RuleOperatorRegistry()

    assert registry.get(RuleOperatorName.EXISTS).matches(
        "value",
        RuleCondition(field="field", operator=RuleOperatorName.EXISTS),
    )
    assert registry.get(RuleOperatorName.IS_EMPTY).matches(
        None,
        RuleCondition(field="field", operator=RuleOperatorName.IS_EMPTY),
    )
    assert registry.get(RuleOperatorName.EQUALS).matches(
        " Acme  Exports ",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.EQUALS,
            expected_value="acme exports",
        ),
    )
    assert registry.get(RuleOperatorName.CONTAINS).matches(
        "State Bank of India",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.CONTAINS,
            expected_value="bank",
        ),
    )
    assert registry.get(RuleOperatorName.STARTS_WITH).matches(
        "TO ORDER",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.STARTS_WITH,
            expected_value="to",
        ),
    )
    assert registry.get(RuleOperatorName.ENDS_WITH).matches(
        "MAERSK LINE",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.ENDS_WITH,
            expected_value="line",
        ),
    )
    assert registry.get(RuleOperatorName.NOT_EQUALS).matches(
        "ACME",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.NOT_EQUALS,
            expected_value="OTHER",
        ),
    )
    assert registry.get(RuleOperatorName.REGEX).matches(
        "TO THE ORDER",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.REGEX,
            expected_value=r"to\s+the\s+order",
        ),
    )
    assert registry.get(RuleOperatorName.GREATER_THAN).matches(
        10,
        RuleCondition(field="field", operator=RuleOperatorName.GREATER_THAN, expected_value=9),
    )
    assert registry.get(RuleOperatorName.LESS_THAN).matches(
        "8",
        RuleCondition(field="field", operator=RuleOperatorName.LESS_THAN, expected_value=9),
    )
    assert registry.get(RuleOperatorName.IN).matches(
        "MUNDRA",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.IN,
            expected_values=("mundra", "nhava sheva"),
        ),
    )
    assert registry.get(RuleOperatorName.NOT_IN).matches(
        "UNKNOWN",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.NOT_IN,
            expected_values=("mundra", "nhava sheva"),
        ),
    )
    registry.register(RapidFuzzEqualsOperator())
    assert registry.get(RuleOperatorName.FUZZY_EQUALS).matches(
        "MAERSK LINE",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.FUZZY_EQUALS,
            expected_value="MAERSK LINES",
            threshold=90,
        ),
    )


def test_case_sensitive_operator_does_not_casefold() -> None:
    registry = RuleOperatorRegistry()

    assert not registry.get(RuleOperatorName.EQUALS).matches(
        "ACME",
        RuleCondition(
            field="field",
            operator=RuleOperatorName.EQUALS,
            expected_value="acme",
            case_sensitive=True,
        ),
    )
