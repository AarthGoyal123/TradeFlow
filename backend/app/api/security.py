"""API security dependencies."""

import logging
import uuid
from typing import Annotated

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.api.dependencies import get_auth_repository
from app.application.auth.tokens import decode_access_token
from app.domain.auth.models import User
from app.domain.auth.ports import AuthRepository

logger = logging.getLogger(__name__)


class CurrentUserContext(BaseModel):
    """Context holding the authenticated user and their active tenant."""

    user: User
    tenant_id: str | None


def get_current_user_context(
    access_token: Annotated[str | None, Cookie()] = None,
    auth_repo: AuthRepository = Depends(get_auth_repository),  # noqa: B008
) -> CurrentUserContext:
    """Dependency to retrieve the current authenticated user context from the cookie."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        payload = decode_access_token(access_token)
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )

        tenant_id = payload.get("tenant_id")

        user = auth_repo.get_user_by_id(user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return CurrentUserContext(user=user, tenant_id=tenant_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from None


def require_tenant_access(
    context: Annotated[CurrentUserContext, Depends(get_current_user_context)],
    auth_repo: AuthRepository = Depends(get_auth_repository),  # noqa: B008  # noqa: B008
) -> CurrentUserContext:
    """Dependency to enforce that the user has a valid active tenant context and membership."""
    if not context.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active organization context",
        )

    membership = auth_repo.get_membership(context.user.id, context.tenant_id)
    if not membership:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied to access this organization",
        )

    return context


def csrf_protect(
    request: Request,
    csrf_cookie: Annotated[str | None, Cookie(alias="csrf_token")] = None,
    csrf_header: Annotated[str | None, Header(alias="x-csrf-token")] = None,
) -> None:
    """Enforce Double Submit Cookie CSRF protection for state-changing requests."""
    if request.method not in ["POST", "PUT", "PATCH", "DELETE"]:
        return

    if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
        logger.warning(
            f"CSRF Failed! Cookie: {csrf_cookie}, Header: {csrf_header}, URL: {request.url}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF token validation failed",
        )


def set_csrf_cookie(response: Response) -> None:
    """Set a readable CSRF token cookie for the frontend to include in headers."""
    from app.core.settings import get_settings

    settings = get_settings()
    token = str(uuid.uuid4())
    response.set_cookie(
        key="csrf_token",
        value=token,
        httponly=False,  # MUST be False so JS can read it
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,  # type: ignore
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
    )
