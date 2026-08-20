"""Persisted IAM authorization entities."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel


class IAMUserPermissionEffect(StrEnum):
    """Whether a user-specific IAM permission override grants or denies access."""

    GRANT = "GRANT"
    DENY = "DENY"


class IAMUserPermissionOverride(SQLModel, table=True):
    """User-specific IAM permission grant or denial."""

    __tablename__ = "iam_user_permission_override"
    __table_args__ = (
        CheckConstraint(
            "effect IN ('GRANT', 'DENY')",
            name="ck_iam_user_permission_override_effect",
        ),
        UniqueConstraint(
            "user_id",
            "permission",
            name="uq_iam_user_permission_override_user_permission",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    permission: str = Field(nullable=False, max_length=120, index=True)
    effect: IAMUserPermissionEffect = Field(nullable=False, max_length=20)
    changed_by: int | None = Field(default=None, foreign_key="iam_user.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
