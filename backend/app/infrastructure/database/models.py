"""SQLAlchemy declarative models for persistence."""

from datetime import datetime
from typing import List

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
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
    user_id: Mapped[str] = mapped_column(String, nullable=True)
    tenant_id: Mapped[str] = mapped_column(String, nullable=True)


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

    outputs: Mapped[List["OutputArtifactModel"]] = relationship(
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
