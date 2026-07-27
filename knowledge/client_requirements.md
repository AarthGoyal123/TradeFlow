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

