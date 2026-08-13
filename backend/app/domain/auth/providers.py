"""Authentication provider abstractions."""

from typing import Protocol

from app.domain.auth.models import ExternalIdentity


class AuthenticationProvider(Protocol):
    """Port for external identity providers (e.g., Google OAuth)."""

    async def get_authorization_url(self, state: str, code_challenge: str) -> str:
        """Get the URL to redirect the user to for authentication."""
        ...

    async def authenticate(self, code: str, code_verifier: str) -> ExternalIdentity:
        """Exchange the authorization code for an external identity."""
        ...
