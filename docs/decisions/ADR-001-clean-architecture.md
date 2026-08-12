# ADR 001: Clean Architecture

**Status:** IMPLEMENTED
**Context:** The codebase needs strict dependency rules to prevent infrastructure logic (like Excel I/O) from polluting business rules.
**Decision:** We adopted Clean Architecture (API -> Application -> Domain <- Infrastructure).
