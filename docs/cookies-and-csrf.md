# Cookies & CSRF Architecture

TradeFlow utilizes a highly secure Double-Submit-Cookie pattern for Cross-Site Request Forgery (CSRF) protection alongside an `HttpOnly` JWT for authentication.

## Cookie Configuration

### 1. The Authentication Cookie (`access_token`)
- **Type**: JWT (JSON Web Token)
- **HttpOnly**: `true` (Cannot be read by JavaScript; protects against XSS)
- **Path**: `/` (Sent for all API requests to the backend)
- **SameSite**: `Lax` (Protects against cross-site POSTs but allows top-level navigations like Google OAuth redirects)
- **Secure**: `true` in Production (HTTPS), `false` in local development (HTTP)

### 2. The CSRF Token Cookie (`csrf_token`)
- **Type**: UUIDv4
- **HttpOnly**: `false` (MUST be readable by frontend JavaScript `document.cookie`)
- **Path**: `/` (Available to the frontend router regardless of the current path)
- **SameSite**: `Lax`
- **Secure**: Matches `access_token`

## The CSRF Flow (Cross-Origin Nuance)

Because the frontend (`http://localhost:5173`) and backend (`http://localhost:8000`) run on different ports during development, standard tools like `Axios` classify API calls as **Cross-Origin Requests**. 

By default, Axios's built-in `xsrfCookieName` and `xsrfHeaderName` features **will silently fail to attach the CSRF header on cross-origin requests** as a security precaution.

To bypass this and correctly fulfill the Double-Submit-Cookie requirement:
1. The frontend uses a custom Axios `requestInterceptor` (`frontend/src/api/interceptors.ts`).
2. The interceptor manually reads `document.cookie` using a regex.
3. The interceptor forcefully injects the `X-CSRF-Token` header.
4. The backend `csrf_protect` FastAPI dependency validates that the `csrf_token` cookie precisely matches the `X-CSRF-Token` header.

## Troubleshooting

- **403 Forbidden on POSTs**: The CSRF token was not sent. Check if the frontend interceptor is running, and verify the `csrf_token` cookie exists with `Path=/` in the browser devtools.
- **401 Unauthorized**: The `access_token` cookie is missing, expired, or the signature is invalid. Ensure `withCredentials: true` is set on the API client.
