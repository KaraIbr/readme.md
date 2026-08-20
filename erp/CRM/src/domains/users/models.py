"""Read-only IAM user references used by CRM."""

from datetime import UTC, datetime

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """IAM-owned central user referenced by CRM records."""

    __tablename__ = "iam_user"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, nullable=False, max_length=255)
    full_name: str | None = Field(default=None, max_length=255)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True, nullable=False, index=True)
    failed_login_attempts: int = Field(default=0, nullable=False)
    locked_until: datetime | None = Field(default=None, nullable=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )


class IAMServiceAccess(SQLModel, table=True):
    """IAM-owned service access grant read by CRM as an entry gate."""

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
