"""Proposals data access functions."""

from collections.abc import Sequence
from typing import Any, cast

from domains.leads.models import Lead
from domains.permissions.models import ProposalAssignment
from domains.proposals.models import (
    Proposal,
    ProposalBESSSystem,
    ProposalCommercialDocument,
    ProposalDocument,
    ProposalDocumentClassification,
    ProposalPVSystem,
    ProposalStage,
)
from sqlalchemy import desc, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

ACTIVE_STAGES = {
    ProposalStage.DRAFT,
    ProposalStage.SENT,
    ProposalStage.NEGOTIATION,
}


def _search_clause(pattern: str):
    return or_(
        cast(ColumnElement[Any], Proposal.name).ilike(pattern),
        cast(ColumnElement[Any], Proposal.version).ilike(pattern),
        cast(ColumnElement[Any], Proposal.installation_address_line).ilike(pattern),
        cast(ColumnElement[Any], Proposal.installation_city).ilike(pattern),
        cast(ColumnElement[Any], Proposal.installation_state).ilike(pattern),
        cast(ColumnElement[Any], Proposal.tariff).ilike(pattern),
        cast(ColumnElement[Any], Proposal.system_type).ilike(pattern),
        cast(ColumnElement[Any], ProposalPVSystem.panel_model).ilike(pattern),
        cast(ColumnElement[Any], ProposalPVSystem.inverter_model).ilike(pattern),
        cast(ColumnElement[Any], ProposalPVSystem.type_of_surface).ilike(pattern),
        cast(ColumnElement[Any], ProposalPVSystem.connection_mode).ilike(pattern),
        cast(ColumnElement[Any], ProposalBESSSystem.battery_model).ilike(pattern),
        cast(ColumnElement[Any], ProposalBESSSystem.bess_primary_use).ilike(pattern),
        cast(ColumnElement[Any], ProposalBESSSystem.technical_notes).ilike(pattern),
    )


def _search_statement():
    return (
        select(Proposal)
        .options(
            selectinload(cast(Any, Proposal.lead)),
            selectinload(cast(Any, Proposal.pv_system)),
            selectinload(cast(Any, Proposal.bess_system)),
        )
        .outerjoin(
            ProposalPVSystem,
            cast(ColumnElement[Any], ProposalPVSystem.proposal_id)
            == cast(ColumnElement[Any], Proposal.id),
        )
        .outerjoin(
            ProposalBESSSystem,
            cast(ColumnElement[Any], ProposalBESSSystem.proposal_id)
            == cast(ColumnElement[Any], Proposal.id),
        )
    )


async def create(session: AsyncSession, proposal: Proposal) -> Proposal:
    """Persist a new proposal and refresh database-populated fields."""

    session.add(proposal)
    await session.flush()
    await session.refresh(proposal)
    return proposal


async def get(session: AsyncSession, proposal_id: int) -> Proposal | None:
    """Return a proposal by primary key."""

    statement = (
        select(Proposal)
        .options(
            selectinload(cast(Any, Proposal.lead)),
            selectinload(cast(Any, Proposal.pv_system)),
            selectinload(cast(Any, Proposal.bess_system)),
        )
        .where(Proposal.id == proposal_id)
    )
    result = await session.exec(statement)
    return result.first()


async def list_for_user(
    session: AsyncSession,
    user_id: int,
    *,
    lead_id: int | None = None,
    stage: ProposalStage | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Proposal]:
    """Return proposals created by a user."""

    statement = (
        select(Proposal)
        .options(
            selectinload(cast(Any, Proposal.lead)),
            selectinload(cast(Any, Proposal.pv_system)),
            selectinload(cast(Any, Proposal.bess_system)),
        )
        .where(Proposal.created_by == user_id)
        .order_by(
            desc(cast(ColumnElement[Any], Proposal.created_at)),
            desc(cast(ColumnElement[Any], Proposal.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if lead_id is not None:
        statement = statement.where(Proposal.lead_id == lead_id)
    if stage is not None:
        statement = statement.where(Proposal.current_stage == stage)

    result = await session.exec(statement)
    return result.all()


async def list_all(
    session: AsyncSession,
    *,
    lead_id: int | None = None,
    stage: ProposalStage | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Proposal]:
    """Return proposals across all users."""

    statement = (
        select(Proposal)
        .options(
            selectinload(cast(Any, Proposal.lead)),
            selectinload(cast(Any, Proposal.pv_system)),
            selectinload(cast(Any, Proposal.bess_system)),
        )
        .order_by(
            desc(cast(ColumnElement[Any], Proposal.created_at)),
            desc(cast(ColumnElement[Any], Proposal.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if lead_id is not None:
        statement = statement.where(Proposal.lead_id == lead_id)
    if stage is not None:
        statement = statement.where(Proposal.current_stage == stage)
    result = await session.exec(statement)
    return result.all()


async def list_for_lead_owner(
    session: AsyncSession,
    user_id: int,
    *,
    lead_id: int | None = None,
    stage: ProposalStage | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Proposal]:
    """Return proposals attached to Leads assigned to a sales user."""

    statement = (
        select(Proposal)
        .options(
            selectinload(cast(Any, Proposal.lead)),
            selectinload(cast(Any, Proposal.pv_system)),
            selectinload(cast(Any, Proposal.bess_system)),
        )
        .join(
            Lead,
            cast(ColumnElement[Any], Lead.id) == cast(ColumnElement[Any], Proposal.lead_id),
        )
        .where(Lead.owner_id == user_id)
        .order_by(
            desc(cast(ColumnElement[Any], Proposal.created_at)),
            desc(cast(ColumnElement[Any], Proposal.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if lead_id is not None:
        statement = statement.where(Proposal.lead_id == lead_id)
    if stage is not None:
        statement = statement.where(Proposal.current_stage == stage)
    result = await session.exec(statement)
    return result.all()


async def list_for_assigned_tech(
    session: AsyncSession,
    user_id: int,
    *,
    lead_id: int | None = None,
    stage: ProposalStage | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Proposal]:
    """Return proposals directly assigned to a technical user."""

    statement = (
        select(Proposal)
        .options(
            selectinload(cast(Any, Proposal.lead)),
            selectinload(cast(Any, Proposal.pv_system)),
            selectinload(cast(Any, Proposal.bess_system)),
        )
        .join(
            ProposalAssignment,
            cast(ColumnElement[Any], ProposalAssignment.proposal_id)
            == cast(ColumnElement[Any], Proposal.id),
        )
        .where(
            ProposalAssignment.user_id == user_id,
            cast(ColumnElement[bool], ProposalAssignment.is_active).is_(True),
        )
        .order_by(
            desc(cast(ColumnElement[Any], Proposal.created_at)),
            desc(cast(ColumnElement[Any], Proposal.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if lead_id is not None:
        statement = statement.where(Proposal.lead_id == lead_id)
    if stage is not None:
        statement = statement.where(Proposal.current_stage == stage)
    result = await session.exec(statement)
    return result.all()


async def search_for_user(
    session: AsyncSession,
    user_id: int,
    *,
    query: str,
    limit: int = 20,
) -> Sequence[Proposal]:
    """Search proposals created by a user across commercial and technical fields."""

    normalized = query.strip()
    if not normalized:
        return []

    pattern = f"%{normalized}%"
    statement = (
        _search_statement()
        .where(
            Proposal.created_by == user_id,
            _search_clause(pattern),
        )
        .order_by(
            desc(cast(ColumnElement[Any], Proposal.created_at)),
            desc(cast(ColumnElement[Any], Proposal.id)),
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
) -> Sequence[Proposal]:
    """Search proposals across all users."""

    normalized = query.strip()
    if not normalized:
        return []

    pattern = f"%{normalized}%"
    statement = (
        _search_statement()
        .where(_search_clause(pattern))
        .order_by(
            desc(cast(ColumnElement[Any], Proposal.created_at)),
            desc(cast(ColumnElement[Any], Proposal.id)),
        )
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()


async def search_for_lead_owner(
    session: AsyncSession,
    user_id: int,
    *,
    query: str,
    limit: int = 20,
) -> Sequence[Proposal]:
    """Search proposals attached to Leads assigned to a sales user."""

    normalized = query.strip()
    if not normalized:
        return []

    pattern = f"%{normalized}%"
    statement = (
        _search_statement()
        .join(Lead, Lead.id == Proposal.lead_id)
        .where(
            Lead.owner_id == user_id,
            _search_clause(pattern),
        )
        .order_by(
            desc(cast(ColumnElement[Any], Proposal.created_at)),
            desc(cast(ColumnElement[Any], Proposal.id)),
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
) -> Sequence[Proposal]:
    """Search proposals directly assigned to a technical user."""

    normalized = query.strip()
    if not normalized:
        return []

    pattern = f"%{normalized}%"
    statement = (
        _search_statement()
        .join(
            ProposalAssignment,
            cast(ColumnElement[Any], ProposalAssignment.proposal_id)
            == cast(ColumnElement[Any], Proposal.id),
        )
        .where(
            ProposalAssignment.user_id == user_id,
            cast(ColumnElement[bool], ProposalAssignment.is_active).is_(True),
            _search_clause(pattern),
        )
        .order_by(
            desc(cast(ColumnElement[Any], Proposal.created_at)),
            desc(cast(ColumnElement[Any], Proposal.id)),
        )
        .limit(limit)
    )
    result = await session.exec(statement)
    return result.all()


async def create_pv_system(
    session: AsyncSession,
    system: ProposalPVSystem,
) -> ProposalPVSystem:
    """Persist PV system details."""

    session.add(system)
    await session.flush()
    await session.refresh(system)
    return system


async def create_bess_system(
    session: AsyncSession,
    system: ProposalBESSSystem,
) -> ProposalBESSSystem:
    """Persist BESS system details."""

    session.add(system)
    await session.flush()
    await session.refresh(system)
    return system


async def delete_pv_system(
    session: AsyncSession,
    system: ProposalPVSystem,
) -> None:
    """Remove PV system details."""

    await session.delete(system)


async def delete_bess_system(
    session: AsyncSession,
    system: ProposalBESSSystem,
) -> None:
    """Remove BESS system details."""

    await session.delete(system)


async def list_active_siblings(
    session: AsyncSession,
    *,
    lead_id: int,
    exclude_id: int,
) -> Sequence[Proposal]:
    """Return active proposal siblings for a lead."""

    statement = select(Proposal).where(
        Proposal.lead_id == lead_id,
        Proposal.id != exclude_id,
        cast(ColumnElement[Any], Proposal.current_stage).in_(ACTIVE_STAGES),
    )
    result = await session.exec(statement)
    return result.all()


async def get_won_for_lead(
    session: AsyncSession,
    *,
    lead_id: int,
) -> Proposal | None:
    """Return the winning proposal for a lead, if any."""

    statement = select(Proposal).where(
        Proposal.lead_id == lead_id,
        Proposal.current_stage == ProposalStage.WON,
    )
    result = await session.exec(statement)
    return result.first()


async def has_active_for_lead(
    session: AsyncSession,
    *,
    lead_id: int,
) -> bool:
    """Return whether a lead still has active proposals."""

    statement = select(Proposal.id).where(
        Proposal.lead_id == lead_id,
        cast(ColumnElement[Any], Proposal.current_stage).in_(ACTIVE_STAGES),
    )
    result = await session.exec(statement)
    return result.first() is not None


async def delete(session: AsyncSession, proposal: Proposal) -> None:
    """Remove a proposal."""

    await session.delete(proposal)


async def create_commercial_document(
    session: AsyncSession,
    document: ProposalCommercialDocument,
) -> ProposalCommercialDocument:
    """Persist commercial proposal PDF metadata."""

    session.add(document)
    await session.flush()
    await session.refresh(document)
    return document


async def get_commercial_document(
    session: AsyncSession,
    document_id: int,
) -> ProposalCommercialDocument | None:
    """Return a commercial proposal PDF metadata row by primary key."""

    return await session.get(ProposalCommercialDocument, document_id)


async def list_commercial_documents(
    session: AsyncSession,
    proposal_id: int,
    *,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[ProposalCommercialDocument]:
    """Return commercial proposal PDFs attached to a proposal."""

    statement = (
        select(ProposalCommercialDocument)
        .where(ProposalCommercialDocument.proposal_id == proposal_id)
        .order_by(
            desc(cast(ColumnElement[Any], ProposalCommercialDocument.uploaded_at)),
            desc(cast(ColumnElement[Any], ProposalCommercialDocument.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    result = await session.exec(statement)
    return result.all()


async def delete_commercial_document(
    session: AsyncSession,
    document: ProposalCommercialDocument,
) -> None:
    """Remove commercial proposal PDF metadata."""

    await session.delete(document)


async def create_document(
    session: AsyncSession,
    document: ProposalDocument,
) -> ProposalDocument:
    """Persist proposal document metadata."""

    session.add(document)
    await session.flush()
    await session.refresh(document)
    return document


async def get_document(
    session: AsyncSession,
    document_id: int,
) -> ProposalDocument | None:
    """Return a proposal document metadata row by primary key."""

    return await session.get(ProposalDocument, document_id)


async def list_documents(
    session: AsyncSession,
    proposal_id: int,
    *,
    classification: ProposalDocumentClassification | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[ProposalDocument]:
    """Return classified documents attached to a proposal."""

    statement = (
        select(ProposalDocument)
        .where(ProposalDocument.proposal_id == proposal_id)
        .order_by(
            desc(cast(ColumnElement[Any], ProposalDocument.uploaded_at)),
            desc(cast(ColumnElement[Any], ProposalDocument.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if classification is not None:
        statement = statement.where(ProposalDocument.classification == classification)

    result = await session.exec(statement)
    return result.all()


async def delete_document(
    session: AsyncSession,
    document: ProposalDocument,
) -> None:
    """Remove proposal document metadata."""

    await session.delete(document)
