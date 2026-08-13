# ADR 014: Direct Google OAuth Integration

## Status
Accepted (2026-08-13)

## Context
TradeFlow requires Social Login/Google Authentication to reduce friction for new users. However, we have a strict "Zero Paid Services" constraint, meaning we cannot rely on mandatory paid SaaS providers like Clerk, Auth0, Firebase, or Supabase.

We already have a secure identity layer using Argon2id passwords and HttpOnly cookies, integrated with our own Role-Based Access Control (RBAC) and Tenant isolation models. We need a way to support Google login without adding a secondary parallel authorization architecture and without breaking our self-hosting capabilities.

## Decision
We will implement Direct Google OAuth (OIDC) natively within TradeFlow's existing backend.

1. **Authentication Flow**: The backend will initiate the OAuth flow using Proof Key for Code Exchange (PKCE) and State validation to prevent CSRF and interception attacks.
2. **Token Verification**: We will use `PyJWT[crypto]` to cryptographically verify Google's OpenID Connect ID Tokens using Google's public JSON Web Key Set (JWKS).
3. **Identity Linking**: We will introduce a `user_identities` table to store verified third-party identities (`provider` + `provider_subject`). This links multiple external accounts to a single TradeFlow `User`.
4. **Auto-Registration**: If a verified Google email does not match any existing TradeFlow user, we will automatically register a new `User`, `Tenant`, and `TenantMembership` (as `OWNER`).
5. **Session Management**: After a successful OAuth exchange, the backend will issue the same HttpOnly JWT `access_token` and double-submit `csrf_token` used by the standard password login.
6. **No Passwords**: The `users.password_hash` column is now nullable, allowing for users who exclusively use Social Login.

## Consequences
- **Positive**: Complete compliance with the Zero Paid Services constraint.
- **Positive**: TradeFlow retains full sovereignty over user data, tenant mapping, and sessions.
- **Positive**: The frontend requires minimal changes—only a new "Continue with Google" button that directs the browser to the backend OAuth initialization URL.
- **Negative**: We must manage our own OAuth Google Developer Console credentials (`TRADEFLOW_GOOGLE_CLIENT_ID` and `TRADEFLOW_GOOGLE_CLIENT_SECRET`).

## Implementation details
- **Libraries**: `httpx` for token exchange requests, `PyJWT[crypto]` for ID Token validation.
- **Security**: OAuth state and PKCE `code_verifier` are stored in a short-lived (5-minute), encrypted `oauth_state` HttpOnly cookie before redirecting to Google.
