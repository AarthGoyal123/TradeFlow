# ADR 004: Background Worker Strategy

**Status:** PLANNED
**Context:** Processing 20,000+ rows synchronously times out HTTP requests.
**Decision:** We will introduce Celery and Redis in Phase 4 to process workbooks asynchronously.
