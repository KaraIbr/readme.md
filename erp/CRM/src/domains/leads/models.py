"""Persisted lead entities."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, Index
from sqlmodel import Field, SQLModel


class LeadStage(StrEnum):
    """Supported commercial opportunity stages."""

    NEW = "NEW"
    QUALIFYING = "QUALIFYING"
    PROPOSAL_PHASE = "PROPOSAL_PHASE"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


class LeadOutcome(StrEnum):
    """Terminal lead outcomes reflected from proposal outcomes."""

    WON = "WON"
    LOST = "LOST"


class LeadInterestType(StrEnum):
    """Supported commercial interest categories for new leads."""

    PHOTOVOLTAIC = "Photovoltaic"
    BESS = "BESS"
    HIBRID = "Hibrid"


class TechnicalVisitRequirement(StrEnum):
    """Explicit decision about whether a lead needs a technical visit."""

    UNDETERMINED = "UNDETERMINED"
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED = "REQUIRED"


class LeadInteractionType(StrEnum):
    """Supported sales interaction categories for lead history."""

    CALL = "CALL"
    EMAIL = "EMAIL"
    MEETING = "MEETING"
    MESSAGE = "MESSAGE"
    NEGOTIATION = "NEGOTIATION"
    NOTE = "NOTE"


class Lead(SQLModel, table=True):
    """Bounded commercial opportunity linked to a durable contact."""

    __tablename__ = "lead"
    __table_args__ = (
        CheckConstraint(
            "interest_type IN ('PHOTOVOLTAIC', 'BESS', 'HIBRID')",
            name="ck_lead_interest_type",
        ),
        CheckConstraint(
            "qualification_score IS NULL OR "
            "(qualification_score >= 0 AND qualification_score <= 100)",
            name="ck_lead_qualification_score_range",
        ),
        CheckConstraint(
            "current_stage IN ('NEW', 'QUALIFYING', 'PROPOSAL_PHASE', 'CLOSED_WON', 'CLOSED_LOST')",
            name="ck_lead_current_stage",
        ),
        CheckConstraint(
            "outcome IS NULL OR outcome IN ('WON', 'LOST')",
            name="ck_lead_outcome",
        ),
        CheckConstraint(
            "technical_visit_requirement IN ('UNDETERMINED', 'NOT_REQUIRED', 'REQUIRED')",
            name="ck_lead_technical_visit_requirement",
        ),
        Index(
            "ix_lead_owner_stage_created",
            "owner_id",
            "current_stage",
            "created_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    contact_id: int = Field(foreign_key="contact.id", nullable=False, index=True)

    title: str = Field(nullable=False, max_length=255, index=True)
    interest_type: LeadInterestType = Field(nullable=False, max_length=120)
    qualification_score: int | None = Field(default=None, ge=0, le=100)

    current_stage: LeadStage = Field(
        default=LeadStage.NEW,
        nullable=False,
        index=True,
    )
    outcome: LeadOutcome | None = Field(default=None, index=True)

    owner_id: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    notes: str | None = Field(default=None, max_length=4000)
    technical_visit_requirement: TechnicalVisitRequirement = Field(
        default=TechnicalVisitRequirement.UNDETERMINED,
        nullable=False,
        index=True,
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    closed_at: datetime | None = Field(default=None)


class LeadDocument(SQLModel, table=True):
    """General project document uploaded against a lead."""

    __tablename__ = "lead_document"
    __table_args__ = (
        CheckConstraint("size_bytes > 0", name="ck_lead_document_size_positive"),
        Index(
            "ix_lead_document_lead_uploaded",
            "lead_id",
            "uploaded_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id", nullable=False, index=True)
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


class LeadElectricityBill(SQLModel, table=True):
    """Electricity bill uploaded against a lead for separate processing."""

    __tablename__ = "lead_electricity_bill"
    __table_args__ = (
        CheckConstraint(
            "size_bytes > 0",
            name="ck_lead_electricity_bill_size_positive",
        ),
        Index(
            "ix_lead_electricity_bill_lead_uploaded",
            "lead_id",
            "uploaded_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id", nullable=False, index=True)
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


class LeadInteraction(SQLModel, table=True):
    """Sales interaction or negotiation note documented against a lead."""

    __tablename__ = "lead_interaction"
    __table_args__ = (
        CheckConstraint(
            "interaction_type IN ('CALL', 'EMAIL', 'MEETING', 'MESSAGE', 'NEGOTIATION', 'NOTE')",
            name="ck_lead_interaction_type",
        ),
        Index(
            "ix_lead_interaction_lead_date",
            "lead_id",
            "interaction_date",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id", nullable=False, index=True)
    interaction_type: LeadInteractionType = Field(nullable=False, index=True)
    title: str = Field(nullable=False, max_length=255, index=True)
    notes: str = Field(nullable=False, max_length=4000)
    interaction_date: datetime = Field(
        nullable=False,
        index=True,
    )
    created_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
