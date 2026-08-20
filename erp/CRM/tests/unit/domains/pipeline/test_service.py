from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from core.config import Settings
from core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from core.exceptions import AuthorizationError, InvalidOperationError
from domains.contacts.models import ContactType
from domains.contacts.schemas import (
    CompanyContactPersonCreate,
    ContactCreate,
    PromoterCreate,
)
from domains.contacts.service import create_contact, create_promoter
from domains.leads.models import LeadInterestType, LeadStage
from domains.leads.schemas import LeadCreate
from domains.leads.service import create_lead
from domains.leads.service import move_to_stage as move_lead_to_stage
from domains.pipeline.models import PipelineEntityType
from domains.pipeline.service import list_transitions, summarize_entity, transition
from domains.proposals.models import ProposalStage, ProposalSystemType
from domains.proposals.schemas import (
    ProposalCreate,
    ProposalInstallationAddress,
    ProposalPVSystemPayload,
)
from domains.proposals.service import (
    create_proposal,
    mark_won,
)
from domains.proposals.service import (
    move_to_stage as move_proposal_to_stage,
)
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


async def _create_lead(session, owner_id: int) -> int:
    promoter = await create_promoter(
        session,
        PromoterCreate(name="Referral Partner", phone="+52 81 5555 0000"),
        owner_id=owner_id,
    )
    assert promoter.id is not None
    contact = await create_contact(
        session,
        ContactCreate(
            type=ContactType.COMPANY,
            name="Acme Solar",
            promoter_id=promoter.id,
            industry="Manufacturing",
            company_people=[
                CompanyContactPersonCreate(
                    name="Jane Manager",
                    phone="+52 81 5555 0101",
                    position="Facility Manager",
                )
            ],
        ),
        owner_id=owner_id,
    )
    assert contact.id is not None
    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact.id,
            title="Solar 8kW - Acme",
            interest_type=LeadInterestType.PHOTOVOLTAIC,
        ),
        owner_id=owner_id,
    )
    assert lead.id is not None
    return lead.id


def _proposal_payload(lead_id: int, *, name: str = "Base option") -> ProposalCreate:
    return ProposalCreate(
        lead_id=lead_id,
        name=name,
        version="1.0",
        installation_address=ProposalInstallationAddress(
            address_line="Av Solar 123",
            city="Monterrey",
            state="Nuevo Leon",
            postal_code="64000",
        ),
        tariff="GDMTH",
        contracted_demand=120,
        system_type=ProposalSystemType.PV,
        total_price=Decimal("250000.00"),
        annual_savings=Decimal("78000.00"),
        currency="MXN",
        estimated_cost=Decimal("180000.00"),
        expected_profit=Decimal("70000.00"),
        submitted_at=datetime(2026, 6, 1, 12, 0),
        valid_until=date.today() + timedelta(days=30),
        pv_system=ProposalPVSystemPayload(
            panel_count=16,
            panel_model="Jinko 550",
            panel_power=550,
            inverter_model="INV-8K",
            inverter_count=1,
            inverter_power=8,
            type_of_surface="roof",
            total_power_ac=8,
            system_size_kw=8.5,
            oversizing_kw=0.5,
            estimated_annual_kwh=12800,
            estimated_savings_kw=7.2,
            connection_mode="interconnected",
            cost_watt=Decimal("21.1765"),
            price_watt=Decimal("29.4118"),
        ),
    )


@pytest.mark.asyncio
async def test_lead_transitions_are_audited(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)

    await move_lead_to_stage(
        session,
        lead_id,
        stage=LeadStage.QUALIFYING,
        owner_id=owner_id,
    )
    transitions = await list_transitions(
        session,
        user_id=owner_id,
        entity_type=PipelineEntityType.LEAD,
        entity_id=lead_id,
    )
    summary = await summarize_entity(
        session,
        user_id=owner_id,
        entity_type=PipelineEntityType.LEAD,
        entity_id=lead_id,
    )

    assert [(item.from_stage, item.to_stage) for item in reversed(transitions)] == [
        (None, "NEW"),
        ("NEW", "QUALIFYING"),
    ]
    assert summary.current_stage == "QUALIFYING"
    assert summary.transition_count == 2
    assert summary.last_transition_at is not None


@pytest.mark.asyncio
async def test_pipeline_rejects_invalid_transition(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)

    with pytest.raises(InvalidOperationError):
        await transition(
            session,
            PipelineEntityType.LEAD,
            lead_id,
            to_stage=LeadStage.PROPOSAL_PHASE,
            by=owner_id,
        )


@pytest.mark.asyncio
async def test_pipeline_summary_is_owner_scoped(session) -> None:
    owner_id = await _create_owner(session)
    other_owner_id = await _create_owner(session, "other@example.com")
    other_lead_id = await _create_lead(session, other_owner_id)

    with pytest.raises(AuthorizationError):
        await summarize_entity(
            session,
            user_id=owner_id,
            entity_type=PipelineEntityType.LEAD,
            entity_id=other_lead_id,
        )


@pytest.mark.asyncio
async def test_proposal_win_flow_is_audited_atomically(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    winner = await create_proposal(
        session,
        _proposal_payload(lead_id, name="Winner"),
        created_by=owner_id,
    )
    sibling = await create_proposal(
        session,
        _proposal_payload(lead_id, name="Sibling"),
        created_by=owner_id,
    )
    await move_proposal_to_stage(
        session,
        winner.id or 0,
        stage=ProposalStage.SENT,
        user_id=owner_id,
    )

    await mark_won(winner.id or 0, owner_id, session)
    proposal_transitions = await list_transitions(
        session,
        user_id=owner_id,
        entity_type=PipelineEntityType.PROPOSAL,
    )
    lead_transitions = await list_transitions(
        session,
        user_id=owner_id,
        entity_type=PipelineEntityType.LEAD,
        entity_id=lead_id,
    )

    assert (None, "DRAFT") in {(item.from_stage, item.to_stage) for item in proposal_transitions}
    assert ("SENT", "WON") in {(item.from_stage, item.to_stage) for item in proposal_transitions}
    assert ("DRAFT", "SUPERSEDED") in {
        (item.from_stage, item.to_stage)
        for item in proposal_transitions
        if item.entity_id == sibling.id
    }
    assert [(item.from_stage, item.to_stage) for item in reversed(lead_transitions)] == [
        (None, "NEW"),
        ("NEW", "CLOSED_WON"),
    ]
