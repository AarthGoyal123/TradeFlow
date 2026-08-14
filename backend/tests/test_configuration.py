import os
from unittest import mock

from app.core.settings import Settings


def test_settings_default_values() -> None:
    settings = Settings()
    assert settings.environment == "development"
    assert settings.max_upload_size_mb == 50

def test_settings_environment_override() -> None:
    with mock.patch.dict(os.environ, {
        "TRADEFLOW_ENVIRONMENT": "production",
        "TRADEFLOW_MAX_UPLOAD_SIZE_MB": "100",
        "TRADEFLOW_AUTH_SECRET": "this-is-a-secure-secret-for-production-testing-123",
        "TRADEFLOW_COOKIE_SECURE": "true",
        "TRADEFLOW_FRONTEND_URL": "https://tradeflow.example.com",
    }):
        settings = Settings()
        assert settings.environment == "production"
        assert settings.max_upload_size_mb == 100

def test_non_sqlite_database_url_returns_empty_path() -> None:
    with mock.patch.dict(os.environ, {"TRADEFLOW_DATABASE_URL": "postgresql://user:pass@host/db"}):
        settings = Settings()
        path = settings.resolved_database_path
        assert str(path) == "."
