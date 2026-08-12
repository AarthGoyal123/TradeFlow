"""Learning Alias Store — persists user-confirmed header mappings."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class AliasRecord:
    workbook_header: str
    business_field: str
    count: int = 1
    first_seen: str = ""
    last_confirmed: str = ""

    def confirmed(self) -> None:
        self.count += 1
        self.last_confirmed = datetime.now().isoformat()


class LearningAliasStore:
    """In-memory store for user-confirmed header-to-business-field mappings.
    
    In production, this would be backed by a database table.
    """

    def __init__(self) -> None:
        self._records: dict[str, AliasRecord] = {}

    def record_confirmation(self, workbook_header: str, business_field: str) -> None:
        key = f"{workbook_header.lower().strip()}|{business_field.lower()}"
        if key in self._records:
            self._records[key].confirmed()
        else:
            now = datetime.now().isoformat()
            self._records[key] = AliasRecord(
                workbook_header=workbook_header,
                business_field=business_field,
                first_seen=now,
                last_confirmed=now,
            )

    def get_learned_alias(self, workbook_header: str) -> str | None:
        for key, record in self._records.items():
            h, f = key.split("|", 1)
            if workbook_header.lower().strip() == h:
                return f
        return None

    def get_learned_headers(self, business_field: str) -> list[str]:
        result = []
        for key, record in self._records.items():
            h, f = key.split("|", 1)
            if f == business_field.lower():
                result.append(record.workbook_header)
        return result

    @property
    def all_learned(self) -> dict[str, str]:
        return {k: v.business_field for k, v in self._records.items()}