"""SQLAlchemy declarative models for persistence."""

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database.base import Base


class JobModel(Base):
    """SQLAlchemy model for a Job."""

    __tablename__ = "jobs"

    job_id: Mapped[str] = mapped_column(String, primary_key=True)
    template_id: Mapped[str] = mapped_column(String, nullable=False)
    original_filename: Mapped[str] = mapped_column(Text, nullable=False)
    stored_filename: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=True, index=True)
    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id"), nullable=True, index=True)


class TenantModel(Base):
    """SQLAlchemy model for a Tenant (Organization)."""

    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class UserModel(Base):
    """SQLAlchemy model for an authenticated User."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TenantMembershipModel(Base):
    """SQLAlchemy model for User's membership in a Tenant."""

    __tablename__ = "tenant_memberships"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, ForeignKey("tenants.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class JobReportModel(Base):
    """SQLAlchemy model for a processing summary report."""

    __tablename__ = "processing_reports"

    job_id: Mapped[str] = mapped_column(String, primary_key=True)
    template_id: Mapped[str] = mapped_column(String, nullable=False)
    total_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    clean_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    removed_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    needs_review_rows: Mapped[int] = mapped_column(Integer, nullable=False)
    rule_matches: Mapped[dict] = mapped_column(JSON, nullable=False)
    validation_findings: Mapped[list] = mapped_column(JSON, nullable=False)

    outputs: Mapped[list["OutputArtifactModel"]] = relationship(
        "OutputArtifactModel",
        back_populates="report",
        cascade="all, delete-orphan",
    )


class OutputArtifactModel(Base):
    """SQLAlchemy model for a generated output file."""

    __tablename__ = "processing_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(
        String, ForeignKey("processing_reports.job_id", ondelete="CASCADE"), nullable=False
    )
    output_type: Mapped[str] = mapped_column(String, nullable=False)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)

    report: Mapped["JobReportModel"] = relationship(
        "JobReportModel", back_populates="outputs"
    )


class UserIdentityModel(Base):
    """SQLAlchemy model for an external User Identity (OAuth/OIDC)."""

    __tablename__ = "user_identities"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String, nullable=False, index=True)
    provider_subject: Mapped[str] = mapped_column(String, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("provider", "provider_subject", name="uq_user_identities_provider_subject"),
    )
