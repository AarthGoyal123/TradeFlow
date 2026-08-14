import os
from unittest import mock

import pytest

from app.core.settings import Settings


def test_settings_default_values() -> None:
    settings = Settings()
    assert settings.environment == "development"
    assert settings.max_upload_size_mb == 50

def test_settings_environment_override() -> None:
    with mock.patch.dict(os.environ, {"TRADEFLOW_ENVIRONMENT": "production", "TRADEFLOW_MAX_UPLOAD_SIZE_MB": "100"}):
        settings = Settings()
        assert settings.environment == "production"
        assert settings.max_upload_size_mb == 100

def test_invalid_database_url_raises() -> None:
    with mock.patch.dict(os.environ, {"TRADEFLOW_DATABASE_URL": "postgres://user:pass@host/db"}):
        settings = Settings()
        with pytest.raises(ValueError, match="Only sqlite:///"):
            _ = settings.resolved_database_path
