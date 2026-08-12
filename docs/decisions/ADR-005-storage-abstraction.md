# ADR 005: Storage Abstraction

**Status:** DESIGNED
**Context:** Local file storage prevents horizontal scaling.
**Decision:** All file I/O uses an `OutputStorage` and `UploadedFileStorage` port, currently backed by local disks, but easily replaceable with S3.
