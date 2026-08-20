"""Proposals domain request and response DTOs."""

from datetime import date, datetime
from decimal import Decimal

from domains.proposals.models import (
    ProposalDocumentClassification,
    ProposalStage,
    ProposalSystemType,
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


class ProposalInstallationAddress(BaseModel):
    """Structured installation address for a proposal."""

    model_config = WRITE_MODEL_CONFIG

    address_line: str | None = Field(default=None, min_length=1, max_length=500)
    city: str | None = Field(default=None, min_length=1, max_length=120)
    state: str | None = Field(default=None, min_length=1, max_length=120)
    postal_code: str | None = Field(default=None, min_length=1, max_length=30)

    @field_validator("address_line", "city", "state", "postal_code")
    @classmethod
    def normalize_optional_address(cls, value: str | None) -> str | None:
        return _normalize_optional(value)


class ProposalPVSystemPayload(BaseModel):
    """PV-specific technical payload."""

    model_config = WRITE_MODEL_CONFIG

    panel_count: int | None = Field(default=None, ge=0)
    panel_model: str | None = Field(default=None, min_length=1, max_length=255)
    panel_power: float | None = Field(default=None, gt=0)
    inverter_model: str | None = Field(default=None, min_length=1, max_length=255)
    inverter_count: int | None = Field(default=None, ge=0)
    inverter_power: float | None = Field(default=None, gt=0)
    type_of_surface: str | None = Field(default=None, min_length=1, max_length=120)
    total_power_ac: float | None = Field(default=None, gt=0)
    system_size_kw: float | None = Field(default=None, gt=0)
    oversizing_kw: float | None = Field(default=None, ge=0)
    estimated_annual_kwh: float | None = Field(default=None, gt=0)
    estimated_savings_kw: float | None = Field(default=None, ge=0)
    connection_mode: str | None = Field(default=None, min_length=1, max_length=120)
    cost_watt: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    price_watt: Decimal | None = Field(default=None, gt=0, decimal_places=4)

    @field_validator(
        "panel_model",
        "inverter_model",
        "type_of_surface",
        "connection_mode",
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional(value)


class ProposalBESSSystemPayload(BaseModel):
    """BESS-specific technical payload."""

    model_config = WRITE_MODEL_CONFIG

    battery_model: str | None = Field(default=None, min_length=1, max_length=255)
    battery_count: int | None = Field(default=None, ge=0)
    battery_power_kw: float | None = Field(default=None, gt=0)
    battery_storage_kwh: float | None = Field(default=None, gt=0)
    bess_primary_use: str | None = Field(default=None, min_length=1, max_length=120)
    technical_notes: str | None = Field(default=None, min_length=1, max_length=4000)
    cost_kwh: Decimal | None = Field(default=None, ge=0, decimal_places=4)
    price_kwh: Decimal | None = Field(default=None, gt=0, decimal_places=4)

    @field_validator("battery_model", "bess_primary_use", "technical_notes")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional(value)


class ProposalBase(BaseModel):
    """Shared common proposal fields accepted by create and update requests."""

    model_config = WRITE_MODEL_CONFIG

    version: str | None = Field(default=None, min_length=1, max_length=50)
    installation_address: ProposalInstallationAddress | None = None
    tariff: str | None = Field(default=None, min_length=1, max_length=120)
    contracted_demand: float | None = Field(default=None, gt=0)
    system_type: ProposalSystemType | None = None
    total_price: Decimal | None = Field(default=None, gt=0)
    annual_savings: Decimal | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    estimated_cost: Decimal | None = Field(default=None, ge=0)
    expected_profit: Decimal | None = Field(default=None, ge=0)
    submitted_at: datetime | None = None
    valid_until: date | None = None

    pv_system: ProposalPVSystemPayload | None = None
    bess_system: ProposalBESSSystemPayload | None = None

    @field_validator("version", "tariff")
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        return _normalize_optional(value)

    @field_validator("system_type", mode="before")
    @classmethod
    def normalize_system_type(cls, value: object) -> object:
        if isinstance(value, str):
            return _normalize_required(value).upper()
        return value

    @field_validator("currency", mode="before")
    @classmethod
    def normalize_currency(cls, value: object) -> object:
        if isinstance(value, str):
            return _normalize_optional(value.upper())
        return value


class ProposalCreate(ProposalBase):
    """Request body for creating a proposal variant."""

    lead_id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        return _normalize_required(value)


class ProposalUpdate(ProposalBase):
    """Request body for partially updating a non-terminal proposal."""

    name: str | None = Field(default=None, min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_optional_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return _normalize_required(value)


class ProposalStageChange(BaseModel):
    """Request body for moving a proposal through non-terminal stages."""

    model_config = WRITE_MODEL_CONFIG

    stage: ProposalStage

    @model_validator(mode="after")
    def validate_open_stage(self) -> ProposalStageChange:
        if self.stage in {
            ProposalStage.WON,
            ProposalStage.LOST,
            ProposalStage.SUPERSEDED,
        }:
            raise ValueError("Use a terminal proposal action for this stage")
        return self


class ProposalLost(BaseModel):
    """Request body for marking a proposal lost."""

    model_config = WRITE_MODEL_CONFIG

    loss_reason: str = Field(min_length=1, max_length=500)

    @field_validator("loss_reason")
    @classmethod
    def normalize_loss_reason(cls, value: str) -> str:
        return _normalize_required(value)


class ProposalPVSystemRead(BaseModel):
    """Public PV-specific proposal details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_id: int
    panel_count: int | None
    panel_model: str | None
    panel_power: float | None
    inverter_model: str | None
    inverter_count: int | None
    inverter_power: float | None
    type_of_surface: str | None
    total_power_ac: float | None
    system_size_kw: float | None
    oversizing_kw: float | None
    estimated_annual_kwh: float | None
    estimated_savings_kw: float | None
    connection_mode: str | None
    cost_watt: Decimal | None
    price_watt: Decimal | None


class ProposalBESSSystemRead(BaseModel):
    """Public BESS-specific proposal details."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_id: int
    battery_model: str | None
    battery_count: int | None
    battery_power_kw: float | None
    battery_storage_kwh: float | None
    bess_primary_use: str | None
    technical_notes: str | None
    cost_kwh: Decimal | None
    price_kwh: Decimal | None


class ProposalRead(BaseModel):
    """Public proposal representation."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    lead_name: str | None = None
    lead_stage: str | None = None
    name: str
    version: str | None
    installation_address: ProposalInstallationAddress
    tariff: str | None
    contracted_demand: float | None
    system_type: ProposalSystemType | None
    total_price: Decimal | None
    annual_savings: Decimal | None
    currency: str | None
    estimated_cost: Decimal | None
    expected_profit: Decimal | None
    submitted_at: datetime | None
    valid_until: date | None
    pv_system: ProposalPVSystemRead | None
    bess_system: ProposalBESSSystemRead | None
    is_complete: bool
    missing_required_fields: list[str]
    current_stage: ProposalStage
    loss_reason: str | None
    proposed_at: datetime | None
    created_by: int
    created_at: datetime


class ProposalCommercialDocumentRead(BaseModel):
    """Public metadata for a proposal commercial PDF."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_id: int
    title: str
    original_filename: str
    content_type: str | None
    size_bytes: int
    uploaded_by: int
    uploaded_at: datetime


class ProposalDocumentRead(BaseModel):
    """Public metadata for a proposal cost, technical, or other document."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    proposal_id: int
    title: str
    classification: ProposalDocumentClassification
    original_filename: str
    content_type: str | None
    size_bytes: int
    uploaded_by: int
    uploaded_at: datetime
