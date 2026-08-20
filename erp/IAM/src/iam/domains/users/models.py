"""Persisted IAM user entities."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Central VERP user account."""

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
