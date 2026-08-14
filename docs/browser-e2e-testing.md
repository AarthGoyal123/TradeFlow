# Browser End-to-End Testing

## The Limitation of `TestClient`
TradeFlow's backend contains over 90 automated tests utilizing FastAPI's `TestClient`. While excellent for validating business logic and database state, `TestClient` operates purely at the Python ASGI level. 

**What `TestClient` does NOT test:**
- Browser Cross-Origin Resource Sharing (CORS) policies.
- SameSite cookie enforcement (`Lax` vs `Strict` cross-site routing).
- Cross-port JavaScript security limitations (like Axios stripping CSRF headers).
- The actual Google OAuth UI/Redirect journey.

## Real Browser Verification Requirements
Because of the limitations above, an automated "PASS" from `pytest` does not guarantee the frontend application can authenticate.

Before marking any Authentication or Security architecture changes as "Production Ready", the following manual (or Playwright-automated) Browser journey must succeed:

1. **Login Page**: Load `/login`.
2. **Google OAuth**: Click "Continue with Google" and successfully authenticate.
3. **Session Establishment**: The browser must receive `access_token` and `csrf_token` cookies with `Path=/`.
4. **State Resolution**: The frontend `useAuth` hook must successfully query `GET /api/v1/auth/me` and enter an authenticated state without preemptively redirecting to `/login` during the fetch.
5. **Mutation & CSRF**: Upload a workbook to trigger `POST /api/v1/jobs`. The browser network request MUST contain both the `access_token` Cookie and the manually injected `X-CSRF-Token` Header.
6. **Success**: The API must return `201 Created` or `200 OK`, explicitly bypassing `403 Forbidden` CSRF errors.
