"""Technical visit domain request and response DTOs."""

from datetime import datetime

from domains.leads.models import TechnicalVisitRequirement
from domains.technical_visits.models import (
    ProposalTechnicalVisitRelationshipType,
    TechnicalVisitAttachmentKind,
    TechnicalVisitStatus,
)
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

WRITE_MODEL_CONFIG = ConfigDict(extra="forbid")


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


class TechnicalVisitRequirementUpdate(BaseModel):
    """Request body for setting the Lead technical visit requirement."""

    model_config = WRITE_MODEL_CONFIG

    requirement: TechnicalVisitRequirement


class TechnicalVisitAssigneePayload(BaseModel):
    """Assignee payload used when scheduling or updating a visit."""

    model_config = WRITE_MODEL_CONFIG

    name: str = Field(min_length=1, max_length=255)
    user_id: int | None = Field(default=None, gt=0)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _normalize_required(value)


class TechnicalVisitCreate(BaseModel):
    """Request body for creating a lead-scoped technical visit."""

    model_config = WRITE_MODEL_CONFIG

    scheduled_at: datetime | None = None
    receiver_name: str | None = Field(default=None, min_length=1, max_length=255)
    receiver_phone: str | None = Field(default=None, min_length=1, max_length=50)
    notes: str | None = Field(default=None, max_length=4000)
    assignees: list[TechnicalVisitAssigneePayload] = Field(default_factory=list)

    @field_validator("receiver_name", "receiver_phone")
    @classmethod
    def normalize_optional_required(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required(value)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional(value)

    @model_validator(mode="after")
    def validate_schedule_shape(self) -> TechnicalVisitCreate:
        schedule_parts = (
            self.scheduled_at is not None,
            self.receiver_name is not None,
            self.receiver_phone is not None,
            bool(self.assignees),
        )
        if any(schedule_parts) and not all(schedule_parts):
            raise ValueError(
                "scheduled_at, receiver_name, receiver_phone, and at least one "
                "assignee are required to schedule a visit"
            )
        return self


class TechnicalVisitUpdate(BaseModel):
    """Request body for partially updating a requested or scheduled visit."""

    model_config = WRITE_MODEL_CONFIG

    scheduled_at: datetime | None = None
    receiver_name: str | None = Field(default=None, min_length=1, max_length=255)
    receiver_phone: str | None = Field(default=None, min_length=1, max_length=50)
    notes: str | None = Field(default=None, max_length=4000)
    assignees: list[TechnicalVisitAssigneePayload] | None = None

    @field_validator("receiver_name", "receiver_phone")
    @classmethod
    def normalize_optional_required(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required(value)

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional(value)


class TechnicalVisitCancel(BaseModel):
    """Request body for cancelling a technical visit."""

    model_config = WRITE_MODEL_CONFIG

    reason: str | None = Field(default=None, max_length=500)

    @field_validator("reason")
    @classmethod
    def normalize_reason(cls, value: str | None) -> str | None:
        return _normalize_optional(value)


class TechnicalVisitAssigneeRead(BaseModel):
    """Public technical visit assignee representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    name: str
    user_id: int | None
    created_at: datetime


class TechnicalVisitRead(BaseModel):
    """Public technical visit representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    status: TechnicalVisitStatus
    scheduled_at: datetime | None
    receiver_name: str | None
    receiver_phone: str | None
    notes: str | None
    created_by: int
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None
    assignees: list[TechnicalVisitAssigneeRead] = Field(default_factory=list)


class TechnicalVisitAttachmentRead(BaseModel):
    """Public metadata for technical visit evidence."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    visit_id: int
    title: str
    file_kind: TechnicalVisitAttachmentKind
    original_filename: str
    content_type: str | None
    size_bytes: int
    uploaded_by: int
    uploaded_at: datetime


class ProposalTechnicalVisitCreate(BaseModel):
    """Request body for linking a proposal to technical visit evidence."""

    model_config = WRITE_MODEL_CONFIG

    technical_visit_id: int = Field(gt=0)
    relationship_type: ProposalTechnicalVisitRelationshipType
    notes: str | None = Field(default=None, max_length=1000)

    @field_validator("relationship_type", mode="before")
    @classmethod
    def normalize_relationship_type(cls, value: object) -> object:
        if isinstance(value, str):
            return _normalize_required(value).upper()
        return value

    @field_validator("notes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        return _normalize_optional(value)


class ProposalTechnicalVisitRead(BaseModel):
    """Public Proposal-to-TechnicalVisit relationship representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_id: int
    technical_visit_id: int
    relationship_type: ProposalTechnicalVisitRelationshipType
    notes: str | None
    linked_by: int
    linked_at: datetime
