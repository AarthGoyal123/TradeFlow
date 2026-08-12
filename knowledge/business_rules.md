# Business Rules

This file records business rules discovered during development.
Each rule should explain why it exists, relevant assumptions, edge cases, and whether it is configurable.

## 2026-07-28 - Initial Business Rules

### Hard Requirements

| Rule ID | Rule | Why It Exists | Assumptions | Edge Cases |
| --- | --- | --- | --- | --- |
| BR-001 | Unknown or low-confidence cases must be routed to `Needs_Review.xlsx`. | Avoid false positives in trade data cleaning and importer identification. | Manual review is acceptable for ambiguous rows. | Rows may be valid but unfamiliar to the current rule set. |
| BR-002 | Every removed row must include a removal reason. | Client needs traceability and trust in automated cleaning. | Output reports will be reviewed by business users. | Multiple reasons may apply; the engine should preserve enough detail for audit. |
| BR-003 | No automatic duplicate removal in the MVP. | The source specification explicitly excludes duplicate removal from the MVP. | Duplicates may have business meaning or require human judgment. | Duplicate detection can be added later as an optional configured module. |
| BR-004 | Business rules must not be hardcoded in application logic. | New datasets should be supported by templates and rule packs. | Rule files are versioned and validated. | Truly generic engine behavior may live in code, but dataset-specific logic must live in configuration. |

### Configurable Rules

| Rule ID | Rule Category | Initial Purpose | Configuration Location |
| --- | --- | --- | --- |
| CR-001 | Column removal | Remove unnecessary source columns from client Excel files. | Template column configuration. |
| CR-002 | Company name normalization | Standardize company names for matching and reporting. | Template normalization and keyword rules. |
| CR-003 | Port cleaning | Normalize inconsistent port names. | Template rules and mapping dictionaries. |
| CR-004 | Bank detection | Identify rows where consignee/importer is likely a bank. | Keyword, regex, and fuzzy rule packs. |
| CR-005 | "To Order" detection | Identify placeholder consignee values. | Keyword and regex rule packs. |
| CR-006 | Shipping company detection | Identify logistics or shipping company names. | Keyword, regex, and fuzzy rule packs. |
| CR-007 | Confidence scoring thresholds | Decide clean vs review routing. | Template output or scoring configuration. |

### Current Assumptions

- The first template will target Indian rice export shipment data.
- Source files are Excel workbooks, not CSV-only workflows.
- Initial processing can be local and synchronous if it meets the target runtime.
- The MVP should prefer review routing over aggressive automated classification.

## 2026-07-28 - Upload and Job Tracking Rules

### Hard Requirements

| Rule ID | Rule | Why It Exists | Assumptions | Edge Cases |
| --- | --- | --- | --- | --- |
| BR-005 | Uploaded workbook files must use an allowed Excel extension. | Prevent unsupported input formats from entering the system. | MVP upload support is limited to Excel workbooks. | Extension validation is not full workbook validation; parsing validation comes later. |
| BR-006 | Uploaded files must be saved with server-generated names and must never overwrite existing files. | Prevent path traversal, accidental overwrite, and filename collisions. | Original filename is metadata only. | UUID collision is extremely unlikely but storage should still check existence. |
| BR-007 | A job must be persisted when an upload is accepted. | Later APIs need stable job status and metadata. | Accepted upload means the file has been saved and the job row recorded. | If persistence fails after save, cleanup can be added later. |

### Configurable Rules

| Rule ID | Rule Category | Initial Purpose | Configuration Location |
| --- | --- | --- | --- |
| CR-008 | Allowed upload extensions | Control accepted workbook formats. | Application settings. |
| CR-009 | Maximum upload size | Prevent oversized uploads from exhausting local resources. | Application settings. |

## 2026-07-28 - Intermediate Dataset Processing Rules

### Hard Requirements

| Rule ID | Rule | Why It Exists | Assumptions | Edge Cases |
| --- | --- | --- | --- | --- |
| BR-008 | Intermediate dataset rows must preserve source worksheet row numbers. | Future reports and review files need traceability back to the original workbook. | Header row is row 1 unless template configuration evolves. | Blank rows may still have row numbers if read from the worksheet. |
| BR-009 | Processing must fail before transformation when required columns are missing. | Avoid producing misleading partially mapped data. | Workbook validation runs before dataset creation. | Optional columns may be absent without failing processing. |
| BR-010 | Template-configured removed columns should be excluded from the intermediate dataset. | Column removal is client-configurable and should not be hardcoded. | Removal can reference conceptual fields or source headers. | Unknown removal names are ignored at this stage and can become warnings later. |

### Configurable Rules

| Rule ID | Rule Category | Initial Purpose | Configuration Location |
| --- | --- | --- | --- |
| CR-010 | Removed columns | Exclude configured fields or source headers from intermediate data. | Template `columns.remove_columns`. |

## 2026-07-28 - Rule Engine Foundation Rules

### Hard Requirements

| Rule ID | Rule | Why It Exists | Assumptions | Edge Cases |
| --- | --- | --- | --- | --- |
| BR-011 | Rule execution must preserve all rule hits in a structured report. | Future reports and review routing need explainable decisions. | Rules produce evidence before final output routing exists. | Multiple rules may apply to the same row or cell. |
| BR-012 | Validation rules must not mutate dataset values. | Validation findings should be auditable separately from transformations. | Validation rules produce issues and classifications only. | A row can have validation findings and transformation outputs. |
| BR-013 | Cell transformation rules must produce transformed values without modifying the original dataset in place. | Avoid hidden mutations and keep processing reproducible. | Later stages can decide whether transformed values become the canonical dataset. | Multiple transformations can target the same cell; conflict resolution is future work. |

### Configurable Rules

| Rule ID | Rule Category | Initial Purpose | Configuration Location |
| --- | --- | --- | --- |
| CR-011 | Rule enabled state | Allow rule packs to include inactive rules. | Rule definitions. |
| CR-012 | Rule priority | Establish deterministic execution ordering. | Rule definitions. |
| CR-013 | Rule operator | Define how a field is evaluated. | Rule definitions. |
