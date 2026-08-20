from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from core.config import Settings
from core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from domains.contacts.models import Contact, ContactType, Promoter
from domains.dashboard.service import get_stats
from domains.leads.models import Lead, LeadStage
from domains.permissions.models import UserRole
from domains.pipeline.models import PipelineEntityType, StageTransition
from domains.proposals.models import Proposal, ProposalStage
from domains.technical_visits.models import TechnicalVisit, TechnicalVisitStatus
from helpers import create_iam_user
from pydantic import SecretStr


@pytest.fixture()
async def session():
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key=SecretStr("super-secret-for-tests"),
    )
    engine = build_async_engine(settings)
    await create_all(engine)
    session_factory = build_session_factory(engine)

    try:
        async with session_factory() as test_session:
            yield test_session
    finally:
        await drop_all(engine)
        await engine.dispose()


async def _create_owner(session, email: str = "owner@example.com") -> int:
    user = await create_iam_user(session, email=email)
    assert user.id is not None
    return user.id


async def _seed_owner_data(session, owner_id: int, *, prefix: str) -> tuple[int, int]:
    promoter = Promoter(
        name=f"{prefix} Partner",
        phone="+52 81 5555 0000",
        owner_id=owner_id,
    )
    session.add(promoter)
    await session.commit()
    await session.refresh(promoter)
    assert promoter.id is not None

    contact = Contact(
        type=ContactType.COMPANY,
        name=f"{prefix} Solar",
        promoter_id=promoter.id,
        owner_id=owner_id,
    )
    session.add(contact)
    await session.commit()
    await session.refresh(contact)
    assert contact.id is not None

    open_lead = Lead(
        contact_id=contact.id,
        title=f"{prefix} open lead",
        interest_type="Photovoltaic",
        current_stage=LeadStage.NEW,
        owner_id=owner_id,
    )
    won_lead = Lead(
        contact_id=contact.id,
        title=f"{prefix} won lead",
        interest_type="Photovoltaic",
        current_stage=LeadStage.CLOSED_WON,
        owner_id=owner_id,
    )
    session.add_all([open_lead, won_lead])
    await session.commit()
    await session.refresh(open_lead)
    await session.refresh(won_lead)
    assert open_lead.id is not None
    assert won_lead.id is not None

    proposal = Proposal(
        lead_id=open_lead.id,
        name=f"{prefix} proposal",
        current_stage=ProposalStage.WON,
        total_price=Decimal("1000.00"),
        created_by=owner_id,
    )
    visit = TechnicalVisit(
        lead_id=open_lead.id,
        status=TechnicalVisitStatus.SCHEDULED,
        created_by=owner_id,
    )
    session.add_all([proposal, visit])
    await session.commit()

    return open_lead.id, won_lead.id


@pytest.mark.asyncio
async def test_get_stats_owner_scoped_counts_only_own_records(session) -> None:
    owner_id = await _create_owner(session)
    other_id = await _create_owner(session, "other@example.com")
    await _seed_owner_data(session, owner_id, prefix="Acme")
    await _seed_owner_data(session, other_id, prefix="Zeta")

    stats = await get_stats(session, owner_id, role=UserRole.SALES)

    assert stats["total_contacts"] == 1
    assert stats["total_leads"] == 2
    assert stats["active_leads"] == 1
    assert stats["won_leads"] == 1
    assert stats["pending_visits"] == 1
    assert stats["revenue_won"] == 1000
    assert stats["leads_by_stage"] == {"NEW": 1, "CLOSED_WON": 1}
    assert stats["proposals_by_stage"] == {"WON": 1}


@pytest.mark.asyncio
async def test_get_stats_aggregate_counts_all_records(session) -> None:
    owner_id = await _create_owner(session)
    other_id = await _create_owner(session, "other@example.com")
    await _seed_owner_data(session, owner_id, prefix="Acme")
    await _seed_owner_data(session, other_id, prefix="Zeta")

    stats = await get_stats(session, owner_id, role=UserRole.MANAGER)

    assert stats["total_contacts"] == 2
    assert stats["total_leads"] == 4
    assert stats["active_leads"] == 2
    assert stats["won_leads"] == 2
    assert stats["pending_visits"] == 2
    assert stats["revenue_won"] == 2000
    assert stats["leads_by_stage"] == {"NEW": 2, "CLOSED_WON": 2}
    assert stats["proposals_by_stage"] == {"WON": 2}


@pytest.mark.asyncio
async def test_get_stats_owner_scoped_filters_proposals_and_visits(session) -> None:
    owner_id = await _create_owner(session)
    other_id = await _create_owner(session, "other@example.com")
    _, _ = await _seed_owner_data(session, owner_id, prefix="Acme")
    _, won_lead_id = await _seed_owner_data(session, other_id, prefix="Zeta")

    completed = TechnicalVisit(
        lead_id=won_lead_id,
        status=TechnicalVisitStatus.COMPLETED,
        created_by=owner_id,
        completed_at=datetime.now(UTC),
    )
    session.add(completed)
    await session.commit()

    stats = await get_stats(session, owner_id, role=UserRole.SALES)

    assert stats["pending_visits"] == 1
    assert stats["revenue_won"] == 1000


@pytest.mark.asyncio
async def test_get_stats_recent_transitions_limited_and_newest_first(session) -> None:
    owner_id = await _create_owner(session)
    _, won_lead_id = await _seed_owner_data(session, owner_id, prefix="Acme")
    base = datetime.now(UTC) - timedelta(minutes=30)

    transitions = [
        StageTransition(
            entity_type=PipelineEntityType.LEAD,
            entity_id=won_lead_id,
            from_stage="NEW",
            to_stage="QUALIFYING",
            transitioned_by=owner_id,
            transitioned_at=base + timedelta(seconds=i),
        )
        for i in range(12)
    ]
    session.add_all(transitions)
    await session.commit()

    stats = await get_stats(session, owner_id, role=UserRole.ADMIN)
    recent = stats["recent_transitions"]

    assert len(recent) == 10
    expected_ids = [t.id for t in transitions[-10:]]
    assert [entry["id"] for entry in recent] == expected_ids[::-1]
    assert recent[0]["entity_type"] == "lead"
    assert recent[0]["to_stage"] == "QUALIFYING"
    assert "transitioned_at" in recent[0]


@pytest.mark.asyncio
async def test_get_stats_empty_tenant_returns_zeros(session) -> None:
    owner_id = await _create_owner(session)

    stats = await get_stats(session, owner_id, role=UserRole.SALES)

    assert stats["total_contacts"] == 0
    assert stats["total_leads"] == 0
    assert stats["active_leads"] == 0
    assert stats["won_leads"] == 0
    assert stats["pending_visits"] == 0
    assert stats["revenue_won"] == 0
    assert stats["leads_by_stage"] == {}
    assert stats["proposals_by_stage"] == {}
    assert stats["recent_transitions"] == []
