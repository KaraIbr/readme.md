"""Leads domain request and response DTOs."""

from datetime import datetime

from domains.leads.models import (
    LeadInteractionType,
    LeadInterestType,
    LeadOutcome,
    LeadStage,
    TechnicalVisitRequirement,
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


class LeadCreate(BaseModel):
    """Request body for creating a lead."""

    model_config = WRITE_MODEL_CONFIG

    contact_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=255)
    interest_type: LeadInterestType
    qualification_score: int | None = Field(default=None, ge=0, le=100)
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator("title")
    @classmethod
    def normalize_required(cls, value: str) -> str:
        return _normalize_required(value)

    @field_validator("interest_type", mode="before")
    @classmethod
    def normalize_interest_type(cls, value: object) -> object:
        if isinstance(value, str):
            return _normalize_required(value)
        return value

    @field_validator("notes")
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        return _normalize_optional(value)


class LeadUpdate(BaseModel):
    """Request body for partially updating an open lead."""

    model_config = WRITE_MODEL_CONFIG

    contact_id: int | None = Field(default=None, gt=0)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    interest_type: LeadInterestType | None = None
    qualification_score: int | None = Field(default=None, ge=0, le=100)
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator("title")
    @classmethod
    def normalize_optional_required(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required(value)

    @field_validator("interest_type", mode="before")
    @classmethod
    def normalize_optional_interest_type(cls, value: object) -> object:
        if isinstance(value, str):
            return _normalize_required(value)
        return value

    @field_validator("notes")
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        return _normalize_optional(value)


class LeadClose(BaseModel):
    """Request body for manually abandoning a lead."""

    model_config = WRITE_MODEL_CONFIG

    outcome: LeadOutcome
    notes: str | None = Field(default=None, max_length=4000)

    @field_validator("notes")
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        return _normalize_optional(value)

    @model_validator(mode="after")
    def validate_manual_close_outcome(self) -> LeadClose:
        if self.outcome == LeadOutcome.WON:
            raise ValueError("WON outcomes must be produced by proposal workflows")
        return self


class LeadStageChange(BaseModel):
    """Request body for moving an open lead through pre-close stages."""

    model_config = WRITE_MODEL_CONFIG

    stage: LeadStage

    @model_validator(mode="after")
    def validate_open_stage(self) -> LeadStageChange:
        if self.stage in {LeadStage.CLOSED_WON, LeadStage.CLOSED_LOST}:
            raise ValueError("Use the close endpoint for terminal lead stages")
        return self


class LeadRead(BaseModel):
    """Public lead representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    title: str
    interest_type: LeadInterestType
    qualification_score: int | None
    current_stage: LeadStage
    outcome: LeadOutcome | None
    owner_id: int
    notes: str | None
    technical_visit_requirement: TechnicalVisitRequirement
    created_at: datetime
    closed_at: datetime | None


class LeadDocumentRead(BaseModel):
    """Public metadata for a general lead document."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    title: str
    original_filename: str
    content_type: str | None
    size_bytes: int
    uploaded_by: int
    uploaded_at: datetime


class LeadElectricityBillRead(BaseModel):
    """Public metadata for a lead electricity bill."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    title: str
    original_filename: str
    content_type: str | None
    size_bytes: int
    uploaded_by: int
    uploaded_at: datetime


class LeadInteractionCreate(BaseModel):
    """Request body for documenting a sales interaction on a lead."""

    model_config = WRITE_MODEL_CONFIG

    interaction_type: LeadInteractionType
    title: str = Field(min_length=1, max_length=255)
    notes: str = Field(min_length=1, max_length=4000)
    interaction_date: datetime

    @field_validator("interaction_type", mode="before")
    @classmethod
    def normalize_interaction_type(cls, value: object) -> object:
        if isinstance(value, str):
            return _normalize_required(value)
        return value

    @field_validator("title", "notes")
    @classmethod
    def normalize_required_text(cls, value: str) -> str:
        return _normalize_required(value)


class LeadInteractionUpdate(BaseModel):
    """Request body for updating a documented lead interaction."""

    model_config = WRITE_MODEL_CONFIG

    interaction_type: LeadInteractionType | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    notes: str | None = Field(default=None, min_length=1, max_length=4000)
    interaction_date: datetime | None = None

    @field_validator("interaction_type", mode="before")
    @classmethod
    def normalize_optional_interaction_type(cls, value: object) -> object:
        if isinstance(value, str):
            return _normalize_required(value)
        return value

    @field_validator("title", "notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required(value)


class LeadInteractionRead(BaseModel):
    """Public representation of a documented lead interaction."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    interaction_type: LeadInteractionType
    title: str
    notes: str
    interaction_date: datetime
    created_by: int
    created_at: datetime
    updated_at: datetime
