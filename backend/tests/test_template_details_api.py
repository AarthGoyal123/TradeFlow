from fastapi.testclient import TestClient

from app.main import create_app
from tests.helpers.auth import create_authenticated_client


def test_get_template_details_returns_columns_pipeline_and_outputs() -> None:
    client = create_authenticated_client()

    response = client.get("/templates/indian_rice_exports")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "indian_rice_exports"
    assert data["name"] == "Indian Rice Exports"
    assert data["version"] == "0.1.0"

    # Verify original required columns still exist
    col_fields = {c["field"]: c for c in data["columns"]}
    assert col_fields["consignee_name"]["required"] is True
    assert col_fields["port"]["required"] is True
    assert col_fields["shipping_company"]["required"] is False

    # Verify all new columns exist
    expected_fields = {
        "consignee_name",
        "port",
        "hs_code",
        "shipping_company",
        "indian_port",
        "cush",
        "date",
        "iec",
        "exporter_name",
        "exporter_address",
        "exporter_city_state",
        "exporter_pin",
        "country",
        "chp",
        "description",
        "quantity",
        "uqc",
        "unit_rate",
        "currency",
        "fob",
    }
    assert col_fields.keys() == expected_fields
    assert len(data["columns"]) == 20

    assert data["pipeline"] == [
        "validation",
        "column_removal",
        "normalization",
        "keyword_rules",
        "regex_rules",
        "fuzzy_matching",
        "confidence_scoring",
        "output_generation",
    ]
    assert data["outputs"] == [
        {"type": "clean_data", "filename": "Clean_Data.xlsx"},
        {"type": "removed_rows", "filename": "Removed_Rows.xlsx"},
        {"type": "needs_review", "filename": "Needs_Review.xlsx"},
        {"type": "processing_report", "filename": "Processing_Report.xlsx"},
    ]


def test_get_missing_template_details_returns_404() -> None:
    client = create_authenticated_client()

    response = client.get("/templates/missing_template")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "template_not_found"
