"""Persisted pipeline transition entities."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, Index
from sqlmodel import Field, SQLModel


class PipelineEntityType(StrEnum):
    """Entity types tracked by the pipeline."""

    LEAD = "lead"
    PROPOSAL = "proposal"


class StageTransition(SQLModel, table=True):
    """Immutable audit entry for one stage transition."""

    __tablename__ = "stage_transition"
    __table_args__ = (
        CheckConstraint(
            "entity_type IN ('LEAD', 'PROPOSAL')",
            name="ck_stage_transition_entity_type",
        ),
        Index(
            "ix_stage_transition_entity_time",
            "entity_type",
            "entity_id",
            "transitioned_at",
            "id",
        ),
        Index(
            "ix_stage_transition_user_time",
            "transitioned_by",
            "transitioned_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    entity_type: PipelineEntityType = Field(nullable=False, index=True)
    entity_id: int = Field(nullable=False, index=True)
    from_stage: str | None = Field(default=None, max_length=80)
    to_stage: str = Field(nullable=False, max_length=80)
    transitioned_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    transitioned_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )
    reason: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=4000)
