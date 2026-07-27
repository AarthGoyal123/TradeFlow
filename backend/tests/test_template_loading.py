from pathlib import Path

import pytest

from app.core.errors import TemplateNotFoundError
from app.infrastructure.template_store.filesystem import FileSystemTemplateRepository


def test_loads_starter_template() -> None:
    repository = FileSystemTemplateRepository(Path("../templates"))

    template = repository.get_template("indian_rice_exports")

    assert template.id == "indian_rice_exports"
    assert template.pipeline.steps[0] == "validation"
    assert template.output.files.clean_data == "Clean_Data.xlsx"


def test_missing_template_raises_not_found() -> None:
    repository = FileSystemTemplateRepository(Path("../templates"))

    with pytest.raises(TemplateNotFoundError):
        repository.get_template("missing_template")

