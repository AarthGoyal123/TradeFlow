# Client Requirements

This file is the chronological source of truth for TradeFlow client requirements.
Do not remove requirements unless the project owner explicitly asks.

## 2026-07-28 - Initial Product Requirements

### Product Goal

- Build TradeFlow as a configurable Excel data processing platform.
- Automate trade data cleaning and importer identification.
- First client use case: Indian export shipment data, especially Indian rice export data.
- Reduce manual Excel cleaning from 1-2 hours to under 30 seconds for the MVP workflow.
- Design the system as a reusable engine, not a one-off script.
- Adding support for a new dataset should require creating a new template, not modifying application logic.

### MVP Functional Requirements

- Users can upload an Excel file.
- Users can choose a processing template.
- System can remove unnecessary columns.
- System can normalize company names.
- System can clean ports.
- System can detect banks.
- System can detect "To Order" consignments.
- System can detect shipping companies.
- System can apply configurable keyword rules.
- System can apply regex rules.
- System can produce `Clean_Data.xlsx`.
- System can produce `Removed_Rows.xlsx`.
- System can produce `Needs_Review.xlsx`.
- System can produce `Processing_Report.xlsx`.
- Every removal must include a reason.
- Unknown cases must go to `Needs_Review`.
- No automatic duplicate removal in MVP.

### MVP Non-Functional Requirements

- Processing should be fast enough for local use, targeting under 30 seconds for the client's workflow.
- Business rules must be configurable.
- Business logic must not be hardcoded into application code.
- System should be modular, testable, and production-grade.
- System should be designed with SaaS potential in mind.
- Paid AI APIs must not be used.
- AI/LLMs are optional future enhancements only.

### Required Technology Stack

- Backend: Python 3.12.
- Backend API: FastAPI.
- Data processing: Pandas and OpenPyXL.
- Matching: RapidFuzz.
- Database: SQLite.
- Frontend: React, Vite, TypeScript, Tailwind CSS, shadcn/ui.
- Development tools: Git and VS Code.

### Required Project Structure Themes

- Create and maintain `templates/`.
- Create and maintain `rules/`.
- Create and maintain `engine/`.
- Create and maintain `config/`.
- Each template should define columns, cleaning pipeline, enabled modules, and output settings.

### Required Documentation

- Maintain `README.md`.
- Maintain `PROJECT.md`.
- Maintain `ARCHITECTURE.md`.
- Maintain `API.md`.
- Maintain `DATABASE.md`.
- Maintain `TODO.md`.
- Maintain `CHANGELOG.md`.
- Maintain `ROADMAP.md`.
- Maintain `TESTING.md`.
- Maintain `AI_CONTEXT.md`.

### Project Knowledge Base Requirement

- Maintain a `knowledge/` folder as the long-term memory of the project.
- Maintain `knowledge/client_requirements.md`.
- Maintain `knowledge/business_rules.md`.
- Maintain `knowledge/excel_format.md`.
- Maintain `knowledge/architecture_decisions.md`.
- Review these knowledge files before implementing new features.
- Update the knowledge base before writing code when implementation changes because of a new requirement.
- Automatically update the appropriate knowledge file whenever an important decision is made.
- If new information conflicts with previous decisions, ask the project owner before changing documented architecture.

## 2026-07-28 - API Foundation Batch Requirements

### Template Details API

- Implement `GET /templates/{template_id}`.
- Return template `id`, `name`, `version`, `description`, `columns`, `pipeline`, and `outputs`.
- Return 404 through the existing error hierarchy when a template does not exist.

### File Upload API

- Implement `POST /jobs`.
- Accept `multipart/form-data`.
- Accept an Excel workbook file and `template_id`.
- Accept `.xlsx` and `.xls` workbook extensions.
- Validate uploaded file extension.
- Enforce configurable maximum upload size.
- Generate a UUID `job_id`.
- Save uploaded workbook into the configured upload directory.
- Never overwrite existing files.
- Return `job_id`, `status`, `template_id`, and original `filename`.
- Do not parse or process the workbook yet.

### Job Tracking

- Add lightweight SQLite job persistence.
- Track `job_id`, `template_id`, `original_filename`, `stored_filename`, `status`, `created_at`, and `updated_at`.
- Supported job statuses are `uploaded`, `processing`, `completed`, and `failed`.

### Job Retrieval API

- Implement `GET /jobs/{job_id}`.
- Return job metadata and current status.
- Return 404 through the existing error hierarchy when a job does not exist.

## 2026-07-28 - Workbook Processing Foundation Requirements

### Workbook Loader

- Read `.xlsx` workbooks with OpenPyXL.
- Support configurable worksheet selection from the selected template.
- Return a project workbook abstraction rather than exposing OpenPyXL across the codebase.

### Sheet Reader

- Read worksheet rows efficiently.
- Preserve original worksheet row numbers.
- Handle empty cells consistently.
- Support header extraction.

### Template Mapping

- Map template column definitions to worksheet columns.
- Detect missing required columns.
- Produce descriptive validation errors.

### Validation Pipeline

- Validate workbook structure.
- Validate required sheets.
- Validate required columns.
- Return structured validation results.
- Do not implement workbook parsing beyond structural reading.
- Do not implement business cleaning, rule execution, classification, or output generation yet.

## 2026-07-28 - Processing Pipeline to Intermediate Dataset Requirements

### Processing Orchestration

- Implement a processing workflow that starts from an uploaded job and a validated workbook.
- Convert valid workbook rows into a normalized intermediate dataset.
- Keep processing synchronous for now; do not add background workers or queues.
- Do not implement rule engine, output workbook generation, download APIs, or report APIs yet.

### Processing Stages

- Add a column removal stage driven by template configuration.
- Add a basic normalization stage for intermediate dataset values.
- Preserve source worksheet row numbers.
- Track structured progress for validation, dataset building, column removal, and normalization.
- Provide extension points for future rule-engine stages without implementing rule behavior.

### Job Workflow

- Processing should update job state from `uploaded` to `processing`, then `completed` or `failed`.
- Processing errors should be structured and traceable.

## 2026-07-28 - Rule Engine Foundation Requirements

### Rule Engine Foundation

- Implement rule domain models.
- Implement a rule evaluation pipeline over the intermediate dataset.
- Implement built-in rule operators.
- Support row classification results.
- Support cell transformation results.
- Support validation rule execution.
- Produce a structured rule execution report.
- Provide extension points for custom rule packs.
- Do not implement workbook export, download APIs, background workers, or UI.

### Rule Engine Boundaries

- Rule business logic belongs in domain and application layers.
- Infrastructure should not contain rule behavior.
- Rule execution should consume the domain-owned intermediate dataset, not workbook or OpenPyXL objects.
