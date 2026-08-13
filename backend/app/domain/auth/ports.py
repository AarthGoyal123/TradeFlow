"""Auth repository ports."""

from typing import Protocol

from app.domain.auth.models import Tenant, TenantMembership, User, UserIdentity


class AuthRepository(Protocol):
    """Port for authentication and authorization data access."""

    def get_user_by_email(self, email: str) -> User | None:
        """Get a user by email."""
        ...

    def get_user_by_id(self, user_id: str) -> User | None:
        """Get a user by ID."""
        ...

    def get_tenant_by_id(self, tenant_id: str) -> Tenant | None:
        """Get a tenant by ID."""
        ...

    def get_memberships_for_user(self, user_id: str) -> list[TenantMembership]:
        """Get all tenant memberships for a user."""
        ...

    def get_membership(self, user_id: str, tenant_id: str) -> TenantMembership | None:
        """Get a specific membership."""
        ...

    def create_account(self, user: User, tenant: Tenant, membership: TenantMembership, identity: UserIdentity | None = None) -> None:
        """Atomically create a tenant, user, membership, and optionally an identity."""
        ...

    def get_user_identity(self, provider: str, provider_subject: str) -> UserIdentity | None:
        """Get a specific linked external identity."""
        ...

    def create_user_identity(self, identity: UserIdentity) -> None:
        """Link an external identity to an existing user."""
        ...
