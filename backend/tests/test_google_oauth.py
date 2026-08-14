"""Tests for Google OAuth flow."""

import pytest
from fastapi.testclient import TestClient

from app.domain.auth.models import ExternalIdentity
from app.main import create_app


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("TRADEFLOW_GOOGLE_CLIENT_ID", "test_client_id")
    monkeypatch.setenv("TRADEFLOW_GOOGLE_CLIENT_SECRET", "test_secret")
    monkeypatch.setenv("TRADEFLOW_GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    monkeypatch.setenv("TRADEFLOW_COOKIE_SECURE", "false")
    
    # Use a file-based sqlite db so that connections share the same database schema
    db_path = tmp_path / "test_oauth.sqlite"
    monkeypatch.setenv("TRADEFLOW_DATABASE_URL", f"sqlite:///{db_path}")
    
    from app.core.settings import get_settings
    get_settings.cache_clear()
    
    import app.infrastructure.database.models
    from app.infrastructure.database.base import Base
    from app.infrastructure.database.session import get_engine
    
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    app = create_app()
    return app




@pytest.fixture
def mock_google_provider(mocker, client):
    from unittest.mock import AsyncMock, MagicMock

    from app.api.dependencies import get_google_oauth_provider
    
    instance = MagicMock()
    instance.generate_pkce.return_value = ("test_verifier", "test_challenge")
    
    async def mock_auth_url(state, challenge, nonce):
        return "https://accounts.google.com/o/oauth2/v2/auth?test=1"
    instance.get_authorization_url = AsyncMock(side_effect=mock_auth_url)
    
    async def mock_auth(*args, **kwargs):
        return ExternalIdentity(
            provider="google",
            subject="google_123",
            email="testgoogle@example.com",
            display_name="Test Google User",
            email_verified=True,
        )
    instance.authenticate = AsyncMock(side_effect=mock_auth)
    
    # Override the dependency in the app
    client.dependency_overrides[get_google_oauth_provider] = lambda: instance
    yield instance
    client.dependency_overrides = {}


@pytest.fixture
def test_client(client):
    return TestClient(client, base_url="http://testserver/api/v1")


def test_google_login_redirect(test_client: TestClient, mock_google_provider):
    """Test that /auth/google/login redirects to Google and sets state cookie."""
    response = test_client.get("/auth/google/login", follow_redirects=False)
    
    assert response.status_code == 307
    assert response.headers["location"].startswith("https://accounts.google.com/o/oauth2/v2/auth")
    
    # Check that oauth_state cookie was set
    cookies = response.cookies
    assert "oauth_state" in cookies


def test_google_callback_success(test_client: TestClient, mock_google_provider):
    """Test a successful callback creates user and returns session."""
    # First get the state cookie
    login_response = test_client.get("/auth/google/login", follow_redirects=False)
    state_cookie = login_response.cookies.get("oauth_state")
    assert state_cookie
    state_value, _, _ = state_cookie.split(":", 2)
    
    # Now simulate the callback
    callback_response = test_client.get(
        f"/auth/google/callback?code=testcode&state={state_value}",
        cookies={"oauth_state": state_cookie},
        follow_redirects=False
    )
    
    # Should redirect to frontend
    assert callback_response.status_code == 307
    assert callback_response.headers["location"] == "http://localhost:5173/"
    
    # Check that tradeflow auth cookies are set
    cookies = callback_response.cookies
    assert "access_token" in cookies
    assert "csrf_token" in cookies


def test_google_callback_invalid_state(test_client: TestClient):
    """Test callback with missing or invalid state."""
    # Missing state
    response = test_client.get("/auth/google/callback?code=testcode", follow_redirects=False)
    assert response.status_code == 307
    assert "error=invalid_request" in response.headers["location"]
    
    # Wrong state
    response = test_client.get(
        "/auth/google/callback?code=testcode&state=wrong",
        cookies={"oauth_state": "correct:verifier:nonce"},
        follow_redirects=False
    )
    assert response.status_code == 307
    assert "error=invalid_state" in response.headers["location"]


def test_google_callback_open_redirect_protection(test_client: TestClient, mock_google_provider):
    """Test callback ignores arbitrary next parameter for open redirect protection."""
    login_response = test_client.get("/auth/google/login", follow_redirects=False)
    state_cookie = login_response.cookies.get("oauth_state")
    state_value, _, _ = state_cookie.split(":", 2)
    
    response = test_client.get(
        f"/auth/google/callback?code=testcode&state={state_value}&next=https://evil.com",
        cookies={"oauth_state": state_cookie},
        follow_redirects=False
    )
    
    assert response.status_code == 307
    assert response.headers["location"] == "http://localhost:5173/"
    assert "https://evil.com" not in response.headers["location"]
