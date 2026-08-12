# ADR 006: Job State Machine

**Status:** IMPLEMENTED
**Context:** Jobs must transition strictly (uploaded -> processing -> completed/failed).
**Decision:** Centralized state transitions in the Domain layer (`Job` model) to prevent invalid sequences.
