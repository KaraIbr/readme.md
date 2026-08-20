"""Persisted CRM authorization entities."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, Column, Enum, Index, UniqueConstraint, text
from sqlmodel import Field, SQLModel


class UserRole(StrEnum):
    """CRM role template assigned to a central VERP user for this service."""

    ADMIN = "admin"
    SALES = "sales"
    MANAGER = "manager"
    TECH = "tech"


class CRMUserPermissionEffect(StrEnum):
    """Whether a user-specific permission override grants or denies access."""

    GRANT = "grant"
    DENY = "deny"


class CRMUserAccess(SQLModel, table=True):
    """CRM service access and role for a central VERP user."""

    __tablename__ = "crm_user_access"
    __table_args__ = (
        CheckConstraint(
            "role IN ('ADMIN', 'SALES', 'MANAGER', 'TECH')",
            name="ck_crm_user_access_role",
        ),
    )

    user_id: int = Field(foreign_key="iam_user.id", primary_key=True)
    role: UserRole = Field(
        default=UserRole.SALES,
        sa_column=Column(Enum(UserRole, name="crmuserrole"), nullable=False),
    )
    is_active: bool = Field(default=True, nullable=False, index=True)
    changed_by: int | None = Field(default=None, foreign_key="iam_user.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )


class CRMUserPermissionOverride(SQLModel, table=True):
    """User-specific CRM permission grant or denial."""

    __tablename__ = "crm_user_permission_override"
    __table_args__ = (
        CheckConstraint(
            "effect IN ('GRANT', 'DENY')",
            name="ck_crm_user_permission_override_effect",
        ),
        UniqueConstraint(
            "user_id",
            "permission",
            name="uq_crm_user_permission_override_user_permission",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    permission: str = Field(nullable=False, max_length=120, index=True)
    effect: CRMUserPermissionEffect = Field(nullable=False, max_length=20)
    changed_by: int | None = Field(default=None, foreign_key="iam_user.id", index=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )


class LeadAssignment(SQLModel, table=True):
    """Assignment history for active sales follow-up on a Lead."""

    __tablename__ = "lead_assignment"
    __table_args__ = (
        Index(
            "uq_lead_assignment_one_active",
            "lead_id",
            unique=True,
            sqlite_where=text("is_active = 1"),
            postgresql_where=text("is_active = true"),
        ),
        Index(
            "ix_lead_assignment_user_active",
            "user_id",
            "is_active",
            "assigned_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    lead_id: int = Field(foreign_key="lead.id", nullable=False, index=True)
    user_id: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    assigned_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    is_active: bool = Field(default=True, nullable=False, index=True)
    assigned_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    unassigned_at: datetime | None = Field(default=None)


class ProposalAssignment(SQLModel, table=True):
    """Assignment history for technical Proposal work."""

    __tablename__ = "proposal_assignment"
    __table_args__ = (
        Index(
            "uq_proposal_assignment_active_user",
            "proposal_id",
            "user_id",
            unique=True,
            sqlite_where=text("is_active = 1"),
            postgresql_where=text("is_active = true"),
        ),
        Index(
            "ix_proposal_assignment_user_active",
            "user_id",
            "is_active",
            "assigned_at",
            "id",
        ),
    )

    id: int | None = Field(default=None, primary_key=True)
    proposal_id: int = Field(foreign_key="proposal.id", nullable=False, index=True)
    user_id: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    assigned_by: int = Field(foreign_key="iam_user.id", nullable=False, index=True)
    is_active: bool = Field(default=True, nullable=False, index=True)
    assigned_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        nullable=False,
    )
    unassigned_at: datetime | None = Field(default=None)
