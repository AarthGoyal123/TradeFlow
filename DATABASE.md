# Database

TradeFlow will use SQLite for MVP persistence.

## Planned Responsibilities

- Track processing jobs.
- Track uploaded file metadata.
- Track selected templates.
- Track generated output locations.
- Track processing summaries.
- Support future learned decisions and review feedback.

## Initial Tables

Planned tables:

- `processing_jobs`
- `processing_outputs`
- `processing_events`
- `review_items`
- `learned_decisions`

Schemas will be finalized when backend persistence is implemented.

