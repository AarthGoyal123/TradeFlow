"""Authentication test helpers."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.api.security import (
    CurrentUserContext,
    csrf_protect,
    get_current_user_context,
    require_tenant_access,
)
from app.domain.auth.models import Role, Tenant, User
from app.main import create_app


def create_test_tenant(tenant_id: str = "test_tenant", name: str = "Test Tenant") -> Tenant:
    return Tenant(
        id=tenant_id,
        name=name,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def create_test_user(
    user_id: str = "test_user", email: str = "test@example.com", display_name: str = "Test User"
) -> User:
    return User(
        id=user_id,
        email=email,
        display_name=display_name,
        password_hash="fakehash",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def override_auth(
    app,
    user: User,
    tenant_id: str | None = None,
    role: Role = Role.OWNER,
) -> None:
    """Override FastAPI dependency injection to simulate an authenticated user."""
    context = CurrentUserContext(user=user, tenant_id=tenant_id)

    app.dependency_overrides[get_current_user_context] = lambda: context
    app.dependency_overrides[csrf_protect] = lambda: None
    # If the route also uses require_tenant_access explicitly
    if tenant_id:
        app.dependency_overrides[require_tenant_access] = lambda: context


def clear_auth_override(app) -> None:
    """Remove authentication overrides."""
    app.dependency_overrides.pop(get_current_user_context, None)
    app.dependency_overrides.pop(require_tenant_access, None)
    app.dependency_overrides.pop(csrf_protect, None)


def create_authenticated_client(
    user_id: str = "test_user",
    tenant_id: str = "test_tenant",
    role: Role = Role.OWNER,
) -> TestClient:
    """Create a TestClient that is fully authenticated for tests that don't need isolation setup."""
    app = create_app()
    user = create_test_user(user_id=user_id)
    override_auth(app, user, tenant_id=tenant_id, role=role)
    return TestClient(app, base_url="http://testserver/api/v1")
