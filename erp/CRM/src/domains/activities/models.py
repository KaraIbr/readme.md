from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


class ActivityType(StrEnum):
    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    NOTE = "NOTE"


class Activity(SQLModel, table=True):
    __tablename__ = "activity"
    __table_args__ = (
        CheckConstraint(
            "activity_type IN ('CALL', 'EMAIL', 'MEETING', 'NOTE')",
            name="ck_activity_type",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    activity_type: ActivityType = Field(nullable=False, index=True)
    title: str = Field(nullable=False, max_length=255)
    description: str | None = Field(default=None, max_length=4000)

    contact_id: int | None = Field(default=None, foreign_key="contact.id", index=True)
    lead_id: int | None = Field(default=None, foreign_key="lead.id", index=True)
    assigned_to: int | None = Field(default=None, foreign_key="iam_user.id", index=True)

    scheduled_at: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    created_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
