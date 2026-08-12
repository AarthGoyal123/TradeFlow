"""Domain models for field-level data cleaning rules."""

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FieldCleaningRule:
    """Per-field cleaning rule configuration."""

    remove_phrases: tuple[str, ...] = ()
    bank_keywords: tuple[str, ...] = ()
    trim: bool = True
    collapse_whitespace: bool = True

    def apply(self, value: str) -> str:
        result = value
        if self.collapse_whitespace:
            result = " ".join(result.split())
        for phrase in self.remove_phrases:
            result = _remove_phrase(result, phrase)
        if self.bank_keywords:
            result = _strip_bank_keywords(result, self.bank_keywords)
        if self.trim:
            result = result.strip()
        return result


def _remove_phrase(text: str, phrase: str) -> str:
    lower = text.lower()
    pattern = re.compile(re.escape(phrase), re.IGNORECASE)
    result = pattern.sub("", text)
    result = " ".join(result.split())
    return result


def _strip_bank_keywords(text: str, keywords: tuple[str, ...]) -> str:
    lower = text.lower()
    tokens = text.split()
    filtered = [t for t in tokens if t.lower() not in keywords]
    result = " ".join(filtered)
    return result


@dataclass(frozen=True)
class DatasetCleaningConfig:
    """Template-level cleaning configuration keyed by business field."""

    field_rules: dict[str, FieldCleaningRule] = field(default_factory=dict)
