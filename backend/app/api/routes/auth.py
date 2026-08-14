"""Auth API routes."""

import logging
import secrets
from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app.api.dependencies import get_auth_service, get_google_oauth_provider
from app.api.schemas.auth import AuthResponse, AuthUserResponse, LoginRequest, RegisterRequest
from app.api.security import CurrentUserContext, get_current_user_context, set_csrf_cookie
from app.application.auth.google import GoogleOAuthProvider
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
        samesite=settings.cookie_samesite,  # type: ignore
        max_age=settings.jwt_expire_minutes * 60,
        path="/",
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
        samesite=settings.cookie_samesite,  # type: ignore
        path="/",
    )
    response.delete_cookie(
        key="csrf_token",
        secure=settings.cookie_secure,
        httponly=False,
        samesite=settings.cookie_samesite,  # type: ignore
        path="/",
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


@router.get("/google/login")
async def google_login(
    response: Response,
    oauth_provider: Annotated[GoogleOAuthProvider, Depends(get_google_oauth_provider)]
):
    """Initiate Google OAuth flow."""
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    code_verifier, code_challenge = oauth_provider.generate_pkce()
    
    settings = get_settings()
    url = await oauth_provider.get_authorization_url(state, code_challenge, nonce)
    redirect_response = RedirectResponse(url)
    
    # Store OAuth state in a short-lived secure HttpOnly cookie
    redirect_response.set_cookie(
        key="oauth_state",
        value=f"{state}:{code_verifier}:{nonce}",
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",  # type: ignore
        max_age=300, # 5 minutes
    )
    
    return redirect_response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    response: Response,
    oauth_provider: Annotated[GoogleOAuthProvider, Depends(get_google_oauth_provider)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> Any:
    """Handle Google OAuth callback."""
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    
    settings = get_settings()
    
    if not code or not state:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error=invalid_request")
        
    oauth_cookie = request.cookies.get("oauth_state")
    if not oauth_cookie:
        return RedirectResponse(url=f"{settings.frontend_url}/login?error=expired_session")
        
    redirect_response = RedirectResponse(url=f"{settings.frontend_url}/login?error=invalid_state")
    redirect_response.delete_cookie(
        key="oauth_state",
        secure=settings.cookie_secure,
        httponly=True,
        samesite="lax",  # type: ignore
    )
    
    try:
        saved_state, code_verifier, expected_nonce = oauth_cookie.split(":", 2)
    except ValueError:
        return redirect_response
        
    if not secrets.compare_digest(state, saved_state):
        return redirect_response
        
    try:
        identity = await oauth_provider.authenticate(code, code_verifier, expected_nonce)
        result = auth_service.authenticate_with_external_identity(identity)
        
        # Set normal TradeFlow session cookies on the redirect response itself
        success_response = RedirectResponse(url=f"{settings.frontend_url}/")
        
        # Clear the oauth state cookie
        success_response.delete_cookie(
            key="oauth_state",
            secure=settings.cookie_secure,
            httponly=True,
            samesite="lax",  # type: ignore
        )
        
        _set_auth_cookie(success_response, result.token)
        set_csrf_cookie(success_response)
        logger.info(f"User {result.user.id} logged in via Google OAuth")
        return success_response
        
    except (ValueError, AuthenticationError) as e:
        logger.warning(f"Google OAuth failed: {e}")
        return RedirectResponse(url=f"{settings.frontend_url}/login?error=auth_failed")

