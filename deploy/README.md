# TradeFlow Minimal Self-Hosted Production Deployment

This directory contains templates and documentation for deploying TradeFlow in a production environment using a minimal, self-hosted architecture.

**Core Principles:**
- **Zero Paid Services:** The application runs entirely on standard VMs without requiring cloud vendor lock-in or paid databases.
- **SQLite Database:** The primary application database is SQLite with WAL mode enabled.
- **Local Storage:** Files are securely stored on the local disk with strict path traversal protections.
- **Process Management:** The backend runs via `uvicorn` (or `gunicorn` with Uvicorn workers).
- **Reverse Proxy:** We recommend Caddy for automatic HTTPS and static file serving, but NGINX works perfectly as well.

## 1. Backend Service Configuration (Gunicorn + Uvicorn)

Because we use SQLite, you must run the application in a multi-thread single-process mode, OR ensure that only one worker writes to the database concurrently.
However, with WAL mode enabled, concurrent reads and limited concurrent writes perform exceptionally well.

**Start command (Single Worker, Multiple Threads):**
```bash
# From the backend/ directory
source .venv/bin/activate
uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1 --proxy-headers
```

*Note on multiple workers:* If you scale to `--workers 4`, SQLite WAL mode handles it fine for standard loads, but you may experience `database is locked` errors during extreme write concurrency. For TradeFlow, 1 worker with async I/O is typically sufficient for 100+ concurrent users due to the asynchronous architecture and offloaded data processing.

## 2. Production Environment Variables

You must supply a hardened `.env` file for production. See `.env.example` for details.

**Critical overrides:**
```ini
TRADEFLOW_ENVIRONMENT=production
TRADEFLOW_AUTH_SECRET=your-secure-random-32-char-string
TRADEFLOW_COOKIE_SECURE=true
TRADEFLOW_CORS_ORIGINS=["https://tradeflow.example.com"]
TRADEFLOW_FRONTEND_URL=https://tradeflow.example.com
```
*Note: The application will fail to start if `TRADEFLOW_ENVIRONMENT=production` and the secret is insecure or CORS contains a wildcard.*

## 3. Reverse Proxy (Caddy)

See the provided `Caddyfile`.

1. Install Caddy on your server.
2. Build the frontend:
   ```bash
   cd frontend
   npm run build
   ```
3. Copy the contents of `frontend/dist` to `/var/www/tradeflow/frontend/dist`.
4. Run Caddy with the `Caddyfile`. Caddy will automatically provision Let's Encrypt certificates for your domain.

## 4. Background Celery Workers (Optional but Recommended)

By default, the application runs jobs synchronously (`TRADEFLOW_JOB_EXECUTOR=sync`). 
If you process large datasets, this blocks the API response. You can configure Celery to run jobs asynchronously (requires Redis).

For local self-hosting without Redis, stick to `TRADEFLOW_JOB_EXECUTOR=sync` or use a lightweight background task runner if implemented.

## 5. Artifact Retention Policy

To prevent the local disk from filling up with old uploads and outputs, enable the retention policy in your `.env`:
```ini
TRADEFLOW_RETENTION_ENABLED=true
TRADEFLOW_RETENTION_DAYS=7
```
You should trigger the cleanup service periodically via a cron job or scheduled task calling a protected management endpoint or CLI command.
