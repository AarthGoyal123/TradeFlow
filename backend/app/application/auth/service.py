"""Authentication application service."""

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from app.application.auth.password import hash_password, verify_password
from app.application.auth.tokens import create_access_token
from app.core.errors import TradeFlowError
from app.domain.auth.models import (
    ExternalIdentity,
    Role,
    Tenant,
    TenantMembership,
    User,
    UserIdentity,
)
from app.domain.auth.ports import (
    AccountAlreadyExistsError,
    AuthRepository,
    IdentityAlreadyExistsError,
)


class AuthenticationError(TradeFlowError):
    """Exception raised for authentication failures."""

    pass


class RegistrationError(TradeFlowError):
    """Exception raised for registration failures."""

    pass


@dataclass
class AuthResult:
    """Result of a successful authentication."""

    user: User
    token: str


class AuthService:
    """Service handling registration and login."""

    def __init__(self, auth_repository: AuthRepository) -> None:
        self.auth_repo = auth_repository

    def register(
        self, email: str, password: str, display_name: str, organization_name: str
    ) -> AuthResult:
        """Register a new user and tenant atomically."""
        email = email.lower().strip()
        if not email or not password:
            raise RegistrationError("Email and password are required")

        existing_user = self.auth_repo.get_user_by_email(email)
        if existing_user:
            # DO NOT LEAK that the email exists in a public API unless design dictates.
            # However, for registration forms it is common to return a 400.
            raise RegistrationError("Registration failed")

        now = datetime.now(UTC)
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            password_hash=hash_password(password),
            display_name=display_name.strip() or email.split("@")[0],
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=organization_name.strip() or "My Organization",
            created_at=now,
            updated_at=now,
        )

        membership = TenantMembership(
            id=str(uuid.uuid4()),
            tenant_id=tenant.id,
            user_id=user.id,
            role=Role.OWNER,
            created_at=now,
        )

        self.auth_repo.create_account(user, tenant, membership)

        # Issue token for the newly created user & tenant
        token = create_access_token(user.id, tenant.id)
        return AuthResult(user=user, token=token)

    def login(self, email: str, password: str) -> AuthResult:
        """Authenticate a user and return a token."""
        user = self.auth_repo.get_user_by_email(email.lower().strip())
        if not user or not user.is_active:
            raise AuthenticationError("Invalid email or password")

        if not verify_password(password, user.password_hash or ""):
            raise AuthenticationError("Invalid email or password")

        memberships = self.auth_repo.get_memberships_for_user(user.id)
        # Default to first tenant if multiple (or require explicit selection later)
        tenant_id = memberships[0].tenant_id if memberships else None

        token = create_access_token(user.id, tenant_id)
        return AuthResult(user=user, token=token)

    def authenticate_with_external_identity(self, external: ExternalIdentity) -> AuthResult:
        """Authenticate using an external identity, registering or linking as needed."""
        # 1. Check if identity already linked
        user_identity = self.auth_repo.get_user_identity(external.provider, external.subject)
        if user_identity:
            user = self.auth_repo.get_user_by_id(user_identity.user_id)
            if not user or not user.is_active:
                raise AuthenticationError("Account disabled or missing") from None
            return self._issue_token(user)

        # 2. Check if a user exists with this verified email
        if not external.email_verified:
            raise AuthenticationError("External email must be verified to link or register")

        user = self.auth_repo.get_user_by_email(external.email)
        now = datetime.now(UTC)

        if user:
            if not user.is_active:
                raise AuthenticationError("Account disabled")
            # Link the identity
            new_identity = UserIdentity(
                id=str(uuid.uuid4()),
                user_id=user.id,
                provider=external.provider,
                provider_subject=external.subject,
                email=external.email,
                created_at=now,
                updated_at=now,
            )
            try:
                self.auth_repo.create_user_identity(new_identity)
            except IdentityAlreadyExistsError:
                # Concurrent request linked this identity. Re-query.
                user_identity = self.auth_repo.get_user_identity(
                    external.provider, external.subject
                )
                if user_identity:
                    user = self.auth_repo.get_user_by_id(user_identity.user_id)
                    if not user or not user.is_active:
                        raise AuthenticationError("Account disabled or missing") from None
                    return self._issue_token(user)
                raise AuthenticationError("Concurrent identity linking failed") from None
            return self._issue_token(user)

        # 3. New user -> Auto register
        user = User(
            id=str(uuid.uuid4()),
            email=external.email,
            password_hash=None,
            display_name=external.display_name,
            is_active=True,
            created_at=now,
            updated_at=now,
        )

        tenant = Tenant(
            id=str(uuid.uuid4()),
            name=f"{external.display_name}'s Organization",
            created_at=now,
            updated_at=now,
        )

        membership = TenantMembership(
            id=str(uuid.uuid4()),
            tenant_id=tenant.id,
            user_id=user.id,
            role=Role.OWNER,
            created_at=now,
        )

        identity = UserIdentity(
            id=str(uuid.uuid4()),
            user_id=user.id,
            provider=external.provider,
            provider_subject=external.subject,
            email=external.email,
            created_at=now,
            updated_at=now,
        )

        try:
            self.auth_repo.create_account(user, tenant, membership, identity=identity)
        except AccountAlreadyExistsError:
            # Re-query if concurrent creation succeeded
            user_identity = self.auth_repo.get_user_identity(external.provider, external.subject)
            if user_identity:
                existing_user = self.auth_repo.get_user_by_id(user_identity.user_id)
                if not existing_user or not existing_user.is_active:
                    raise AuthenticationError("Account disabled or missing") from None
                return self._issue_token(existing_user)
            raise RegistrationError("Concurrent registration failed") from None

        return self._issue_token(user)

    def _issue_token(self, user: User) -> AuthResult:
        memberships = self.auth_repo.get_memberships_for_user(user.id)
        tenant_id = memberships[0].tenant_id if memberships else None
        token = create_access_token(user.id, tenant_id)
        return AuthResult(user=user, token=token)
