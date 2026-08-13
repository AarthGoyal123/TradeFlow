import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from tests.helpers.auth import create_test_user, override_auth, clear_auth_override


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


def test_tenant_isolation_jobs_and_outputs(client: TestClient) -> None:
    # Setup Tenant A
    user_a = create_test_user(user_id="user_a", email="a@tenant.com")
    override_auth(client.app, user_a, tenant_id="tenant_a")
    
    # Upload job A
    resp_a = client.post(
        "/jobs",
        data={"template_id": "indian_rice_exports"},
        files={"file": ("shipment_a.xlsx", b"bytes", "application/vnd.ms-excel")},
    )
    assert resp_a.status_code == 200
    job_a_id = resp_a.json()["job_id"]

    # Verify User A can access Job A
    assert client.get(f"/jobs/{job_a_id}").status_code == 200
    
    # Setup Tenant B
    clear_auth_override(client.app)
    user_b = create_test_user(user_id="user_b", email="b@tenant.com")
    override_auth(client.app, user_b, tenant_id="tenant_b")

    # Upload job B
    resp_b = client.post(
        "/jobs",
        data={"template_id": "indian_rice_exports"},
        files={"file": ("shipment_b.xlsx", b"bytes", "application/vnd.ms-excel")},
    )
    assert resp_b.status_code == 200
    job_b_id = resp_b.json()["job_id"]

    # Verify User B can access Job B
    assert client.get(f"/jobs/{job_b_id}").status_code == 200
    
    # Verify User B CANNOT access Job A
    resp_b_job_a = client.get(f"/jobs/{job_a_id}")
    assert resp_b_job_a.status_code == 404
    assert resp_b_job_a.json()["error"]["code"] == "job_not_found"
    
    resp_b_proc_a = client.post(f"/jobs/{job_a_id}/process")
    assert resp_b_proc_a.status_code == 404
    
    resp_b_intel_a = client.get(f"/jobs/{job_a_id}/intelligence")
    assert resp_b_intel_a.status_code == 404
    
    resp_b_report_a = client.get(f"/jobs/{job_a_id}/report")
    assert resp_b_report_a.status_code == 404

    resp_b_out_a = client.get(f"/jobs/{job_a_id}/outputs/clean")
    assert resp_b_out_a.status_code == 404
    
    # Re-authenticate as Tenant A
    clear_auth_override(client.app)
    override_auth(client.app, user_a, tenant_id="tenant_a")
    
    # Verify User A CANNOT access Job B
    assert client.get(f"/jobs/{job_b_id}").status_code == 404
