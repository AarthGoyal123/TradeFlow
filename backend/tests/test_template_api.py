from fastapi.testclient import TestClient

from app.main import create_app


def test_get_templates_returns_template_summaries() -> None:
    client = TestClient(create_app())

    response = client.get("/templates")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "indian_rice_exports",
            "name": "Indian Rice Export Shipments",
            "version": "0.1.0",
            "description": "Starter template for Indian rice export shipment data.",
        }
    ]

