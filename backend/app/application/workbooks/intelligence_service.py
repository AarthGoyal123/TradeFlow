"""Workbook Intelligence Service — orchestrates analysis into a unified report."""

from pathlib import Path

from rapidfuzz import fuzz, process

from app.application.workbooks.column_mapper import TemplateColumnMapper
from app.domain.templates.models import TemplateDefinition
from app.domain.workbooks.analyzer import WorkbookAnalyzer
from app.domain.workbooks.intelligence import (
    ColumnMappingExplanation,
    ConfidenceReport,
    DetectedFieldInfo,
    SemanticAnalysis,
    StructureAnalysis,
    WorkbookIntelligenceReport,
)
from app.domain.workbooks.models import WorksheetHeader
from app.domain.workbooks.ports import WorkbookDocument, WorkbookLoader, WorksheetReader
from app.domain.workbooks.semantic_detector import SemanticDetector
from app.domain.workbooks.synonyms import GlobalSynonymDictionary


class WorkbookIntelligenceService:
    """Produce a complete intelligence report for any workbook."""

    def __init__(
        self,
        *,
        workbook_loader: WorkbookLoader,
        column_mapper: TemplateColumnMapper,
        global_dict: GlobalSynonymDictionary | None = None,
    ) -> None:
        self._workbook_loader = workbook_loader
        self._column_mapper = column_mapper
        gd = global_dict or GlobalSynonymDictionary()
        self._analyzer = WorkbookAnalyzer()
        self._semantic = SemanticDetector(gd)

    def analyze(
        self,
        *,
        workbook_path: Path,
        template: TemplateDefinition | None = None,
    ) -> WorkbookIntelligenceReport:
        workbook = self._workbook_loader.load(workbook_path)
        structure = self._analyzer.analyze(workbook)

        sheet = self._select_sheet(workbook)
        if sheet is None:
            return WorkbookIntelligenceReport(
                structure=structure,
                sheets=workbook.sheet_names,
            )

        header = sheet.read_header()
        header_row = structure.header.detected_row if structure.header.detected_row > 0 else 1
        semantic = self._semantic.analyze(sheet, header_row)

        extracted = self._extract_detected_fields(semantic)
        semantic_with_fields = SemanticAnalysis(
            detected_entities=semantic.detected_entities,
            detected_patterns=semantic.detected_patterns,
            has_country_data=semantic.has_country_data,
            has_hs_code_data=semantic.has_hs_code_data,
            has_port_data=semantic.has_port_data,
            has_currency_data=semantic.has_currency_data,
            total_fields_detected=len(extracted),
            fields=extracted,
        )

        explanations: tuple[ColumnMappingExplanation, ...] = ()
        if template is not None and header is not None:
            explanations = self._build_column_explanations(template, header)

        overall = self._compute_overall_confidence(structure, explanations)

        detected_cols = tuple(c.value for c in header.cells if c.value)

        return WorkbookIntelligenceReport(
            structure=structure,
            semantic=semantic_with_fields,
            mapping_explanations=explanations,
            confidence=overall,
            sheets=workbook.sheet_names,
            raw_header=detected_cols,
            detected_columns=detected_cols,
        )

    def _build_column_explanations(
        self,
        template: TemplateDefinition,
        header: WorksheetHeader,
    ) -> tuple[ColumnMappingExplanation, ...]:
        explanations: list[ColumnMappingExplanation] = []
        all_mappings = [(c, True) for c in template.columns.required_fields] + [
            (c, False) for c in template.columns.optional_fields
        ]
        for column, required in all_mappings:
            explanation = self._explain_column(column.field, column.aliases, header, required)
            explanations.append(explanation)
        return tuple(explanations)

    def _explain_column(
        self,
        field: str,
        template_aliases: list[str],
        header: WorksheetHeader,
        required: bool,
    ) -> ColumnMappingExplanation:
        header_values = [c.value for c in header.cells if c.value]

        for alias in template_aliases:
            if alias in header_values:
                cell = next(c for c in header.cells if c.value == alias)
                return ColumnMappingExplanation(
                    field=field,
                    required=required,
                    matched=True,
                    source_header=alias,
                    column_number=cell.column_number,
                    method="exact",
                    confidence=1.0,
                    searched_aliases=tuple(template_aliases),
                )

        normalized_lookup = {self._normalize(v): v for v in header_values}
        for alias in template_aliases:
            normal = self._normalize(alias)
            if normal in normalized_lookup:
                orig = normalized_lookup[normal]
                cell = next(c for c in header.cells if c.value == orig)
                return ColumnMappingExplanation(
                    field=field,
                    required=required,
                    matched=True,
                    source_header=orig,
                    column_number=cell.column_number,
                    method="normalized",
                    confidence=0.90,
                    searched_aliases=tuple(template_aliases),
                )

        closest: list[tuple[str, float]] = []
        for alias in template_aliases:
            result = process.extractOne(alias, header_values, scorer=fuzz.WRatio, score_cutoff=75)
            if result:
                value, score, _ = result
                normalized = score / 100.0
                closest.append((value, normalized))
                if normalized >= 0.85:
                    cell = next(c for c in header.cells if c.value == value)
                    method = "fuzzy_auto" if normalized >= 0.95 else "fuzzy"
                    return ColumnMappingExplanation(
                        field=field,
                        required=required,
                        matched=True,
                        source_header=value,
                        column_number=cell.column_number,
                        method=method,
                        confidence=normalized,
                        searched_aliases=tuple(template_aliases),
                        closest_matches=tuple(
                            {"value": v, "confidence": c}
                            for v, c in sorted(closest, key=lambda x: -x[1])[:3]
                        ),
                    )

        sorted_closest = sorted(closest, key=lambda x: -x[1])[:3]
        return ColumnMappingExplanation(
            field=field,
            required=required,
            matched=False,
            method="none",
            confidence=0.0,
            searched_aliases=tuple(template_aliases),
            closest_matches=tuple({"value": v, "confidence": c} for v, c in sorted_closest),
        )

    @staticmethod
    def _compute_overall_confidence(
        structure: "StructureAnalysis",
        explanations: tuple[ColumnMappingExplanation, ...],
    ) -> ConfidenceReport:
        scores = [structure.structure_confidence] if structure.structure_confidence > 0 else []
        for exp in explanations:
            if exp.matched:
                scores.append(exp.confidence)
        overall = sum(scores) / len(scores) if scores else 0.0
        mapped = sum(1 for e in explanations if e.matched)
        total = len(explanations) if explanations else 1

        return ConfidenceReport(
            overall=overall,
            structure_confidence=structure.structure_confidence,
            header_confidence=structure.header.confidence,
            mapping_confidence=overall,
            mapping_coverage=mapped / total if total > 0 else 0.0,
        )

    @staticmethod
    def _extract_detected_fields(semantic: SemanticAnalysis) -> tuple[DetectedFieldInfo, ...]:
        fields: list[DetectedFieldInfo] = []
        for pattern in semantic.detected_patterns:
            if pattern.pattern_type not in ("unknown", "text") and pattern.confidence > 0.5:
                sample = pattern.sample_values[0] if pattern.sample_values else ""
                reason = {
                    "country": "Values match known country names",
                    "hs_code": "Values match HS code patterns (6-10 digit numeric codes)",
                    "port": "Values match known port names",
                    "currency": "Values start with currency symbols ($, €, etc.)",
                    "numeric": "Values are numeric",
                    "date": "Values match date patterns",
                }.get(pattern.pattern_type, f"Detected as {pattern.pattern_type}")
                fields.append(
                    DetectedFieldInfo(
                        label=pattern.pattern_type,
                        column=0,
                        sample=sample,
                        confidence=pattern.confidence,
                        reason=reason,
                    )
                )
        return tuple(fields)

    @staticmethod
    def _normalize(value: str) -> str:
        return " ".join(
            value.strip().casefold().replace("_", " ").replace("-", " ").replace(".", " ").split()
        )

    @staticmethod
    def _select_sheet(workbook: WorkbookDocument) -> WorksheetReader | None:
        try:
            return workbook.first_sheet()
        except Exception:
            return None
