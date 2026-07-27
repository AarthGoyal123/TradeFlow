# API

This file will document the backend API as it is implemented.

## Planned MVP Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service health check. Implemented. |
| GET | `/templates` | List available processing templates. Implemented. |
| GET | `/templates/{template_id}` | Get template metadata. Implemented. |
| POST | `/jobs` | Upload workbook and create an uploaded job. Implemented. |
| GET | `/jobs/{job_id}` | Get job status and summary. Implemented. |
| GET | `/jobs/{job_id}/report` | Get processing report metadata. |
| GET | `/jobs/{job_id}/download/{output_type}` | Download generated workbook. |

## Implemented Endpoints

### `GET /health`

Returns:

```json
{
  "status": "ok"
}
```

### `GET /templates`

Returns all available processing templates from the filesystem template repository.

Response:

```json
[
  {
    "id": "indian_rice_exports",
    "name": "Indian Rice Export Shipments",
    "version": "0.1.0",
    "description": "Starter template for Indian rice export shipment data."
  }
]
```

### `GET /templates/{template_id}`

Returns detailed metadata for one processing template.

Response:

```json
{
  "id": "indian_rice_exports",
  "name": "Indian Rice Export Shipments",
  "version": "0.1.0",
  "description": "Starter template for Indian rice export shipment data.",
  "columns": [
    {
      "field": "consignee_name",
      "aliases": ["Consignee", "Importer", "Buyer", "Notify Party"],
      "required": true
    }
  ],
  "pipeline": ["validation", "column_removal"],
  "outputs": [
    {
      "type": "clean_data",
      "filename": "Clean_Data.xlsx"
    }
  ]
}
```

Returns `404` with `template_not_found` when the template does not exist.

### `POST /jobs`

Accepts `multipart/form-data` with:

- `template_id`: processing template identifier.
- `file`: uploaded Excel workbook.

Allowed extensions are configurable and currently default to `.xlsx` and `.xls`.
The endpoint saves the uploaded file and creates a persisted job, but it does not parse or process the workbook yet.

Response:

```json
{
  "job_id": "uuid",
  "status": "uploaded",
  "template_id": "indian_rice_exports",
  "filename": "shipment.xlsx"
}
```

Returns:

- `400` with `upload_validation_error` for invalid extension or oversized uploads.
- `404` with `template_not_found` when the selected template does not exist.

### `GET /jobs/{job_id}`

Returns persisted job metadata and current status.

Response:

```json
{
  "job_id": "uuid",
  "template_id": "indian_rice_exports",
  "original_filename": "shipment.xlsx",
  "stored_filename": "uuid.xlsx",
  "status": "uploaded",
  "created_at": "2026-07-28T00:00:00+00:00",
  "updated_at": "2026-07-28T00:00:00+00:00"
}
```

Returns `404` with `job_not_found` when the job does not exist.

## Notes

- API contracts must be versioned before production use.
- File upload limits and validation errors must be explicit.
- Expected TradeFlow errors are mapped to structured JSON error responses.

## Error Shape

```json
{
  "error": {
    "code": "template_validation_error",
    "message": "Human-readable message",
    "details": {}
  }
}
```
