import json
from pathlib import Path

import pytest

from app.core.errors import RulePackValidationError
from app.domain.rules.models import RuleOperatorName, RuleType
from app.infrastructure.rules.filesystem import FileSystemRulePackRepository
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository


def test_filesystem_rule_pack_repository_loads_typed_rules(tmp_path) -> None:
    template_root = _copy_template(tmp_path)
    _write_rule_pack(
        template_root,
        "custom.json",
        {
            "pack_id": "custom",
            "name": "Custom rules",
            "version": "1.2.0",
            "enabled": True,
            "rules": [
                {
                    "rule_id": "bank_rule",
                    "name": "Bank rule",
                    "rule_type": "row_classification",
                    "condition": {
                        "field": "consignee_name",
                        "operator": "contains",
                        "expected_value": "bank",
                    },
                    "classification": "bank",
                    "severity": "warning",
                    "priority": 10,
                    "message": "Bank detected",
                }
            ],
        },
    )

    repository = _repository(template_root)
    rule_packs = repository.list_rule_packs("indian_rice_exports")

    custom_pack = next(pack for pack in rule_packs if pack.pack_id == "custom")
    assert custom_pack.version == "1.2.0"
    assert custom_pack.rules[0].rule_id == "bank_rule"
    assert custom_pack.rules[0].rule_type == RuleType.ROW_CLASSIFICATION
    assert custom_pack.rules[0].condition.operator == RuleOperatorName.CONTAINS


def test_filesystem_rule_pack_repository_rejects_invalid_operator(tmp_path) -> None:
    template_root = _copy_template(tmp_path)
    _write_rule_pack(
        template_root,
        "invalid_operator.json",
        {
            "rules": [
                {
                    "rule_id": "bad",
                    "name": "Bad",
                    "rule_type": "validation",
                    "condition": {"field": "port", "operator": "unknown"},
                }
            ]
        },
    )

    with pytest.raises(RulePackValidationError) as exc:
        _repository(template_root).list_rule_packs("indian_rice_exports")

    assert exc.value.code == "rule_pack_validation_error"


def test_filesystem_rule_pack_repository_rejects_duplicate_rule_ids(tmp_path) -> None:
    template_root = _copy_template(tmp_path)
    _write_rule_pack(
        template_root,
        "duplicate.json",
        {
            "rules": [
                {
                    "rule_id": "duplicate",
                    "name": "One",
                    "rule_type": "validation",
                    "condition": {"field": "port", "operator": "is_empty"},
                },
                {
                    "rule_id": "duplicate",
                    "name": "Two",
                    "rule_type": "validation",
                    "condition": {"field": "port", "operator": "exists"},
                },
            ]
        },
    )

    with pytest.raises(RulePackValidationError) as exc:
        _repository(template_root).list_rule_packs("indian_rice_exports")

    assert exc.value.details["rule_id"] == "duplicate"


def test_filesystem_rule_pack_repository_rejects_unknown_template_field(tmp_path) -> None:
    template_root = _copy_template(tmp_path)
    _write_rule_pack(
        template_root,
        "unknown_field.json",
        {
            "rules": [
                {
                    "rule_id": "unknown",
                    "name": "Unknown",
                    "rule_type": "validation",
                    "condition": {"field": "not_a_field", "operator": "exists"},
                }
            ]
        },
    )

    with pytest.raises(RulePackValidationError) as exc:
        _repository(template_root).list_rule_packs("indian_rice_exports")

    assert exc.value.details["field"] == "not_a_field"


def test_filesystem_rule_pack_repository_rejects_invalid_regex(tmp_path) -> None:
    template_root = _copy_template(tmp_path)
    _write_rule_pack(
        template_root,
        "bad_regex.json",
        {
            "rules": [
                {
                    "rule_id": "bad_regex",
                    "name": "Bad regex",
                    "rule_type": "validation",
                    "condition": {
                        "field": "port",
                        "operator": "regex",
                        "expected_value": "[",
                    },
                }
            ]
        },
    )

    with pytest.raises(RulePackValidationError) as exc:
        _repository(template_root).list_rule_packs("indian_rice_exports")

    assert exc.value.details["rule_id"] == "bad_regex"


def _repository(template_root: Path) -> FileSystemRulePackRepository:
    template_repository = FileSystemTemplateRepository(template_root)
    return FileSystemRulePackRepository(
        template_root=template_root,
        template_repository=template_repository,
    )


def _copy_template(tmp_path) -> Path:
    source_root = Path("../templates/indian_rice_exports")
    template_root = tmp_path / "templates"
    target_root = template_root / "indian_rice_exports"
    rules_dir = target_root / "rules"
    rules_dir.mkdir(parents=True)
    for filename in ["config.json", "columns.json", "pipeline.json", "output.json"]:
        (target_root / filename).write_text(
            (source_root / filename).read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    return template_root


def _write_rule_pack(template_root: Path, filename: str, payload: dict[str, object]) -> None:
    path = template_root / "indian_rice_exports" / "rules" / filename
    path.write_text(json.dumps(payload), encoding="utf-8")
