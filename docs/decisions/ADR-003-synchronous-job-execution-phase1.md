# ADR 003: Synchronous Job Execution (Phase 1)

**Status:** IMPLEMENTED
**Context:** We need a reliable baseline before introducing background workers.
**Decision:** Processing happens synchronously in the HTTP request via a `SynchronousJobExecutor`, which acts as an abstraction for future async execution.
