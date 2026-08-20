from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


class OpportunityStage(StrEnum):
    PROSPECTING = "PROSPECTING"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"


class OpportunityOutcome(StrEnum):
    WON = "WON"
    LOST = "LOST"


class Opportunity(SQLModel, table=True):
    __tablename__ = "opportunity"
    __table_args__ = (
        CheckConstraint(
            "current_stage IN ('PROSPECTING','QUALIFIED','PROPOSAL',"
            "'NEGOTIATION','CLOSED_WON','CLOSED_LOST')",
            name="ck_opportunity_stage",
        ),
        CheckConstraint(
            "outcome IS NULL OR outcome IN ('WON','LOST')",
            name="ck_opportunity_outcome",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, max_length=255, index=True)
    contact_id: int = Field(foreign_key="contact.id", nullable=False, index=True)
    lead_id: int | None = Field(default=None, foreign_key="lead.id", index=True)
    value: float | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=3)
    current_stage: OpportunityStage = Field(
        default=OpportunityStage.PROSPECTING, nullable=False, index=True
    )
    outcome: OpportunityOutcome | None = Field(default=None, index=True)
    expected_close_date: datetime | None = Field(default=None)
    owner_id: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    notes: str | None = Field(default=None, max_length=4000)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    closed_at: datetime | None = Field(default=None)
