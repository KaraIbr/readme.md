"""Pipeline domain request and response DTOs."""

from datetime import datetime

from domains.pipeline.models import PipelineEntityType
from pydantic import BaseModel, ConfigDict, Field


class StageTransitionRead(BaseModel):
    """Public stage transition representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: PipelineEntityType
    entity_id: int
    from_stage: str | None
    to_stage: str
    transitioned_by: int
    transitioned_at: datetime
    reason: str | None
    notes: str | None


class PipelineSummary(BaseModel):
    """Compact transition summary for one entity."""

    entity_type: PipelineEntityType
    entity_id: int = Field(gt=0)
    current_stage: str
    transition_count: int = Field(ge=0)
    last_transition_at: datetime | None
