from collections import Counter

from domains.contacts.models import Contact
from domains.leads.models import Lead
from domains.permissions.models import UserRole
from domains.pipeline.models import StageTransition
from domains.proposals.models import Proposal
from domains.technical_visits.models import TechnicalVisit
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def _count_contacts(session: AsyncSession, owner_id: int | None) -> int:
    query = select(Contact)
    if owner_id is not None:
        query = query.where(Contact.owner_id == owner_id)
    result = await session.exec(query)
    return len(result.all())


async def get_stats(session: AsyncSession, owner_id: int, role: UserRole | None = None) -> dict:
    aggregate = role in {UserRole.ADMIN, UserRole.MANAGER}

    total_contacts = await _count_contacts(session, None if aggregate else owner_id)

    if aggregate:
        leads_result = await session.exec(select(Lead))
    else:
        leads_result = await session.exec(select(Lead).where(Lead.owner_id == owner_id))
    leads = leads_result.all()
    total_leads = len(leads)
    active_leads = sum(
        1 for lead in leads if lead.current_stage not in ("CLOSED_WON", "CLOSED_LOST")
    )
    won_leads = sum(1 for lead in leads if lead.current_stage == "CLOSED_WON")

    if aggregate:
        visits_result = await session.exec(
            select(TechnicalVisit).where(
                TechnicalVisit.status.in_(["SCHEDULED", "REQUESTED"]),  # type: ignore[attr-defined]
            )
        )
    else:
        visits_result = await session.exec(
            select(TechnicalVisit).where(
                TechnicalVisit.created_by == owner_id,
                TechnicalVisit.status.in_(["SCHEDULED", "REQUESTED"]),  # type: ignore[attr-defined]
            )
        )
    pending_visits = len(visits_result.all())

    if aggregate:
        won_result = await session.exec(select(Proposal).where(Proposal.current_stage == "WON"))
    else:
        won_result = await session.exec(
            select(Proposal).where(Proposal.created_by == owner_id, Proposal.current_stage == "WON")
        )
    revenue_won = sum(p.total_price or 0 for p in won_result.all())

    lead_stages = Counter(lead.current_stage or "NEW" for lead in leads)
    if aggregate:
        proposals_result = await session.exec(select(Proposal))
    else:
        proposals_result = await session.exec(
            select(Proposal).where(Proposal.created_by == owner_id)
        )
    proposal_stages = Counter(p.current_stage or "DRAFT" for p in proposals_result.all())

    transitions_result = await session.exec(
        select(StageTransition)
        .order_by(StageTransition.transitioned_at.desc())  # type: ignore[attr-defined]
        .limit(10)
    )
    recent = [
        {
            "id": t.id,
            "entity_type": t.entity_type,
            "entity_id": t.entity_id,
            "to_stage": t.to_stage,
            "transitioned_at": t.transitioned_at.isoformat(),
        }
        for t in transitions_result.all()
    ]

    return {
        "total_contacts": total_contacts,
        "total_leads": total_leads,
        "active_leads": active_leads,
        "won_leads": won_leads,
        "pending_visits": pending_visits,
        "revenue_won": revenue_won,
        "leads_by_stage": dict(lead_stages),
        "proposals_by_stage": dict(proposal_stages),
        "recent_transitions": recent,
    }
