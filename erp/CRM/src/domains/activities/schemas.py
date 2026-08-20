from datetime import datetime

from domains.activities.models import ActivityType
from pydantic import BaseModel, ConfigDict, Field


def _normalize_required(value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("Value cannot be blank")
    return normalized


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


class ActivityCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activity_type: ActivityType
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    contact_id: int | None = Field(default=None, gt=0)
    lead_id: int | None = Field(default=None, gt=0)
    assigned_to: int | None = Field(default=None, gt=0)
    scheduled_at: datetime | None = None


class ActivityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    activity_type: ActivityType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=4000)
    assigned_to: int | None = Field(default=None, gt=0)
    scheduled_at: datetime | None = None


class ActivityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activity_type: ActivityType
    title: str
    description: str | None
    contact_id: int | None
    lead_id: int | None
    assigned_to: int | None
    scheduled_at: datetime | None
    completed_at: datetime | None
    created_by: int
    created_at: datetime
    updated_at: datetime
