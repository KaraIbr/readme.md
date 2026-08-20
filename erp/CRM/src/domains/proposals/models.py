"""Persisted proposal entities."""

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any, Optional

from domains.leads.models import Lead
from sqlalchemy import CheckConstraint, Index, text
from sqlmodel import Field, Relationship, SQLModel


class ProposalStage(StrEnum):
    """Supported technical proposal stages."""

    DRAFT = "DRAFT"
    SENT = "SENT"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"
    SUPERSEDED = "SUPERSEDED"


class ProposalSystemType(StrEnum):
    """Supported proposal system families."""

    PV = "PV"
    BESS = "BESS"
    HIBRID = "HIBRID"


class ProposalDocumentClassification(StrEnum):
    """Supported non-commercial proposal document classifications."""

    COSTS = "Costs"
    TECHNICAL = "Technical"
    OTHER = "Other"


COMMON_COMPLETION_FIELDS = (
    "version",
    "installation_address_line",
    "installation_city",
    "installation_state",
    "installation_postal_code",
    "tariff",
    "contracted_demand",
    "system_type",
    "total_price",
    "annual_savings",
    "currency",
    "estimated_cost",
    "expected_profit",
    "submitted_at",
    "valid_until",
)

PV_COMPLETION_FIELDS = (
    "panel_count",
    "panel_model",
    "panel_power",
    "inverter_model",
    "inverter_count",
    "inverter_power",
    "type_of_surface",
    "total_power_ac",
    "system_size_kw",
    "oversizing_kw",
    "estimated_annual_kwh",
    "estimated_savings_kw",
    "connection_mode",
    "cost_watt",
    "price_watt",
)

BESS_COMPLETION_FIELDS = (
    "battery_model",
    "battery_count",
    "battery_power_kw",
    "battery_storage_kwh",
    "bess_primary_use",
    "technical_notes",
    "cost_kwh",
    "price_kwh",
)

MISSING_FIELD_LABELS = {
    "installation_address_line": "installation_address.address_line",
    "installation_city": "installation_address.city",
    "installation_state": "installation_address.state",
    "installation_postal_code": "installation_address.postal_code",
}


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _missing_from_object(prefix: str, field_names: tuple[str, ...], obj: Any) -> list[str]:
    if obj is None:
        return [f"{prefix}.{field_name}" for field_name in field_names]
    return [
        f"{prefix}.{field_name}"
        for field_name in field_names
        if not _is_present(getattr(obj, field_name))
    ]


def missing_required_fields(proposal: "Proposal") -> list[str]:
    """Return fields required before a proposal can leave draft."""

    pv_system = proposal.__dict__.get("pv_system")
    bess_system = proposal.__dict__.get("bess_system")
    missing = [
        MISSING_FIELD_LABELS.get(field_name, field_name)
        for field_name in COMMON_COMPLETION_FIELDS
        if not _is_present(getattr(proposal, field_name))
    ]
    if proposal.system_type in {ProposalSystemType.PV, ProposalSystemType.HIBRID}:
        missing.extend(_missing_from_object("pv_system", PV_COMPLETION_FIELDS, pv_system))
    if proposal.system_type in {ProposalSystemType.BESS, ProposalSystemType.HIBRID}:
        missing.extend(_missing_from_object("bess_system", BESS_COMPLETION_FIELDS, bess_system))
    return missing


class Proposal(SQLModel, table=True):
    """Common commercial proposal header for a lead."""

    __tablename__ = "proposal"
    __table_args__ = (
        CheckConstraint(
            "system_type IS NULL OR system_type IN ('PV', 'BESS', 'HIBRID')",
            name="ck_proposal_system_type",
        ),
        CheckConstraint(
            "contracted_demand IS NULL OR contracted_demand > 0",
            name="ck_proposal_contracted_demand_positive",
        ),
        CheckConstraint(
            "total_price IS NULL OR total_price > 0",
            name="ck_proposal_total_price_positive",
        ),
        CheckConstraint(
            "annual_savings IS NULL OR annual_savings >= 0",
            name="ck_proposal_annual_savings_nonnegative",
        ),
        CheckConstraint(
            "currency IS NULL OR length(currency) = 3",
            name="ck_proposal_currency_length",
        ),
        CheckConstraint(
            "estimated_cost IS NULL OR estimated_cost >= 0",
            name="ck_proposal_estimated_cost_nonnegative",
        ),
        CheckConstraint(
            "expected_profit IS NULL OR expected_profit >= 0",
            name="ck_proposal_expected_profit_nonnegative",
        ),
        CheckConstraint(
            "current_stage IN ('DRAFT', 'SENT', 'NEGOTIATION', 'WON', 'LOST', 'SUPERSEDED')",
            name="ck_proposal_current_stage",
        ),
        CheckConstraint(
            "current_stage != 'LOST' OR "
            "(loss_reason IS NOT NULL AND length(trim(loss_reason)) > 0)",
            name="ck_proposal_lost_requires_reason",
        ),
        Index(
            "ix_proposal_user_stage_created",
            "created_by",
            "current_stage",
            "created_at",
            "id",
        ),
        Index("ix_proposal_lead_stage", "lead_id", "current_stage"),
        Index(
            "uq_proposal_one_won_per_lead",
            "lead_id",
            unique=True,
            sqlite_where=text("current_stage = 'WON'"),
            postgresql_where=text("current_stage = 'WON'"),
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id", nullable=False, index=True)

    name: str = Field(nullable=False, max_length=255, index=True)
    version: str | None = Field(default=None, max_length=50)

    installation_address_line: str | None = Field(default=None, max_length=500)
    installation_city: str | None = Field(default=None, max_length=120)
    installation_state: str | None = Field(default=None, max_length=120)
    installation_postal_code: str | None = Field(default=None, max_length=30)

    tariff: str | None = Field(default=None, max_length=120)
    contracted_demand: float | None = Field(default=None, gt=0)
    system_type: ProposalSystemType | None = Field(
        default=None,
        max_length=20,
        index=True,
    )

    total_price: Decimal | None = Field(
        default=None,
        max_digits=14,
        decimal_places=2,
    )
    annual_savings: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=14,
        decimal_places=2,
    )
    currency: str | None = Field(default=None, max_length=3)
    estimated_cost: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=14,
        decimal_places=2,
    )
    expected_profit: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=14,
        decimal_places=2,
    )
    submitted_at: datetime | None = Field(default=None, index=True)
    valid_until: date | None = Field(default=None, index=True)

    current_stage: ProposalStage = Field(
        default=ProposalStage.DRAFT,
        nullable=False,
        index=True,
    )
    loss_reason: str | None = Field(default=None, max_length=500)

    proposed_at: datetime | None = Field(default=None)
    created_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )

    lead: Optional["Lead"] = Relationship(
        sa_relationship_kwargs={"uselist": False},
    )
    pv_system: Optional["ProposalPVSystem"] = Relationship(
        back_populates="proposal",
        sa_relationship_kwargs={"uselist": False},
    )
    bess_system: Optional["ProposalBESSSystem"] = Relationship(
        back_populates="proposal",
        sa_relationship_kwargs={"uselist": False},
    )

    @property
    def installation_address(self) -> dict[str, str | None]:
        """Return the API-facing installation address object."""

        return {
            "address_line": self.installation_address_line,
            "city": self.installation_city,
            "state": self.installation_state,
            "postal_code": self.installation_postal_code,
        }

    @property
    def missing_required_fields(self) -> list[str]:
        """Fields missing before this proposal can advance beyond draft."""

        return missing_required_fields(self)

    @property
    def is_complete(self) -> bool:
        """Whether the proposal has every required field for its system type."""

        return not self.missing_required_fields

    @property
    def lead_name(self) -> str | None:
        """Resolved lead title for display, loaded via selectinload."""

        if self.lead is None:
            return None
        return self.lead.title

    @property
    def lead_stage(self) -> str | None:
        """Resolved lead current_stage for display, loaded via selectinload."""

        if self.lead is None:
            return None
        return self.lead.current_stage


class ProposalPVSystem(SQLModel, table=True):
    """PV-specific technical details for a proposal."""

    __tablename__ = "proposal_pv_system"
    __table_args__ = (
        CheckConstraint(
            "panel_count IS NULL OR panel_count >= 0",
            name="ck_proposal_pv_panel_count_nonnegative",
        ),
        CheckConstraint(
            "panel_power IS NULL OR panel_power > 0",
            name="ck_proposal_pv_panel_power_positive",
        ),
        CheckConstraint(
            "inverter_count IS NULL OR inverter_count >= 0",
            name="ck_proposal_pv_inverter_count_nonnegative",
        ),
        CheckConstraint(
            "inverter_power IS NULL OR inverter_power > 0",
            name="ck_proposal_pv_inverter_power_positive",
        ),
        CheckConstraint(
            "total_power_ac IS NULL OR total_power_ac > 0",
            name="ck_proposal_pv_total_power_ac_positive",
        ),
        CheckConstraint(
            "system_size_kw IS NULL OR system_size_kw > 0",
            name="ck_proposal_pv_system_size_kw_positive",
        ),
        CheckConstraint(
            "oversizing_kw IS NULL OR oversizing_kw >= 0",
            name="ck_proposal_pv_oversizing_kw_nonnegative",
        ),
        CheckConstraint(
            "estimated_annual_kwh IS NULL OR estimated_annual_kwh > 0",
            name="ck_proposal_pv_estimated_annual_kwh_positive",
        ),
        CheckConstraint(
            "estimated_savings_kw IS NULL OR estimated_savings_kw >= 0",
            name="ck_proposal_pv_estimated_savings_kw_nonnegative",
        ),
        CheckConstraint(
            "cost_watt IS NULL OR cost_watt >= 0",
            name="ck_proposal_pv_cost_watt_nonnegative",
        ),
        CheckConstraint(
            "price_watt IS NULL OR price_watt > 0",
            name="ck_proposal_pv_price_watt_positive",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(
        foreign_key="proposal.id",
        nullable=False,
        index=True,
        unique=True,
    )
    panel_count: int | None = Field(default=None, ge=0)
    panel_model: str | None = Field(default=None, max_length=255)
    panel_power: float | None = Field(default=None, gt=0)
    inverter_model: str | None = Field(default=None, max_length=255)
    inverter_count: int | None = Field(default=None, ge=0)
    inverter_power: float | None = Field(default=None, gt=0)
    type_of_surface: str | None = Field(default=None, max_length=120)
    total_power_ac: float | None = Field(default=None, gt=0)
    system_size_kw: float | None = Field(default=None, gt=0)
    oversizing_kw: float | None = Field(default=None, ge=0)
    estimated_annual_kwh: float | None = Field(default=None, gt=0)
    estimated_savings_kw: float | None = Field(default=None, ge=0)
    connection_mode: str | None = Field(default=None, max_length=120)
    cost_watt: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=14,
        decimal_places=4,
    )
    price_watt: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=14,
        decimal_places=4,
    )

    proposal: Optional[Proposal] = Relationship(back_populates="pv_system")


class ProposalBESSSystem(SQLModel, table=True):
    """BESS-specific technical details for a proposal."""

    __tablename__ = "proposal_bess_system"
    __table_args__ = (
        CheckConstraint(
            "battery_count IS NULL OR battery_count >= 0",
            name="ck_proposal_bess_battery_count_nonnegative",
        ),
        CheckConstraint(
            "battery_power_kw IS NULL OR battery_power_kw > 0",
            name="ck_proposal_bess_battery_power_kw_positive",
        ),
        CheckConstraint(
            "battery_storage_kwh IS NULL OR battery_storage_kwh > 0",
            name="ck_proposal_bess_battery_storage_kwh_positive",
        ),
        CheckConstraint(
            "cost_kwh IS NULL OR cost_kwh >= 0",
            name="ck_proposal_bess_cost_kwh_nonnegative",
        ),
        CheckConstraint(
            "price_kwh IS NULL OR price_kwh > 0",
            name="ck_proposal_bess_price_kwh_positive",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(
        foreign_key="proposal.id",
        nullable=False,
        index=True,
        unique=True,
    )
    battery_model: str | None = Field(default=None, max_length=255)
    battery_count: int | None = Field(default=None, ge=0)
    battery_power_kw: float | None = Field(default=None, gt=0)
    battery_storage_kwh: float | None = Field(default=None, gt=0)
    bess_primary_use: str | None = Field(default=None, max_length=120)
    technical_notes: str | None = Field(default=None, max_length=4000)
    cost_kwh: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=14,
        decimal_places=4,
    )
    price_kwh: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=14,
        decimal_places=4,
    )

    proposal: Optional[Proposal] = Relationship(back_populates="bess_system")


class ProposalCommercialDocument(SQLModel, table=True):
    """Commercial proposal PDF sent or intended to be sent to the customer."""

    __tablename__ = "proposal_commercial_document"
    __table_args__ = (
        CheckConstraint(
            "size_bytes > 0",
            name="ck_proposal_commercial_document_size_positive",
        ),
        Index(
            "ix_proposal_commercial_document_proposal_uploaded",
            "proposal_id",
            "uploaded_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id", nullable=False, index=True)
    title: str = Field(nullable=False, max_length=255, index=True)
    original_filename: str = Field(nullable=False, max_length=255)
    content_type: str | None = Field(default=None, max_length=120)
    stored_path: str = Field(nullable=False, max_length=500)
    size_bytes: int = Field(nullable=False, ge=1)
    uploaded_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )


class ProposalDocument(SQLModel, table=True):
    """Cost, technical, or other internal document attached to a proposal."""

    __tablename__ = "proposal_document"
    __table_args__ = (
        CheckConstraint(
            "classification IN ('COSTS', 'TECHNICAL', 'OTHER')",
            name="ck_proposal_document_classification",
        ),
        CheckConstraint(
            "size_bytes > 0",
            name="ck_proposal_document_size_positive",
        ),
        Index(
            "ix_proposal_document_proposal_uploaded",
            "proposal_id",
            "uploaded_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id", nullable=False, index=True)
    title: str = Field(nullable=False, max_length=255, index=True)
    classification: ProposalDocumentClassification = Field(
        nullable=False,
        max_length=30,
        index=True,
    )
    original_filename: str = Field(nullable=False, max_length=255)
    content_type: str | None = Field(default=None, max_length=120)
    stored_path: str = Field(nullable=False, max_length=500)
    size_bytes: int = Field(nullable=False, ge=1)
    uploaded_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    uploaded_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
