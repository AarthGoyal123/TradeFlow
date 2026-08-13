"""Auth API routes."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import get_auth_service
from app.api.schemas.auth import AuthResponse, AuthUserResponse, LoginRequest, RegisterRequest
from app.api.security import CurrentUserContext, get_current_user_context, set_csrf_cookie
from app.application.auth.service import AuthenticationError, AuthService, RegistrationError
from app.core.settings import get_settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


def _set_auth_cookie(response: Response, token: str) -> None:
    """Set the HTTP-only auth cookie."""
    settings = get_settings()
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_expire_minutes * 60,
    )


@router.post("/register", response_model=AuthResponse)
def register(
    request: RegisterRequest,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthResponse:
    """Register a new user and organization."""
    try:
        result = auth_service.register(
            email=request.email,
            password=request.password,
            display_name=request.display_name,
            organization_name=request.organization_name,
        )
        _set_auth_cookie(response, result.token)
        set_csrf_cookie(response)
        logger.info(f"Registered new user {result.user.id}")
        return AuthResponse(
            user=AuthUserResponse(
                id=result.user.id,
                email=result.user.email,
                display_name=result.user.display_name,
            )
        )
    except RegistrationError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Email may already be in use.",
        )


@router.post("/login", response_model=AuthResponse)
def login(
    request: LoginRequest,
    response: Response,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthResponse:
    """Authenticate and create a session."""
    try:
        result = auth_service.login(request.email, request.password)
        _set_auth_cookie(response, result.token)
        set_csrf_cookie(response)
        logger.info(f"User {result.user.id} logged in")
        return AuthResponse(
            user=AuthUserResponse(
                id=result.user.id,
                email=result.user.email,
                display_name=result.user.display_name,
            )
        )
    except AuthenticationError:
        logger.warning(f"Login failed for email {request.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )


@router.post("/logout")
def logout(response: Response) -> dict:
    """Clear the session cookie."""
    settings = get_settings()
    response.delete_cookie(
        key="access_token",
        secure=settings.cookie_secure,
        httponly=True,
        samesite=settings.cookie_samesite,
    )
    response.delete_cookie(
        key="csrf_token",
        secure=settings.cookie_secure,
        httponly=False,
        samesite=settings.cookie_samesite,
    )
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=AuthResponse)
def get_me(
    response: Response,
    context: Annotated[CurrentUserContext, Depends(get_current_user_context)],
) -> AuthResponse:
    """Return the currently authenticated user."""
    set_csrf_cookie(response)
    return AuthResponse(
        user=AuthUserResponse(
            id=context.user.id,
            email=context.user.email,
            display_name=context.user.display_name,
        )
    )
