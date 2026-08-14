import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app, base_url="http://testserver/api/v1")


def test_auth_registration_creates_tenant_and_user(client: TestClient) -> None:
    email = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strongPassword123!",
            "display_name": "Test Owner",
            "organization_name": "Acme Corp",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == email
    assert data["user"]["display_name"] == "Test Owner"
    
    # Try duplicate registration
    resp_dup = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strongPassword123!",
            "display_name": "Test Owner",
            "organization_name": "Acme Corp",
        },
    )
    assert resp_dup.status_code == 400


def test_auth_login_sets_cookie_and_csrf(client: TestClient) -> None:
    email = f"login_{uuid.uuid4().hex[:8]}@example.com"
    # First register
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strongPassword123!",
            "display_name": "Login Tester",
            "organization_name": "Acme Corp",
        },
    )

    # Then login
    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "strongPassword123!",
        },
    )
    assert response.status_code == 200
    
    # Check cookies
    assert "access_token" in response.cookies
    assert "csrf_token" in response.cookies
    
    access_token_cookie = None
    for cookie in response.headers.get_list("set-cookie"):
        if cookie.startswith("access_token="):
            access_token_cookie = cookie
            break
            
    assert access_token_cookie is not None
    assert "HttpOnly" in access_token_cookie
    assert "samesite=lax" in access_token_cookie.lower()

    # Invalid login
    resp_invalid = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "wrongpassword",
        },
    )
    assert resp_invalid.status_code == 401


def test_auth_me_returns_user_details(client: TestClient) -> None:
    # Unauthenticated should fail
    resp_unauth = client.get("/auth/me")
    assert resp_unauth.status_code == 401
    
    email = f"me_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strongPassword123!",
            "display_name": "Me Tester",
            "organization_name": "Acme Corp",
        },
    )
    client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "strongPassword123!",
        },
    )

    resp_auth = client.get("/auth/me")
    assert resp_auth.status_code == 200
    assert resp_auth.json()["user"]["email"] == email
    

def test_auth_logout_clears_cookies(client: TestClient) -> None:
    email = f"logout_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strongPassword123!",
            "display_name": "Logout Tester",
            "organization_name": "Acme Corp",
        },
    )
    client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "strongPassword123!",
        },
    )

    # Logout
    # Since it's a POST, we need to send the CSRF token
    csrf_token = client.cookies.get("csrf_token") or ""
    resp_logout = client.post(
        "/auth/logout",
        headers={"X-CSRF-Token": csrf_token}
    )
    assert resp_logout.status_code == 200
    
    # Check if cookies are cleared (value should be empty or expired)
    cleared_access_token = False
    for cookie in resp_logout.headers.get_list("set-cookie"):
        if cookie.startswith("access_token="):
            # typically max-age=0 or expires in the past
            if "Max-Age=0" in cookie or "expires=" in cookie:
                cleared_access_token = True
    assert cleared_access_token

    # Verify session is dead
    resp_me = client.get("/auth/me")
    assert resp_me.status_code == 401


def test_csrf_protection_rejects_missing_token(client: TestClient) -> None:
    email = f"csrf_{uuid.uuid4().hex[:8]}@example.com"
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": "strongPassword123!",
            "display_name": "CSRF Tester",
            "organization_name": "Acme Corp",
        },
    )
    client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "strongPassword123!",
        },
    )
    
    # Make a state changing request WITHOUT csrf header
    # /jobs POST requires auth and CSRF
    resp_no_csrf = client.post(
        "/jobs",
        data={"template_id": "indian_rice_exports"},
        files={"file": ("shipment.xlsx", b"bytes", "application/vnd.ms-excel")},
    )
    assert resp_no_csrf.status_code == 403
    assert resp_no_csrf.json()["detail"] == "CSRF token validation failed"
    
    # With wrong csrf token
    resp_bad_csrf = client.post(
        "/jobs",
        data={"template_id": "indian_rice_exports"},
        files={"file": ("shipment.xlsx", b"bytes", "application/vnd.ms-excel")},
        headers={"X-CSRF-Token": "badtoken"}
    )
    assert resp_bad_csrf.status_code == 403
