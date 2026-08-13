"""Auth API schemas."""

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request schema for registration."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str
    organization_name: str


class LoginRequest(BaseModel):
    """Request schema for login."""

    email: EmailStr
    password: str


class AuthUserResponse(BaseModel):
    """Response schema representing an authenticated user."""

    id: str
    email: str
    display_name: str


class AuthResponse(BaseModel):
    """Response containing user data on successful auth (cookie handles token)."""

    user: AuthUserResponse
