from fastapi.testclient import TestClient

from app.main import create_app


def test_get_template_details_returns_columns_pipeline_and_outputs() -> None:
    client = TestClient(create_app())

    response = client.get("/templates/indian_rice_exports")

    assert response.status_code == 200
    assert response.json() == {
        "id": "indian_rice_exports",
        "name": "Indian Rice Export Shipments",
        "version": "0.1.0",
        "description": "Starter template for Indian rice export shipment data.",
        "columns": [
            {
                "field": "consignee_name",
                "aliases": ["Consignee", "Importer", "Buyer", "Notify Party"],
                "required": True,
            },
            {
                "field": "port",
                "aliases": ["Port", "Destination Port", "Discharge Port", "POD"],
                "required": True,
            },
            {
                "field": "shipping_company",
                "aliases": ["Shipping Line", "Carrier", "Vessel Operator"],
                "required": False,
            },
        ],
        "pipeline": [
            "validation",
            "column_removal",
            "normalization",
            "keyword_rules",
            "regex_rules",
            "fuzzy_matching",
            "confidence_scoring",
            "output_generation",
        ],
        "outputs": [
            {"type": "clean_data", "filename": "Clean_Data.xlsx"},
            {"type": "removed_rows", "filename": "Removed_Rows.xlsx"},
            {"type": "needs_review", "filename": "Needs_Review.xlsx"},
            {"type": "processing_report", "filename": "Processing_Report.xlsx"},
        ],
    }


def test_get_template_details_missing_template_returns_404() -> None:
    client = TestClient(create_app())

    response = client.get("/templates/missing_template")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "template_not_found"

