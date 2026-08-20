from datetime import datetime

from domains.opportunities.models import OpportunityStage
from pydantic import BaseModel, ConfigDict, Field, field_validator


class OpportunityCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=255)
    contact_id: int = Field(gt=0)
    lead_id: int | None = Field(default=None, gt=0)
    value: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=3)
    expected_close_date: datetime | None = None
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return value.strip()


class OpportunityUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, min_length=1, max_length=255)
    value: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=3)
    expected_close_date: datetime | None = None
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip()


class OpportunityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    contact_id: int
    lead_id: int | None
    value: float | None
    currency: str | None
    current_stage: OpportunityStage
    outcome: str | None
    expected_close_date: datetime | None
    owner_id: int
    notes: str | None
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None


class OpportunityStageChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    stage: OpportunityStage


class OpportunityClose(BaseModel):
    model_config = ConfigDict(extra="forbid")

    outcome: str = Field(min_length=1)
    notes: str | None = Field(default=None, max_length=4000)
