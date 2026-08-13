"""Authentication and Authorization domain models."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class Role(StrEnum):
    """Supported RBAC roles within a tenant."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


@dataclass(frozen=True, slots=True)
class Tenant:
    """A distinct organization isolating jobs, files, and users."""

    id: str
    name: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class User:
    """An authenticated user of the system."""

    id: str
    email: str
    password_hash: str | None
    display_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class TenantMembership:
    """Association between a User and a Tenant with a specific role."""

    id: str
    tenant_id: str
    user_id: str
    role: Role
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ExternalIdentity:
    """An identity verified by an external provider."""

    provider: str
    subject: str
    email: str
    display_name: str
    email_verified: bool


@dataclass(frozen=True, slots=True)
class UserIdentity:
    """A linked external identity for a TradeFlow User."""

    id: str
    user_id: str
    provider: str
    provider_subject: str
    email: str
    created_at: datetime
    updated_at: datetime
