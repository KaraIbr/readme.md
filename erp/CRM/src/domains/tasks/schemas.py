from datetime import datetime

from domains.tasks.models import TaskPriority, TaskStatus
from pydantic import BaseModel, ConfigDict, Field


class TaskStatusChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: TaskStatus


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: datetime | None = None
    contact_id: int | None = Field(default=None, gt=0)
    lead_id: int | None = Field(default=None, gt=0)
    opportunity_id: int | None = Field(default=None, gt=0)
    assigned_to: int | None = Field(default=None, gt=0)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    assigned_to: int | None = Field(default=None, gt=0)


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    completed_at: datetime | None
    contact_id: int | None
    lead_id: int | None
    opportunity_id: int | None
    assigned_to: int | None
    created_by: int
    created_at: datetime
    updated_at: datetime
