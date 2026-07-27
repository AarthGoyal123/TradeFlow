# Excel Format Knowledge

This file documents supported Excel formats, sheet names, columns, validation rules, template behavior, and mapping examples.

## 2026-07-28 - Supported Format: Indian Rice Export Shipments

Status: starter template created.

### Workbook Type

- Excel workbook uploaded by the user.
- Exact extension support will be confirmed during implementation, but `.xlsx` is the primary target.

### Sheet Names

- Unknown at project start.
- Planned behavior: template should define whether the engine reads a named sheet, the first sheet, or a sheet selected by the user.

### Required Columns

The exact client file headers are not yet available.
The initial template should support configurable aliases for likely trade-data fields.

Likely required conceptual fields:

- Consignee or importer name.
- Port.
- Shipment/export details needed to preserve output context.

### Optional Columns

Unknown at project start.
The template should allow optional columns and pass-through columns.

### Validation Rules

- File must be a readable Excel workbook.
- Required conceptual fields must be mapped before processing.
- Missing required columns should produce a validation error before transformation.
- Unknown extra columns should be allowed unless the template says otherwise.
- Header extraction should preserve worksheet row numbers.
- Empty cells should be represented consistently as `None`.
- Template worksheet selection currently supports the first sheet and named sheets.

### Template-Specific Processing Behavior

- Remove configured unnecessary columns.
- Normalize company names.
- Clean port values.
- Detect banks.
- Detect "To Order" consignments.
- Detect shipping companies.
- Apply configured keyword rules.
- Apply configured regex rules.
- Apply RapidFuzz matching where configured.
- Route uncertain rows to `Needs_Review.xlsx`.
- Produce clean, removed, needs-review, and report workbooks.

### Template Files

Initial files exist under `templates/indian_rice_exports/`:

- `config.json`
- `columns.json`
- `pipeline.json`
- `output.json`
- `rules/keywords.json`
- `rules/regex.json`
- `rules/fuzzy_matches.json`

### Sample Mapping Examples

These are illustrative only and must be replaced or validated against real client files.

| Conceptual Field | Possible Source Headers |
| --- | --- |
| Importer / Consignee | `Consignee`, `Importer`, `Buyer`, `Notify Party` |
| Port | `Port`, `Destination Port`, `Discharge Port`, `POD` |
| Shipping Company | `Shipping Line`, `Carrier`, `Vessel Operator` |
