"""Leads data access functions."""

from collections.abc import Sequence
from typing import Any, cast

from domains.leads.models import (
    Lead,
    LeadDocument,
    LeadElectricityBill,
    LeadInteraction,
    LeadStage,
)
from domains.permissions.models import ProposalAssignment
from domains.proposals.models import Proposal
from domains.technical_visits.models import TechnicalVisit, TechnicalVisitAssignee
from sqlalchemy import desc, or_
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


def _assigned_tech_lead_clause(user_id: int):
    assigned_proposal_leads = (
        select(Proposal.lead_id)
        .join(
            ProposalAssignment,
            cast(ColumnElement[Any], ProposalAssignment.proposal_id)
            == cast(ColumnElement[Any], Proposal.id),
        )
        .where(
            ProposalAssignment.user_id == user_id,
            cast(ColumnElement[bool], ProposalAssignment.is_active).is_(True),
        )
    )
    assigned_visit_leads = (
        select(TechnicalVisit.lead_id)
        .join(
            TechnicalVisitAssignee,
            cast(ColumnElement[Any], TechnicalVisitAssignee.visit_id)
            == cast(ColumnElement[Any], TechnicalVisit.id),
        )
        .where(TechnicalVisitAssignee.user_id == user_id)
    )
    return or_(
        cast(ColumnElement[Any], Lead.id).in_(assigned_proposal_leads),
        cast(ColumnElement[Any], Lead.id).in_(assigned_visit_leads),
    )


async def create(session: AsyncSession, lead: Lead) -> Lead:
    """Persist a new lead and refresh database-populated fields."""

    session.add(lead)
    await session.flush()
    await session.refresh(lead)
    return lead


async def get(session: AsyncSession, lead_id: int) -> Lead | None:
    """Return a lead by primary key."""

    return await session.get(Lead, lead_id)


async def list_for_owner(
    session: AsyncSession,
    owner_id: int,
    *,
    contact_id: int | None = None,
    stage: LeadStage | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Lead]:
    """Return leads owned by a user."""

    statement = (
        select(Lead)
        .where(Lead.owner_id == owner_id)
        .order_by(
            desc(cast(ColumnElement[Any], Lead.created_at)),
            desc(cast(ColumnElement[Any], Lead.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if contact_id is not None:
        statement = statement.where(Lead.contact_id == contact_id)
    if stage is not None:
        statement = statement.where(Lead.current_stage == stage)

    result = await session.exec(statement)
    return result.all()


async def list_all(
    session: AsyncSession,
    *,
    contact_id: int | None = None,
    stage: LeadStage | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Lead]:
    """Return leads across all users."""

    statement = (
        select(Lead)
        .order_by(
            desc(cast(ColumnElement[Any], Lead.created_at)),
            desc(cast(ColumnElement[Any], Lead.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if contact_id is not None:
        statement = statement.where(Lead.contact_id == contact_id)
    if stage is not None:
        statement = statement.where(Lead.current_stage == stage)

    result = await session.exec(statement)
    return result.all()


async def list_for_assigned_tech(
    session: AsyncSession,
    user_id: int,
    *,
    contact_id: int | None = None,
    stage: LeadStage | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Lead]:
    """Return leads with technical work assigned to one user."""

    statement = (
        select(Lead)
        .where(_assigned_tech_lead_clause(user_id))
        .order_by(
            desc(cast(ColumnElement[Any], Lead.created_at)),
            desc(cast(ColumnElement[Any], Lead.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if contact_id is not None:
        statement = statement.where(Lead.contact_id == contact_id)
    if stage is not None:
        statement = statement.where(Lead.current_stage == stage)

    result = await session.exec(statement)
    return result.all()


async def search_for_owner(
    session: AsyncSession,
    owner_id: int,
    *,
    query: str,
    limit: int = 20,
) -> Sequence[Lead]:
    """Search leads owned by a user across descriptive fields."""

    normalized = query.strip()
    if not normalized:
        return []

    pattern = f"%{normalized}%"
    statement = (
        select(Lead)
        .where(
            Lead.owner_id == owner_id,
            or_(
                cast(ColumnElement[Any], Lead.title).ilike(pattern),
                cast(ColumnElement[Any], Lead.interest_type).ilike(pattern),
                cast(ColumnElement[Any], Lead.notes).ilike(pattern),
            ),
        )
        .order_by(
            desc(cast(ColumnElement[Any], Lead.created_at)),
            desc(cast(ColumnElement[Any], Lead.id)),
        )
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()


async def search_all(
    session: AsyncSession,
    *,
    query: str,
    limit: int = 20,
) -> Sequence[Lead]:
    """Search leads across all users."""

    normalized = query.strip()
    if not normalized:
        return []

    pattern = f"%{normalized}%"
    statement = (
        select(Lead)
        .where(
            or_(
                cast(ColumnElement[Any], Lead.title).ilike(pattern),
                cast(ColumnElement[Any], Lead.interest_type).ilike(pattern),
                cast(ColumnElement[Any], Lead.notes).ilike(pattern),
            ),
        )
        .order_by(
            desc(cast(ColumnElement[Any], Lead.created_at)),
            desc(cast(ColumnElement[Any], Lead.id)),
        )
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()


async def search_for_assigned_tech(
    session: AsyncSession,
    user_id: int,
    *,
    query: str,
    limit: int = 20,
) -> Sequence[Lead]:
    """Search leads with technical work assigned to one user."""

    normalized = query.strip()
    if not normalized:
        return []

    pattern = f"%{normalized}%"
    statement = (
        select(Lead)
        .where(
            _assigned_tech_lead_clause(user_id),
            or_(
                cast(ColumnElement[Any], Lead.title).ilike(pattern),
                cast(ColumnElement[Any], Lead.interest_type).ilike(pattern),
                cast(ColumnElement[Any], Lead.notes).ilike(pattern),
            ),
        )
        .order_by(
            desc(cast(ColumnElement[Any], Lead.created_at)),
            desc(cast(ColumnElement[Any], Lead.id)),
        )
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()


async def delete(session: AsyncSession, lead: Lead) -> None:
    """Remove a lead."""

    await session.delete(lead)


async def create_document(
    session: AsyncSession,
    document: LeadDocument,
) -> LeadDocument:
    """Persist a general lead document."""

    session.add(document)
    await session.flush()
    await session.refresh(document)
    return document


async def get_document(
    session: AsyncSession,
    document_id: int,
) -> LeadDocument | None:
    """Return a general lead document by primary key."""

    return await session.get(LeadDocument, document_id)


async def list_documents(
    session: AsyncSession,
    lead_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[LeadDocument]:
    """Return general documents attached to a lead."""

    statement = (
        select(LeadDocument)
        .where(LeadDocument.lead_id == lead_id)
        .order_by(
            desc(cast(ColumnElement[Any], LeadDocument.uploaded_at)),
            desc(cast(ColumnElement[Any], LeadDocument.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await session.exec(statement)
    return result.all()


async def delete_document(
    session: AsyncSession,
    document: LeadDocument,
) -> None:
    """Remove a general lead document metadata row."""

    await session.delete(document)


async def create_electricity_bill(
    session: AsyncSession,
    bill: LeadElectricityBill,
) -> LeadElectricityBill:
    """Persist a lead electricity bill."""

    session.add(bill)
    await session.flush()
    await session.refresh(bill)
    return bill


async def get_electricity_bill(
    session: AsyncSession,
    bill_id: int,
) -> LeadElectricityBill | None:
    """Return a lead electricity bill by primary key."""

    return await session.get(LeadElectricityBill, bill_id)


async def list_electricity_bills(
    session: AsyncSession,
    lead_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[LeadElectricityBill]:
    """Return electricity bills attached to a lead."""

    statement = (
        select(LeadElectricityBill)
        .where(LeadElectricityBill.lead_id == lead_id)
        .order_by(
            desc(cast(ColumnElement[Any], LeadElectricityBill.uploaded_at)),
            desc(cast(ColumnElement[Any], LeadElectricityBill.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await session.exec(statement)
    return result.all()


async def delete_electricity_bill(
    session: AsyncSession,
    bill: LeadElectricityBill,
) -> None:
    """Remove a lead electricity bill metadata row."""

    await session.delete(bill)


async def create_interaction(
    session: AsyncSession,
    interaction: LeadInteraction,
) -> LeadInteraction:
    """Persist a sales interaction for a lead."""

    session.add(interaction)
    await session.flush()
    await session.refresh(interaction)
    return interaction


async def get_interaction(
    session: AsyncSession,
    interaction_id: int,
) -> LeadInteraction | None:
    """Return a lead interaction by primary key."""

    return await session.get(LeadInteraction, interaction_id)


async def list_interactions(
    session: AsyncSession,
    lead_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[LeadInteraction]:
    """Return interactions attached to a lead."""

    statement = (
        select(LeadInteraction)
        .where(LeadInteraction.lead_id == lead_id)
        .order_by(
            desc(cast(ColumnElement[Any], LeadInteraction.interaction_date)),
            desc(cast(ColumnElement[Any], LeadInteraction.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await session.exec(statement)
    return result.all()


async def delete_interaction(
    session: AsyncSession,
    interaction: LeadInteraction,
) -> None:
    """Remove a lead interaction."""

    await session.delete(interaction)
