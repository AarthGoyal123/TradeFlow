"""Workbook validation application service with intelligent detection."""

from pathlib import Path

from app.application.workbooks.column_mapper import TemplateColumnMapper
from app.core.errors import WorkbookValidationError
from app.domain.templates.models import TemplateDefinition
from app.domain.templates.ports import TemplateRepository
from app.domain.workbooks.analyzer import WorkbookAnalyzer
from app.domain.workbooks.models import (
    WorkbookValidationIssue,
    WorkbookValidationResult,
)
from app.domain.workbooks.ports import WorkbookDocument, WorkbookLoader, WorksheetReader
from app.domain.workbooks.semantic_detector import SemanticDetector
from app.domain.workbooks.synonyms import GlobalSynonymDictionary, IndustrySynonymDictionary


class WorkbookValidationService:
    """Validate workbook structure against a processing template with intelligence."""

    def __init__(
        self,
        *,
        template_repository: TemplateRepository,
        workbook_loader: WorkbookLoader,
        column_mapper: TemplateColumnMapper,
        global_dict: GlobalSynonymDictionary | None = None,
        industry_dict: IndustrySynonymDictionary | None = None,
    ) -> None:
        self._template_repository = template_repository
        self._workbook_loader = workbook_loader
        self._column_mapper = column_mapper
        gd = global_dict or GlobalSynonymDictionary()
        self._analyzer = WorkbookAnalyzer()
        self._semantic = SemanticDetector(gd)

    def validate(self, *, template_id: str, workbook_path: Path) -> WorkbookValidationResult:
        """Validate workbook with intelligent structure analysis and column detection."""
        template = self._template_repository.get_template(template_id)
        try:
            workbook = self._workbook_loader.load(workbook_path)
        except WorkbookValidationError as exc:
            return WorkbookValidationResult(
                template_id=template_id,
                workbook_path=workbook_path,
                valid=False,
                sheet_name=None,
                available_sheets=(),
                header=None,
                mapped_columns=(),
                issues=(
                    WorkbookValidationIssue(
                        code=exc.code, message=exc.message, details=exc.details,
                    ),
                ),
            )

        sheet, sheet_issue = self._select_sheet(template=template, workbook=workbook)
        if sheet is None:
            if sheet_issue is None:
                raise WorkbookValidationError("Workbook sheet selection failed unexpectedly")
            return WorkbookValidationResult(
                template_id=template_id,
                workbook_path=workbook_path,
                valid=False,
                sheet_name=None,
                available_sheets=workbook.sheet_names,
                header=None,
                mapped_columns=(),
                issues=(sheet_issue,),
            )

        header = sheet.read_header()

        # Run intelligent analysis
        structure = self._analyzer.analyze(workbook)
        semantic = self._semantic.analyze(sheet, structure.header.detected_row)

        # Use enhanced column mapper with global synonyms
        mapped_columns, issues = self._column_mapper.map_columns(
            template=template, header=header,
        )

        # Attach intelligence context to every issue
        enriched = tuple(
            self._enrich_issue(issue, structure, semantic, template)
            for issue in issues
        )

        return WorkbookValidationResult(
            template_id=template_id,
            workbook_path=workbook_path,
            valid=not enriched,
            sheet_name=sheet.name,
            available_sheets=workbook.sheet_names,
            header=header,
            mapped_columns=mapped_columns,
            issues=enriched,
        )

    def _enrich_issue(
        self,
        issue: WorkbookValidationIssue,
        structure: "StructureAnalysis",
        semantic: "SemanticAnalysis",
        template: TemplateDefinition,
    ) -> WorkbookValidationIssue:
        details = dict(issue.details)
        details["intelligence"] = {
            "detected_header_row": structure.header.detected_row,
            "header_confidence": structure.header.confidence,
            "structure_confidence": structure.structure_confidence,
        }
        return WorkbookValidationIssue(code=issue.code, message=issue.message, details=details)

    @staticmethod
    def _select_sheet(
        *,
        template: TemplateDefinition,
        workbook: WorkbookDocument,
    ) -> tuple[WorksheetReader | None, WorkbookValidationIssue | None]:
        workbook_config = template.config.workbook
        if workbook_config.sheet_strategy == "first_sheet":
            try:
                return workbook.first_sheet(), None
            except WorkbookValidationError as exc:
                return None, WorkbookValidationIssue(
                    code=exc.code, message=exc.message, details=exc.details,
                )

        sheet_name = workbook_config.sheet_name
        if sheet_name is None:
            return None, WorkbookValidationIssue(
                code="missing_sheet_name",
                message="Template requires a named sheet but no sheet name is configured",
                details={"template_id": template.id},
            )
        sheet = workbook.sheet_by_name(sheet_name)
        if sheet is None:
            return None, WorkbookValidationIssue(
                code="required_sheet_missing",
                message=f"Required worksheet '{sheet_name}' was not found",
                details={"required_sheet": sheet_name, "available_sheets": workbook.sheet_names},
            )
        return sheet, None