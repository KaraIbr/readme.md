"""Persisted auth entities."""

from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class TokenBlacklist(SQLModel, table=True):
    """Revoked JWT tokens tracked by their unique JWT ID (jti)."""

    __tablename__ = "iam_token_blacklist"

    id: int | None = Field(default=None, primary_key=True)
    jti: str = Field(nullable=False, max_length=512, index=True, unique=True)
    expires_at: datetime = Field(nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
