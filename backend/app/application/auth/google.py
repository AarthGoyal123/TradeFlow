"""Google OAuth Provider Implementation."""

import base64
import hashlib
import os
import secrets

import httpx
import jwt
from jwt import PyJWKClient

from app.core.settings import get_settings
from app.domain.auth.models import ExternalIdentity
from app.domain.auth.providers import AuthenticationProvider


class GoogleOAuthProvider(AuthenticationProvider):
    """Google implementation of the AuthenticationProvider."""

    AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
    ISSUERS = ["https://accounts.google.com", "accounts.google.com"]

    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.google_client_id:
            raise ValueError("TRADEFLOW_GOOGLE_CLIENT_ID is not configured")
        if not self.settings.google_client_secret:
            raise ValueError("TRADEFLOW_GOOGLE_CLIENT_SECRET is not configured")
        if not self.settings.google_redirect_uri:
            raise ValueError("TRADEFLOW_GOOGLE_REDIRECT_URI is not configured")

        self.client_id = self.settings.google_client_id
        self.client_secret = self.settings.google_client_secret
        self.redirect_uri = self.settings.google_redirect_uri
        self.jwks_client = PyJWKClient(self.JWKS_URL)

    @staticmethod
    def generate_pkce() -> tuple[str, str]:
        """Generate PKCE verifier and challenge."""
        code_verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode("utf-8")).digest()
        ).decode("utf-8").rstrip("=")
        return code_verifier, code_challenge

    async def get_authorization_url(self, state: str, code_challenge: str, nonce: str) -> str:
        """Return the Google OAuth authorize URL."""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "nonce": nonce,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "access_type": "online",
        }
        query_string = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTHORIZE_URL}?{query_string}"

    async def authenticate(self, code: str, code_verifier: str, expected_nonce: str) -> ExternalIdentity:
        """Exchange code for tokens and verify the ID token."""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(self.TOKEN_URL, data=data)

        if response.status_code != 200:
            raise ValueError(f"Failed to exchange code: {response.text}")

        tokens = response.json()
        id_token = tokens.get("id_token")
        if not id_token:
            raise ValueError("No id_token received from Google")

        identity = self._verify_id_token(id_token, expected_nonce)
        return identity

    def _verify_id_token(self, id_token: str, expected_nonce: str) -> ExternalIdentity:
        """Verify the Google ID token and return an ExternalIdentity."""
        signing_key = self.jwks_client.get_signing_key_from_jwt(id_token)

        try:
            payload = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=self.client_id,
            )
        except jwt.PyJWTError as e:
            raise ValueError(f"Invalid ID token: {e}")

        token_nonce = payload.get("nonce")
        if not token_nonce or not secrets.compare_digest(token_nonce, expected_nonce):
            raise ValueError("Invalid or missing nonce")

        issuer = payload.get("iss")
        if issuer not in self.ISSUERS:
            raise ValueError(f"Invalid issuer: {issuer}")

        subject = payload.get("sub")
        email = payload.get("email")
        email_verified = payload.get("email_verified", False)
        display_name = payload.get("name") or payload.get("given_name") or email.split("@")[0]

        if not subject or not email:
            raise ValueError("Missing subject or email in ID token")

        return ExternalIdentity(
            provider="google",
            subject=subject,
            email=email.lower().strip(),
            display_name=display_name,
            email_verified=email_verified,
        )
