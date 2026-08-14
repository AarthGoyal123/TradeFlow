"""JWT Token service."""

from datetime import UTC, datetime, timedelta

import jwt

from app.core.settings import get_settings


def create_access_token(user_id: str, tenant_id: str | None = None) -> str:
    """Create a signed JWT access token."""
    settings = get_settings()
    now = datetime.now(UTC)
    expires = now + timedelta(minutes=settings.jwt_expire_minutes)

    payload = {
        "sub": user_id,
        "exp": expires,
        "iat": now,
    }
    if tenant_id:
        payload["tenant_id"] = tenant_id

    return jwt.encode(payload, settings.auth_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    """Decode a JWT access token. Raises jwt.InvalidTokenError if invalid."""
    settings = get_settings()
    return jwt.decode(token, settings.auth_secret, algorithms=["HS256"])
