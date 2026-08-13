"""SQLAlchemy implementation of auth repository."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.auth.models import Role, Tenant, TenantMembership, User
from app.domain.auth.ports import AuthRepository
from app.infrastructure.database.models import TenantMembershipModel, TenantModel, UserModel


class SQLAlchemyAuthRepository(AuthRepository):
    """AuthRepository implementation using SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        model = self.session.scalars(stmt).first()
        if not model:
            return None
        return self._to_user(model)

    def get_user_by_id(self, user_id: str) -> User | None:
        model = self.session.get(UserModel, user_id)
        if not model:
            return None
        return self._to_user(model)

    def get_tenant_by_id(self, tenant_id: str) -> Tenant | None:
        model = self.session.get(TenantModel, tenant_id)
        if not model:
            return None
        return Tenant(
            id=model.id,
            name=model.name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def get_memberships_for_user(self, user_id: str) -> list[TenantMembership]:
        stmt = select(TenantMembershipModel).where(TenantMembershipModel.user_id == user_id)
        models = self.session.scalars(stmt).all()
        return [self._to_membership(m) for m in models]

    def get_membership(self, user_id: str, tenant_id: str) -> TenantMembership | None:
        stmt = select(TenantMembershipModel).where(
            TenantMembershipModel.user_id == user_id,
            TenantMembershipModel.tenant_id == tenant_id
        )
        model = self.session.scalars(stmt).first()
        if not model:
            return None
        return self._to_membership(model)

    def create_account(self, user: User, tenant: Tenant, membership: TenantMembership) -> None:
        """Atomically create a tenant, user, and membership."""
        user_model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            display_name=user.display_name,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        tenant_model = TenantModel(
            id=tenant.id,
            name=tenant.name,
            created_at=tenant.created_at,
            updated_at=tenant.updated_at,
        )
        membership_model = TenantMembershipModel(
            id=membership.id,
            tenant_id=membership.tenant_id,
            user_id=membership.user_id,
            role=membership.role,
            created_at=membership.created_at,
        )

        self.session.add(user_model)
        self.session.add(tenant_model)
        self.session.add(membership_model)
        self.session.commit()

    def _to_user(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            display_name=model.display_name,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_membership(self, model: TenantMembershipModel) -> TenantMembership:
        return TenantMembership(
            id=model.id,
            tenant_id=model.tenant_id,
            user_id=model.user_id,
            role=Role(model.role),
            created_at=model.created_at,
        )
