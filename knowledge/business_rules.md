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

