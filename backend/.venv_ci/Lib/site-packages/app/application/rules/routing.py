"""Rule conflict resolution and row routing."""

from app.domain.datasets.models import IntermediateDataset
from app.domain.rules.models import RoutedRow, RowClassification, RuleExecutionReport, RuleSeverity


class RuleConflictResolver:
    """Resolve rule evidence into one final route per row."""

    def resolve(
        self,
        *,
        dataset: IntermediateDataset,
        report: RuleExecutionReport,
        review_threshold: float = 0.75,
    ) -> tuple[RoutedRow, ...]:
        """Return deterministic row routes."""
        validation_by_row = {finding.row_number: finding for finding in report.validation_findings}
        classifications_by_row: dict[int, RowClassification] = {}
        for cls in report.classifications:
            existing = classifications_by_row.get(cls.row_number)
            if existing is None or _severity_rank(cls.severity) > _severity_rank(existing.severity):
                classifications_by_row[cls.row_number] = cls

        confidence_by_row: dict[int, float] = {}
        for row in dataset.rows:
            confidence_by_row[row.source_row_number] = row.confidence
        for match in report.matches:
            best = confidence_by_row.get(match.row_number, 0.0)
            if match.confidence > best:
                confidence_by_row[match.row_number] = match.confidence

        routed_rows: list[RoutedRow] = []
        for row in dataset.rows:
            validation = validation_by_row.get(row.source_row_number)
            classification = classifications_by_row.get(row.source_row_number)
            if classification is not None and classification.classification == "remove":
                routed_rows.append(
                    RoutedRow(
                        row_number=row.source_row_number,
                        route="removed",
                        reason=classification.message,
                    )
                )
            elif validation is not None and validation.severity == RuleSeverity.ERROR:
                routed_rows.append(
                    RoutedRow(
                        row_number=row.source_row_number,
                        route="needs_review",
                        reason=validation.message,
                    )
                )
            elif classification is not None and classification.severity in {
                RuleSeverity.WARNING,
                RuleSeverity.ERROR,
            }:
                routed_rows.append(
                    RoutedRow(
                        row_number=row.source_row_number,
                        route="needs_review",
                        reason=classification.message,
                    )
                )
            else:
                max_confidence = confidence_by_row.get(row.source_row_number, 0.0)
                if max_confidence < review_threshold:
                    routed_rows.append(
                        RoutedRow(
                            row_number=row.source_row_number,
                            route="needs_review",
                            reason=(
                                f"Low confidence ({max_confidence:.2f}) "
                                f"below review threshold ({review_threshold:.2f})"
                            ),
                        )
                    )
                else:
                    routed_rows.append(
                        RoutedRow(
                            row_number=row.source_row_number,
                            route="clean",
                            reason="No review or removal rules matched",
                        )
                    )
        return tuple(routed_rows)


def _severity_rank(severity: RuleSeverity) -> int:
    return {
        RuleSeverity.INFO: 1,
        RuleSeverity.WARNING: 2,
        RuleSeverity.ERROR: 3,
    }[severity]
