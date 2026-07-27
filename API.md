# API

This file will document the backend API as it is implemented.

## Planned MVP Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/health` | Service health check. Implemented. |
| GET | `/templates` | List available processing templates. |
| GET | `/templates/{template_id}` | Get template metadata. |
| POST | `/jobs` | Upload workbook and start processing. |
| GET | `/jobs/{job_id}` | Get job status and summary. |
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
