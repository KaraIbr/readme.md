"""Persisted IAM service-access entities."""

from datetime import UTC, datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class ServiceAccess(SQLModel, table=True):
    """Access grant from a central IAM user to a VERP service."""

    __tablename__ = "iam_service_access"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "service_key",
            name="uq_iam_service_access_user_service",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    service_key: str = Field(nullable=False, max_length=80, index=True)
    is_active: bool = Field(default=True, nullable=False, index=True)
    granted_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
