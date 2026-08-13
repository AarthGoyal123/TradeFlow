import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.helpers.auth import create_test_user, override_auth, clear_auth_override
from app.domain.auth.models import Role


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_rbac_owner_can_access(client: TestClient) -> None:
    user = create_test_user(user_id="owner_user", email="owner@test.com")
    override_auth(client.app, user, tenant_id="tenant_rbac", role=Role.OWNER)
    
    # Verify owner can access their tenant's resources (like fetching templates)
    # The current routes only enforce tenant membership broadly.
    # We test that the role injection works and doesn't break basic access.
    resp = client.get("/templates")
    assert resp.status_code == 200


def test_rbac_admin_can_access(client: TestClient) -> None:
    user = create_test_user(user_id="admin_user", email="admin@test.com")
    override_auth(client.app, user, tenant_id="tenant_rbac", role=Role.ADMIN)
    
    resp = client.get("/templates")
    assert resp.status_code == 200


def test_rbac_member_can_access(client: TestClient) -> None:
    user = create_test_user(user_id="member_user", email="member@test.com")
    override_auth(client.app, user, tenant_id="tenant_rbac", role=Role.MEMBER)
    
    resp = client.get("/templates")
    assert resp.status_code == 200
