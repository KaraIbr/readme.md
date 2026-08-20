"""CRM permissions data access functions."""

from collections.abc import Sequence
from typing import cast

from domains.permissions.models import (
    CRMUserAccess,
    CRMUserPermissionOverride,
    LeadAssignment,
    ProposalAssignment,
)
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_user_access(
    session: AsyncSession,
    user_id: int,
) -> CRMUserAccess | None:
    """Return CRM service access for one user."""

    return await session.get(CRMUserAccess, user_id)


async def count_user_accesses(session: AsyncSession) -> int:
    """Return the number of persisted CRM access rows."""

    result = await session.exec(select(CRMUserAccess.user_id))
    return len(result.all())


async def save_user_access(
    session: AsyncSession,
    access: CRMUserAccess,
) -> CRMUserAccess:
    """Persist CRM service access for one user."""

    session.add(access)
    await session.flush()
    await session.refresh(access)
    return access


async def list_user_overrides(
    session: AsyncSession,
    user_id: int,
) -> Sequence[CRMUserPermissionOverride]:
    """Return permission overrides for one user."""

    result = await session.exec(
        select(CRMUserPermissionOverride).where(CRMUserPermissionOverride.user_id == user_id)
    )
    return result.all()


async def get_user_override(
    session: AsyncSession,
    user_id: int,
    permission: str,
) -> CRMUserPermissionOverride | None:
    """Return one permission override."""

    result = await session.exec(
        select(CRMUserPermissionOverride).where(
            CRMUserPermissionOverride.user_id == user_id,
            CRMUserPermissionOverride.permission == permission,
        )
    )
    return result.first()


async def save_override(
    session: AsyncSession,
    override: CRMUserPermissionOverride,
) -> CRMUserPermissionOverride:
    """Persist a permission override."""

    session.add(override)
    await session.flush()
    await session.refresh(override)
    return override


async def delete_override(
    session: AsyncSession,
    override: CRMUserPermissionOverride,
) -> None:
    """Delete one permission override."""

    await session.delete(override)


async def list_active_proposal_assignments(
    session: AsyncSession,
    proposal_id: int,
) -> Sequence[ProposalAssignment]:
    """Return active Proposal assignments for one proposal."""

    result = await session.exec(
        select(ProposalAssignment).where(
            ProposalAssignment.proposal_id == proposal_id,
            cast(ColumnElement[bool], ProposalAssignment.is_active).is_(True),
        )
    )
    return result.all()


async def deactivate_assignment(
    session: AsyncSession,
    assignment: LeadAssignment | ProposalAssignment,
) -> None:
    """Mark an assignment as inactive with a timestamp."""

    from datetime import UTC, datetime

    assignment.is_active = False
    assignment.unassigned_at = datetime.now(UTC)
    session.add(assignment)
    await session.flush()


async def get_active_lead_assignment(
    session: AsyncSession,
    lead_id: int,
) -> LeadAssignment | None:
    """Return the active sales assignment for one Lead."""

    result = await session.exec(
        select(LeadAssignment).where(
            LeadAssignment.lead_id == lead_id,
            cast(ColumnElement[bool], LeadAssignment.is_active).is_(True),
        )
    )
    return result.first()


async def list_active_lead_assignments_for_user(
    session: AsyncSession,
    user_id: int,
) -> Sequence[LeadAssignment]:
    """Return active Lead assignments for a sales user."""

    result = await session.exec(
        select(LeadAssignment).where(
            LeadAssignment.user_id == user_id,
            cast(ColumnElement[bool], LeadAssignment.is_active).is_(True),
        )
    )
    return result.all()


async def save_lead_assignment(
    session: AsyncSession,
    assignment: LeadAssignment,
) -> LeadAssignment:
    """Persist a Lead assignment row."""

    session.add(assignment)
    await session.flush()
    await session.refresh(assignment)
    return assignment


async def get_active_proposal_assignment(
    session: AsyncSession,
    proposal_id: int,
    user_id: int,
) -> ProposalAssignment | None:
    """Return one active Proposal assignment for a technical user."""

    result = await session.exec(
        select(ProposalAssignment).where(
            ProposalAssignment.proposal_id == proposal_id,
            ProposalAssignment.user_id == user_id,
            cast(ColumnElement[bool], ProposalAssignment.is_active).is_(True),
        )
    )
    return result.first()


async def save_proposal_assignment(
    session: AsyncSession,
    assignment: ProposalAssignment,
) -> ProposalAssignment:
    """Persist a Proposal assignment row."""

    session.add(assignment)
    await session.flush()
    await session.refresh(assignment)
    return assignment
