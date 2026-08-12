# ADR 007: Security Boundaries

**Status:** DESIGNED
**Context:** We need tenant isolation in the future.
**Decision:** The domain models (`Job`) contain `tenant_id` and `user_id` to prepare for Phase 6 RBAC.
