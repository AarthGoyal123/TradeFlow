"""Intelligent column mapper with layered matching."""

from dataclasses import dataclass, field

from rapidfuzz import fuzz, process

from app.domain.templates.models import ColumnMapping, TemplateDefinition
from app.domain.workbooks.models import (
    HeaderCell,
    MappedColumn,
    WorkbookValidationIssue,
    WorksheetHeader,
)
from app.domain.workbooks.synonyms import GlobalSynonymDictionary, IndustrySynonymDictionary

AUTO_MAP_THRESHOLD = 0.95
SUGGEST_THRESHOLD = 0.85


class TemplateColumnMapper:
    """Map template conceptual columns to worksheet headers using layered matching.

    Matching hierarchy:
        1. Exact match
        2. Case-insensitive match
        3. Normalized match (ignoring spaces, underscores, hyphens, periods)
        4. Synonym match (global trade dictionary)
        5. Fuzzy match (RapidFuzz with configurable threshold)
    """

    def __init__(
        self,
        *,
        global_dict: GlobalSynonymDictionary | None = None,
        industry_dict: IndustrySynonymDictionary | None = None,
    ) -> None:
        self._global_dict = global_dict or GlobalSynonymDictionary()
        self._industry_dict = industry_dict or IndustrySynonymDictionary(self._global_dict)

    def map_columns(
        self,
        *,
        template: TemplateDefinition,
        header: WorksheetHeader,
    ) -> tuple[tuple[MappedColumn, ...], tuple[WorkbookValidationIssue, ...]]:
        """Resolve required and optional template fields against a worksheet header."""
        header_lookup = self._build_lookup(header)
        all_header_values = list(header_lookup.keys())

        mapped: list[MappedColumn] = []
        issues: list[WorkbookValidationIssue] = []

        for column in template.columns.required_fields:
            result = self._map_field(column, header_lookup, all_header_values, required=True)
            if result.mapped_column:
                mapped.append(result.mapped_column)
            else:
                issues.append(self._build_issue(column, result, required=True))

        for column in template.columns.optional_fields:
            result = self._map_field(column, header_lookup, all_header_values, required=False)
            if result.mapped_column:
                mapped.append(result.mapped_column)
            else:
                issues.append(self._build_issue(column, result, required=False))

        return tuple(mapped), tuple(issues)

    def _build_lookup(self, header: WorksheetHeader) -> dict[str, HeaderCell]:
        lookup: dict[str, HeaderCell] = {}
        for c in header.cells:
            if not c.value:
                continue
            lookup[c.value] = c
            normal = self._normalize(c.value)
            if normal != c.value:
                lookup.setdefault(normal, c)
        return lookup

    def _map_field(
        self,
        column: ColumnMapping,
        lookup: dict[str, HeaderCell],
        all_values: list[str],
        *,
        required: bool,
    ) -> "_FieldResult":
        field = column.field
        template_aliases = column.aliases

        # Stage 1: Exact match
        for alias in template_aliases:
            if alias in lookup:
                cell = lookup[alias]
                mc = MappedColumn(
                    field=field,
                    required=required,
                    source_header=cell.value,
                    column_number=cell.column_number,
                    confidence=1.0,
                )
                return _FieldResult(mc, 1.0, "exact")

        # Stage 2: Case-insensitive / Normalized match on template aliases
        for alias in template_aliases:
            normal = self._normalize(alias)
            if normal in lookup:
                cell = lookup[normal]
                mc = MappedColumn(
                    field=field,
                    required=required,
                    source_header=cell.value,
                    column_number=cell.column_number,
                    confidence=0.90,
                )
                return _FieldResult(mc, 0.90, "normalized")

        # Stage 3: Synonym dictionary match
        all_synonyms = self._industry_dict.get_all(field)
        for synonym in all_synonyms:
            if synonym in lookup:
                cell = lookup[synonym]
                mc = MappedColumn(
                    field=field,
                    required=required,
                    source_header=cell.value,
                    column_number=cell.column_number,
                    confidence=0.85,
                )
                return _FieldResult(mc, 0.85, "synonym")
            normal = self._normalize(synonym)
            if normal in lookup:
                cell = lookup[normal]
                mc = MappedColumn(
                    field=field,
                    required=required,
                    source_header=cell.value,
                    column_number=cell.column_number,
                    confidence=0.82,
                )
                return _FieldResult(mc, 0.82, "synonym")

        # Stage 4: Fuzzy match with auto-map threshold
        all_searched = list(template_aliases)
        for s in all_synonyms:
            if s not in all_searched:
                all_searched.append(s)

        best_cell: HeaderCell | None = None
        best_score = 0.0

        for alias in all_searched:
            result = process.extractOne(
                alias, all_values, scorer=fuzz.WRatio, score_cutoff=int(SUGGEST_THRESHOLD * 100)
            )
            if result:
                value, score, _ = result
                normalized_score = score / 100.0
                if normalized_score >= AUTO_MAP_THRESHOLD and lookup.get(value):
                    cell = lookup[value]
                    mc = MappedColumn(
                        field=field,
                        required=required,
                        source_header=cell.value,
                        column_number=cell.column_number,
                        confidence=normalized_score,
                    )
                    return _FieldResult(mc, normalized_score, "fuzzy_auto")
                if normalized_score > best_score and lookup.get(value):
                    best_score = normalized_score
                    best_cell = lookup[value]

        # Return best fuzzy match if above suggestion threshold
        if best_cell and best_score >= SUGGEST_THRESHOLD:
            mc = MappedColumn(
                field=field,
                required=required,
                source_header=best_cell.value,
                column_number=best_cell.column_number,
                confidence=best_score,
            )
            return _FieldResult(mc, best_score, "fuzzy_suggest")

        return _FieldResult(
            None,
            0.0,
            "none",
            suggestions=[
                (value, score / 100.0)
                for result in [
                    process.extract(a, all_values, scorer=fuzz.WRatio, limit=2)
                    for a in all_searched[:5]
                ]
                for value, score, _ in (result or [])
                if score / 100.0 >= SUGGEST_THRESHOLD - 0.1
            ],
        )

    def _build_issue(
        self, column: ColumnMapping, result: "_FieldResult", required: bool
    ) -> WorkbookValidationIssue:
        all_synonyms = self._industry_dict.get_all(column.field)

        if required:
            code = "missing_required_column"
            if result.suggestions:
                msg = f"Missing required field '{column.field}'. Closest match: {result.suggestions[0][0]} ({result.suggestions[0][1]:.0%})"  # noqa: E501
            else:
                msg = f"Missing required field '{column.field}'"
        else:
            code = "missing_optional_column"
            msg = f"Optional field '{column.field}' not found"

        details: dict[str, object] = {
            "field": column.field,
            "required": required,
            "searched_aliases": column.aliases,
            "all_synonyms": all_synonyms,
            "closest_matches": [{"value": v, "confidence": c} for v, c in result.suggestions],
            "confidence": result.confidence,
            "detection_method": result.method,
        }

        if result.suggestions:
            best = result.suggestions[0]
            details["recommended_fix"] = (
                f"Rename or map '{best[0]}' to '{column.field}' (confidence: {best[1]:.0%}). "
            )
            details["suggested_mapping"] = {
                "workbook_header": best[0],
                "business_field": column.field,
            }
        else:
            details["recommended_fix"] = (
                f"Add a column named one of: {', '.join(column.aliases[:3])}"
            )

        issue_details: dict[str, object] = {
            "problem": f"Missing {'required' if required else 'optional'} field '{column.field}'",
            "reason": f"No column in the workbook matches '{column.field}' or its known aliases",
            "searched_aliases": column.aliases,
            "closest_matches": details["closest_matches"],
            "confidence": result.confidence,
            "suggested_fix": details["recommended_fix"],
            "field": column.field,
            "required": required,
            "all_synonyms": all_synonyms,
            "detection_method": result.method,
        }

        return WorkbookValidationIssue(code=code, message=msg, details=issue_details)

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(
            value.strip().casefold().replace("_", " ").replace("-", " ").replace(".", " ").split()
        )


@dataclass
class _FieldResult:
    mapped_column: MappedColumn | None
    confidence: float
    method: str
    suggestions: list[tuple[str, float]] = field(default_factory=list)
