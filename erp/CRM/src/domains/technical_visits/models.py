"""Persisted technical visit entities."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Optional

from sqlalchemy import CheckConstraint, Index, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class TechnicalVisitStatus(StrEnum):
    """Supported technical visit lifecycle states."""

    REQUESTED = "REQUESTED"
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TechnicalVisitAttachmentKind(StrEnum):
    """Supported technical visit evidence file kinds."""

    DOCUMENT = "DOCUMENT"
    PHOTO = "PHOTO"
    OTHER = "OTHER"


class ProposalTechnicalVisitRelationshipType(StrEnum):
    """Why a proposal is related to a technical visit."""

    BASED_ON = "BASED_ON"
    VALIDATED_BY = "VALIDATED_BY"


class TechnicalVisit(SQLModel, table=True):
    """Lead-scoped on-site technical inspection subprocess."""

    __tablename__ = "technical_visit"
    __table_args__ = (
        CheckConstraint(
            "status IN ('REQUESTED', 'SCHEDULED', 'COMPLETED', 'CANCELLED')",
            name="ck_technical_visit_status",
        ),
        CheckConstraint(
            "status != 'COMPLETED' OR completed_at IS NOT NULL",
            name="ck_technical_visit_completed_at_required",
        ),
        CheckConstraint(
            "status != 'CANCELLED' OR cancelled_at IS NOT NULL",
            name="ck_technical_visit_cancelled_at_required",
        ),
        Index(
            "ix_technical_visit_lead_status_scheduled",
            "lead_id",
            "status",
            "scheduled_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id", nullable=False, index=True)
    status: TechnicalVisitStatus = Field(
        default=TechnicalVisitStatus.REQUESTED,
        nullable=False,
        index=True,
        max_length=30,
    )
    scheduled_at: datetime | None = Field(default=None, index=True)
    receiver_name: str | None = Field(default=None, max_length=255)
    receiver_phone: str | None = Field(default=None, max_length=50)
    notes: str | None = Field(default=None, max_length=4000)
    created_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    completed_at: datetime | None = Field(default=None)
    cancelled_at: datetime | None = Field(default=None)
    cancellation_reason: str | None = Field(default=None, max_length=500)

    assignees: list["TechnicalVisitAssignee"] = Relationship(
        back_populates="visit",
    )
    proposal_links: list["ProposalTechnicalVisit"] = Relationship(
        back_populates="technical_visit",
    )


class TechnicalVisitAssignee(SQLModel, table=True):
    """Engineer or qualified visitor assigned to a technical visit."""

    __tablename__ = "technical_visit_assignee"

    id: int | None = Field(default=None, primary_key=True)
    visit_id: int = Field(foreign_key="technical_visit.id", nullable=False, index=True)
    name: str = Field(nullable=False, max_length=255, index=True)
    user_id: int | None = Field(default=None, foreign_key="iam_user.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )

    visit: Optional[TechnicalVisit] = Relationship(back_populates="assignees")


class TechnicalVisitAttachment(SQLModel, table=True):
    """Document, photo, or other evidence uploaded for a technical visit."""

    __tablename__ = "technical_visit_attachment"
    __table_args__ = (
        CheckConstraint(
            "file_kind IN ('DOCUMENT', 'PHOTO', 'OTHER')",
            name="ck_technical_visit_attachment_file_kind",
        ),
        CheckConstraint(
            "size_bytes > 0",
            name="ck_technical_visit_attachment_size_positive",
        ),
        Index(
            "ix_technical_visit_attachment_visit_uploaded",
            "visit_id",
            "uploaded_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    visit_id: int = Field(foreign_key="technical_visit.id", nullable=False, index=True)
    title: str = Field(nullable=False, max_length=255, index=True)
    file_kind: TechnicalVisitAttachmentKind = Field(
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


class ProposalTechnicalVisit(SQLModel, table=True):
    """Relationship between a proposal and technical visit evidence."""

    __tablename__ = "proposal_technical_visit"
    __table_args__ = (
        CheckConstraint(
            "relationship_type IN ('BASED_ON', 'VALIDATED_BY')",
            name="ck_proposal_technical_visit_relationship_type",
        ),
        UniqueConstraint(
            "proposal_id",
            "technical_visit_id",
            name="uq_proposal_technical_visit_pair",
        ),
        Index(
            "ix_proposal_technical_visit_proposal_linked",
            "proposal_id",
            "linked_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id", nullable=False, index=True)
    technical_visit_id: int = Field(
        foreign_key="technical_visit.id",
        nullable=False,
        index=True,
    )
    relationship_type: ProposalTechnicalVisitRelationshipType = Field(
        nullable=False,
        max_length=30,
        index=True,
    )
    notes: str | None = Field(default=None, max_length=1000)
    linked_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    linked_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )

    technical_visit: Optional[TechnicalVisit] = Relationship(
        back_populates="proposal_links",
    )
