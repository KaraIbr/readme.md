"""Technical visits data access functions."""

from collections.abc import Sequence
from typing import Any, cast

from domains.leads.models import Lead
from domains.technical_visits.models import (
    ProposalTechnicalVisit,
    TechnicalVisit,
    TechnicalVisitAssignee,
    TechnicalVisitAttachment,
    TechnicalVisitStatus,
)
from sqlalchemy import desc, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def create_visit(session: AsyncSession, visit: TechnicalVisit) -> TechnicalVisit:
    """Persist a technical visit."""

    session.add(visit)
    await session.flush()
    await session.refresh(visit)
    return visit


async def get_visit(session: AsyncSession, visit_id: int) -> TechnicalVisit | None:
    """Return a technical visit with its assignees by primary key."""

    statement = (
        select(TechnicalVisit)
        .options(selectinload(cast(Any, TechnicalVisit.assignees)))
        .where(TechnicalVisit.id == visit_id)
    )
    result = await session.exec(statement)
    return result.first()


async def list_visits_for_lead(
    session: AsyncSession,
    lead_id: int,
    *,
    status: TechnicalVisitStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[TechnicalVisit]:
    """Return technical visits attached to one lead."""

    statement = (
        select(TechnicalVisit)
        .options(selectinload(cast(Any, TechnicalVisit.assignees)))
        .where(TechnicalVisit.lead_id == lead_id)
        .order_by(
            desc(cast(ColumnElement[Any], TechnicalVisit.scheduled_at)),
            desc(cast(ColumnElement[Any], TechnicalVisit.created_at)),
            desc(cast(ColumnElement[Any], TechnicalVisit.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if status is not None:
        statement = statement.where(TechnicalVisit.status == status)

    result = await session.exec(statement)
    return result.all()


async def list_visits_for_owner(
    session: AsyncSession,
    owner_id: int,
    *,
    lead_id: int | None = None,
    status: TechnicalVisitStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[TechnicalVisit]:
    """Return technical visits for leads owned by a user."""

    statement = (
        select(TechnicalVisit)
        .options(selectinload(cast(Any, TechnicalVisit.assignees)))
        .join(
            Lead,
            cast(ColumnElement[Any], TechnicalVisit.lead_id) == cast(ColumnElement[Any], Lead.id),
        )
        .where(Lead.owner_id == owner_id)
        .order_by(
            desc(cast(ColumnElement[Any], TechnicalVisit.scheduled_at)),
            desc(cast(ColumnElement[Any], TechnicalVisit.created_at)),
            desc(cast(ColumnElement[Any], TechnicalVisit.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if lead_id is not None:
        statement = statement.where(TechnicalVisit.lead_id == lead_id)
    if status is not None:
        statement = statement.where(TechnicalVisit.status == status)

    result = await session.exec(statement)
    return result.all()


async def list_all_visits(
    session: AsyncSession,
    *,
    lead_id: int | None = None,
    status: TechnicalVisitStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[TechnicalVisit]:
    """Return technical visits across all users."""

    statement = (
        select(TechnicalVisit)
        .options(selectinload(cast(Any, TechnicalVisit.assignees)))
        .order_by(
            desc(cast(ColumnElement[Any], TechnicalVisit.scheduled_at)),
            desc(cast(ColumnElement[Any], TechnicalVisit.created_at)),
            desc(cast(ColumnElement[Any], TechnicalVisit.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if lead_id is not None:
        statement = statement.where(TechnicalVisit.lead_id == lead_id)
    if status is not None:
        statement = statement.where(TechnicalVisit.status == status)

    result = await session.exec(statement)
    return result.all()


async def list_visits_for_assignee_or_creator(
    session: AsyncSession,
    user_id: int,
    *,
    lead_id: int | None = None,
    status: TechnicalVisitStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[TechnicalVisit]:
    """Return technical visits assigned to or created by one user."""

    assigned_visit_ids = select(TechnicalVisitAssignee.visit_id).where(
        TechnicalVisitAssignee.user_id == user_id
    )
    statement = (
        select(TechnicalVisit)
        .options(selectinload(cast(Any, TechnicalVisit.assignees)))
        .where(
            or_(
                cast(ColumnElement[Any], TechnicalVisit.created_by) == user_id,
                cast(ColumnElement[Any], TechnicalVisit.id).in_(assigned_visit_ids),
            )
        )
        .order_by(
            desc(cast(ColumnElement[Any], TechnicalVisit.scheduled_at)),
            desc(cast(ColumnElement[Any], TechnicalVisit.created_at)),
            desc(cast(ColumnElement[Any], TechnicalVisit.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if lead_id is not None:
        statement = statement.where(TechnicalVisit.lead_id == lead_id)
    if status is not None:
        statement = statement.where(TechnicalVisit.status == status)

    result = await session.exec(statement)
    return result.all()


async def create_assignee(
    session: AsyncSession,
    assignee: TechnicalVisitAssignee,
) -> TechnicalVisitAssignee:
    """Persist a technical visit assignee."""

    session.add(assignee)
    await session.flush()
    await session.refresh(assignee)
    return assignee


async def list_assignees(
    session: AsyncSession,
    visit_id: int,
) -> Sequence[TechnicalVisitAssignee]:
    """Return assignees for a technical visit."""

    statement = (
        select(TechnicalVisitAssignee)
        .where(TechnicalVisitAssignee.visit_id == visit_id)
        .order_by(cast(ColumnElement[Any], TechnicalVisitAssignee.id))
    )
    result = await session.exec(statement)
    return result.all()


async def delete_assignee(
    session: AsyncSession,
    assignee: TechnicalVisitAssignee,
) -> None:
    """Remove a technical visit assignee."""

    await session.delete(assignee)


async def create_attachment(
    session: AsyncSession,
    attachment: TechnicalVisitAttachment,
) -> TechnicalVisitAttachment:
    """Persist technical visit attachment metadata."""

    session.add(attachment)
    await session.flush()
    await session.refresh(attachment)
    return attachment


async def get_attachment(
    session: AsyncSession,
    attachment_id: int,
) -> TechnicalVisitAttachment | None:
    """Return technical visit attachment metadata by primary key."""

    return await session.get(TechnicalVisitAttachment, attachment_id)


async def list_attachments(
    session: AsyncSession,
    visit_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[TechnicalVisitAttachment]:
    """Return attachments uploaded for a technical visit."""

    statement = (
        select(TechnicalVisitAttachment)
        .where(TechnicalVisitAttachment.visit_id == visit_id)
        .order_by(
            desc(cast(ColumnElement[Any], TechnicalVisitAttachment.uploaded_at)),
            desc(cast(ColumnElement[Any], TechnicalVisitAttachment.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await session.exec(statement)
    return result.all()


async def delete_attachment(
    session: AsyncSession,
    attachment: TechnicalVisitAttachment,
) -> None:
    """Remove technical visit attachment metadata."""

    await session.delete(attachment)


async def create_proposal_link(
    session: AsyncSession,
    link: ProposalTechnicalVisit,
) -> ProposalTechnicalVisit:
    """Persist a Proposal-to-TechnicalVisit relationship."""

    session.add(link)
    await session.flush()
    await session.refresh(link)
    return link


async def get_proposal_link(
    session: AsyncSession,
    *,
    proposal_id: int,
    technical_visit_id: int,
) -> ProposalTechnicalVisit | None:
    """Return a Proposal-to-TechnicalVisit relationship by pair."""

    statement = select(ProposalTechnicalVisit).where(
        ProposalTechnicalVisit.proposal_id == proposal_id,
        ProposalTechnicalVisit.technical_visit_id == technical_visit_id,
    )
    result = await session.exec(statement)
    return result.first()


async def list_links_for_proposal(
    session: AsyncSession,
    proposal_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[ProposalTechnicalVisit]:
    """Return technical visit relationships for one proposal."""

    statement = (
        select(ProposalTechnicalVisit)
        .where(ProposalTechnicalVisit.proposal_id == proposal_id)
        .order_by(
            desc(cast(ColumnElement[Any], ProposalTechnicalVisit.linked_at)),
            desc(cast(ColumnElement[Any], ProposalTechnicalVisit.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await session.exec(statement)
    return result.all()


async def delete_proposal_link(
    session: AsyncSession,
    link: ProposalTechnicalVisit,
) -> None:
    """Remove a Proposal-to-TechnicalVisit relationship."""

    await session.delete(link)
