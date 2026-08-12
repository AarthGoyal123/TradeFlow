"""Rule evaluation pipeline over intermediate datasets."""

from app.application.rules.routing import RuleConflictResolver
from app.domain.datasets.models import IntermediateDataset
from app.domain.rules.evaluator import RuleEvaluator
from app.domain.rules.models import (
    CellTransformation,
    RowClassification,
    RuleDefinition,
    RuleExecutionReport,
    RuleMatch,
    ValidationFinding,
)
from app.domain.rules.ports import RulePackRepository


class RuleEvaluationService:
    """Evaluate typed rules over an intermediate dataset."""

    def __init__(
        self,
        *,
        rule_evaluator: RuleEvaluator | None = None,
        rule_pack_repository: RulePackRepository | None = None,
        conflict_resolver: RuleConflictResolver | None = None,
    ) -> None:
        self._rule_evaluator = rule_evaluator or RuleEvaluator()
        self._rule_pack_repository = rule_pack_repository
        self._conflict_resolver = conflict_resolver or RuleConflictResolver()

    def evaluate(
        self,
        *,
        dataset: IntermediateDataset,
        rules: tuple[RuleDefinition, ...],
        review_threshold: float = 0.75,
    ) -> RuleExecutionReport:
        """Evaluate enabled rules in deterministic priority order."""
        ordered_rules = tuple(
            sorted(
                (rule for rule in rules if rule.enabled),
                key=lambda rule: (rule.priority, rule.rule_id),
            )
        )
        matches: list[RuleMatch] = []
        classifications: list[RowClassification] = []
        transformations: list[CellTransformation] = []
        validation_findings: list[ValidationFinding] = []

        for row in dataset.rows:
            for rule in ordered_rules:
                match, classification, transformation, validation_finding = (
                    self._rule_evaluator.evaluate_row(row=row, rule=rule)
                )
                if match is not None:
                    matches.append(match)
                if classification is not None:
                    classifications.append(classification)
                if transformation is not None:
                    transformations.append(transformation)
                if validation_finding is not None:
                    validation_findings.append(validation_finding)

        report = RuleExecutionReport(
            template_id=dataset.template_id,
            row_count=dataset.row_count,
            rules_evaluated=len(ordered_rules),
            matches=tuple(matches),
            classifications=tuple(classifications),
            transformations=tuple(transformations),
            validation_findings=tuple(validation_findings),
        )
        return RuleExecutionReport(
            template_id=report.template_id,
            row_count=report.row_count,
            rules_evaluated=report.rules_evaluated,
            matches=report.matches,
            classifications=report.classifications,
            transformations=report.transformations,
            validation_findings=report.validation_findings,
            routed_rows=self._conflict_resolver.resolve(
                dataset=dataset, report=report, review_threshold=review_threshold
            ),
        )

    def evaluate_template_rules(
        self, *, dataset: IntermediateDataset, review_threshold: float = 0.75
    ) -> RuleExecutionReport:
        """Load enabled template rule packs and evaluate their rules."""
        if self._rule_pack_repository is None:
            raise ValueError("rule_pack_repository is required to load template rules")
        rule_packs = self._rule_pack_repository.list_rule_packs(dataset.template_id)
        rules = tuple(
            rule for rule_pack in rule_packs if rule_pack.enabled for rule in rule_pack.rules
        )
        return self.evaluate(dataset=dataset, rules=rules, review_threshold=review_threshold)
