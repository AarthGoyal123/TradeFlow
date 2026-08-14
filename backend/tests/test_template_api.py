
from tests.helpers.auth import create_authenticated_client


def test_get_templates_returns_template_summaries() -> None:
    client = create_authenticated_client()

    response = client.get("/templates")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "indian_rice_exports",
            "name": "Indian Rice Exports",
            "version": "0.1.0",
            "description": "Starter template for Indian rice export shipment data.",
        }
    ]
