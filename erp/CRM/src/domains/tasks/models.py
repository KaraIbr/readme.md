from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


class TaskStatus(StrEnum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class TaskPriority(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class Task(SQLModel, table=True):
    __tablename__ = "task"
    __table_args__ = (
        CheckConstraint(
            "status IN ('TODO', 'IN_PROGRESS', 'DONE', 'CANCELLED')",
            name="ck_task_status",
        ),
        CheckConstraint(
            "priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')",
            name="ck_task_priority",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    status: TaskStatus = Field(default=TaskStatus.TODO, nullable=False, index=True)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, nullable=False, index=True)

    due_date: datetime | None = Field(default=None)
    completed_at: datetime | None = Field(default=None)

    contact_id: int | None = Field(default=None, foreign_key="contact.id", index=True)
    lead_id: int | None = Field(default=None, foreign_key="lead.id", index=True)
    opportunity_id: int | None = Field(default=None, foreign_key="opportunity.id", index=True)
    assigned_to: int | None = Field(default=None, foreign_key="iam_user.id", index=True)

    created_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
