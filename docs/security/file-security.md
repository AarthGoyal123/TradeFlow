# File Security

**Status:** IMPLEMENTED

Uploads are strictly checked for size limits and extensions. Path traversal is prevented via `os.path.basename` enforcement in the upload and download routes.
