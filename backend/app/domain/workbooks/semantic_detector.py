"""Semantic Detector — inspects sample cell values to identify data types."""

from typing import Any

from app.domain.workbooks.intelligence import BusinessEntity, DetectedPattern, SemanticAnalysis
from app.domain.workbooks.ports import WorksheetReader
from app.domain.workbooks.synonyms import (
    COMMON_COUNTRY_NAMES,
    COMMON_CURRENCY_SYMBOLS,
    COMMON_HS_CODE_PREFIXES,
    COMMON_PORT_NAMES,
    GlobalSynonymDictionary,
)

_SAMPLE_LIMIT = 100


class SemanticDetector:
    """Analyze cell values to understand what data each column contains."""

    def __init__(self, global_dict: GlobalSynonymDictionary) -> None:
        self._global_dict = global_dict

    def analyze(self, worksheet: WorksheetReader, header_row: int) -> SemanticAnalysis:
        header = worksheet.read_header(header_row)
        sample = list(worksheet.iter_rows(min_row=header_row + 1))[:_SAMPLE_LIMIT]

        entities: list[BusinessEntity] = []
        patterns: list[DetectedPattern] = []
        has_country = has_hs = has_port = has_currency = False

        for cell in header.cells:
            col_values = self._collect_column(sample, cell.column_number)
            pattern = self._detect_pattern(cell.value, col_values)
            patterns.append(pattern)

            if pattern.pattern_type == "country":
                has_country = True
                entities.append(
                    BusinessEntity(
                        business_concept="country",
                        workbook_header=cell.value,
                        detection_method="semantic",
                        confidence=pattern.confidence,
                        sample_values=pattern.sample_values,
                    )
                )
            elif pattern.pattern_type == "hs_code":
                has_hs = True
                entities.append(
                    BusinessEntity(
                        business_concept="hs_code",
                        workbook_header=cell.value,
                        detection_method="semantic",
                        confidence=pattern.confidence,
                        sample_values=pattern.sample_values,
                    )
                )
            elif pattern.pattern_type == "port":
                has_port = True
                entities.append(
                    BusinessEntity(
                        business_concept="port",
                        workbook_header=cell.value,
                        detection_method="semantic",
                        confidence=pattern.confidence,
                        sample_values=pattern.sample_values,
                    )
                )
            elif pattern.pattern_type == "currency":
                has_currency = True
                entities.append(
                    BusinessEntity(
                        business_concept="fob_value",
                        workbook_header=cell.value,
                        detection_method="semantic",
                        confidence=pattern.confidence,
                        sample_values=pattern.sample_values,
                    )
                )

        return SemanticAnalysis(
            detected_entities=tuple(entities),
            detected_patterns=tuple(patterns),
            has_country_data=has_country,
            has_hs_code_data=has_hs,
            has_port_data=has_port,
            has_currency_data=has_currency,
        )

    def _collect_column(self, rows: list[Any], col_number: int) -> list[str]:
        result: list[str] = []
        for r in rows:
            if r.values and col_number <= len(r.values):
                v = r.values[col_number - 1]
                if v is not None and str(v).strip():
                    result.append(str(v).strip())
        return result

    def _detect_pattern(self, header_name: str, values: list[str]) -> DetectedPattern:
        if not values:
            return DetectedPattern("unknown", header_name, (), 0.0)

        # Check for currency values
        currency_matches = sum(
            1 for v in values if any(v.startswith(s) for s in COMMON_CURRENCY_SYMBOLS)
        )
        if currency_matches > len(values) * 0.3:
            return DetectedPattern(
                "currency",
                header_name,
                tuple(values[:5]),
                min(0.95, currency_matches / len(values)),
            )

        # Check for HS codes (6-8 digit numbers, optionally with dots/hyphens)
        hs_matches = 0
        for v in values:
            cleaned = v.replace("-", "").replace(".", "").replace("/", "")
            if cleaned.isdigit() and 4 <= len(cleaned) <= 10:
                hs_matches += 1
                continue
            if any(v.startswith(p) for p in COMMON_HS_CODE_PREFIXES):
                hs_matches += 1
        if hs_matches > len(values) * 0.3:
            return DetectedPattern(
                "hs_code",
                header_name,
                tuple(values[:5]),
                min(0.95, hs_matches / len(values)),
            )

        # Check for country names
        country_matches = sum(
            1 for v in values if v.strip().title() in {c.title() for c in COMMON_COUNTRY_NAMES}
        )
        if country_matches > len(values) * 0.3:
            return DetectedPattern(
                "country",
                header_name,
                tuple(values[:5]),
                min(0.95, country_matches / len(values)),
            )

        # Check for port names
        port_matches = sum(
            1 for v in values if v.strip().title() in {p.title() for p in COMMON_PORT_NAMES}
        )
        if port_matches > len(values) * 0.3:
            return DetectedPattern(
                "port",
                header_name,
                tuple(values[:5]),
                min(0.85, port_matches / len(values)),
            )

        # Check for numeric values
        numeric_matches = sum(1 for v in values if _is_numeric(v))
        if numeric_matches > len(values) * 0.6:
            return DetectedPattern(
                "numeric",
                header_name,
                tuple(values[:5]),
                min(0.7, numeric_matches / len(values)),
            )

        # Check for date-like values
        date_matches = sum(1 for v in values if _looks_like_date(v))
        if date_matches > len(values) * 0.4:
            return DetectedPattern(
                "date",
                header_name,
                tuple(values[:5]),
                min(0.75, date_matches / len(values)),
            )

        return DetectedPattern("text", header_name, tuple(values[:3]), 0.5)


def _is_numeric(v: str) -> bool:
    try:
        float(v.replace(",", ""))
        return True
    except ValueError:
        return False


def _looks_like_date(v: str) -> bool:
    import re

    patterns = [r"\d{2}[/-]\d{2}[/-]\d{2,4}", r"\d{4}[/-]\d{2}[/-]\d{2}"]
    return bool(re.match(patterns[0], v)) or bool(re.match(patterns[1], v))
