import pytest
from pydantic import ValidationError

from app.core.settings import Settings


def test_development_settings_allow_insecure_defaults() -> None:
    settings = Settings(environment="development")
    assert settings.environment == "development"
    assert not settings.cookie_secure
    assert settings.auth_secret == "super-secret-development-key-change-in-production"

def test_production_settings_reject_default_secret() -> None:
    with pytest.raises(ValidationError, match="TRADEFLOW_AUTH_SECRET must be changed in production"):
        Settings(
            environment="production",
            auth_secret="super-secret-development-key-change-in-production",
            cookie_secure=True,
            cors_origins=["https://tradeflow.example.com"]
        )

def test_production_settings_reject_short_secret() -> None:
    with pytest.raises(ValidationError, match="TRADEFLOW_AUTH_SECRET must be at least 32 characters long"):
        Settings(
            environment="production",
            auth_secret="too-short",
            cookie_secure=True,
            cors_origins=["https://tradeflow.example.com"]
        )

def test_production_settings_reject_insecure_cookies() -> None:
    with pytest.raises(ValidationError, match="TRADEFLOW_COOKIE_SECURE must be true in production"):
        Settings(
            environment="production",
            auth_secret="this-is-a-long-enough-secret-for-production",
            cookie_secure=False,
            cors_origins=["https://tradeflow.example.com"]
        )

def test_production_settings_reject_wildcard_cors() -> None:
    with pytest.raises(ValidationError, match="TRADEFLOW_CORS_ORIGINS must not contain '\\*' in production"):
        Settings(
            environment="production",
            auth_secret="this-is-a-long-enough-secret-for-production",
            cookie_secure=True,
            cors_origins=["*", "https://tradeflow.example.com"]
        )

def test_production_settings_google_oauth_requires_secret() -> None:
    with pytest.raises(ValidationError, match="TRADEFLOW_GOOGLE_CLIENT_SECRET is required when using Google OAuth"):
        Settings(
            environment="production",
            auth_secret="this-is-a-long-enough-secret-for-production",
            cookie_secure=True,
            cors_origins=["https://tradeflow.example.com"],
            google_client_id="client-id",
            google_client_secret=None,
        )

def test_production_settings_google_oauth_requires_redirect_uri() -> None:
    with pytest.raises(ValidationError, match="TRADEFLOW_GOOGLE_REDIRECT_URI is required when using Google OAuth"):
        Settings(
            environment="production",
            auth_secret="this-is-a-long-enough-secret-for-production",
            cookie_secure=True,
            cors_origins=["https://tradeflow.example.com"],
            google_client_id="client-id",
            google_client_secret="client-secret",
            google_redirect_uri=None,
        )

def test_production_settings_valid() -> None:
    settings = Settings(
        environment="production",
        auth_secret="this-is-a-long-enough-secret-for-production",
        cookie_secure=True,
        cors_origins=["https://tradeflow.example.com"],
        google_client_id="client-id",
        google_client_secret="client-secret",
        google_redirect_uri="https://api.example.com/api/v1/auth/google/callback",
    )
    assert settings.environment == "production"
