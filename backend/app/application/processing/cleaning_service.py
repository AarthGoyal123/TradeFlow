"""Apply template-configured cleaning rules to a dataset."""

from app.domain.datasets.models import DatasetCell, DatasetRow, IntermediateDataset
from app.domain.workbooks.cleaning import DatasetCleaningConfig, FieldCleaningRule
from app.domain.workbooks.models import CellValue


class DataCleaningService:
    """Apply field-level cleaning rules from template configuration."""

    def clean(
        self,
        *,
        dataset: IntermediateDataset,
        cleaning_config: DatasetCleaningConfig,
    ) -> IntermediateDataset:
        if not cleaning_config.field_rules:
            return dataset
        return IntermediateDataset(
            template_id=dataset.template_id,
            sheet_name=dataset.sheet_name,
            rows=tuple(self._clean_row(row, cleaning_config.field_rules) for row in dataset.rows),
            removed_fields=dataset.removed_fields,
        )

    @staticmethod
    def _clean_row(
        row: DatasetRow,
        rules: dict[str, FieldCleaningRule],
    ) -> DatasetRow:
        return DatasetRow(
            source_row_number=row.source_row_number,
            cells=tuple(
                DatasetCell(
                    field=cell.field,
                    source_header=cell.source_header,
                    value=_clean_value(cell.value, rules.get(cell.field)),
                )
                for cell in row.cells
            ),
            confidence=row.confidence,
        )


def _clean_value(value: CellValue, rule: FieldCleaningRule | None) -> CellValue:
    if rule is None:
        return value
    if not isinstance(value, str):
        return value
    cleaned = rule.apply(value)
    return cleaned if cleaned else None
