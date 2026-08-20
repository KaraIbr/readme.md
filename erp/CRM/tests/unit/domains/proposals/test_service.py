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
from domains.leads.models import LeadInterestType, LeadOutcome, LeadStage
from domains.leads.schemas import LeadCreate
from domains.leads.service import create_lead, get_lead
from domains.proposals.models import (
    ProposalDocumentClassification,
    ProposalStage,
    ProposalSystemType,
)
from domains.proposals.schemas import (
    ProposalBESSSystemPayload,
    ProposalCreate,
    ProposalInstallationAddress,
    ProposalPVSystemPayload,
    ProposalUpdate,
)
from domains.proposals.service import (
    create_proposal,
    get_proposal,
    list_documents,
    list_proposals,
    mark_lost,
    mark_won,
    move_to_stage,
    update_proposal,
    upload_document,
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


def _minimal_proposal_payload(
    lead_id: int,
    *,
    name: str = "Base option",
) -> ProposalCreate:
    return ProposalCreate(
        lead_id=lead_id,
        name=name,
    )


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


class FakeUpload:
    def __init__(
        self,
        content: bytes,
        *,
        filename: str = "costs.pdf",
        content_type: str = "application/pdf",
    ) -> None:
        self._content = content
        self._read = False
        self.filename: str | None = filename
        self.content_type: str | None = content_type

    async def read(self, size: int = -1) -> bytes:
        if self._read:
            return b""
        self._read = True
        return self._content


@pytest.mark.asyncio
async def test_create_proposal_assigns_creator_and_defaults_stage(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)

    proposal = await create_proposal(
        session,
        _minimal_proposal_payload(lead_id, name="  Base option  "),
        created_by=owner_id,
    )

    assert proposal.id is not None
    assert proposal.created_by == owner_id
    assert proposal.lead_id == lead_id
    assert proposal.name == "Base option"
    assert proposal.current_stage == ProposalStage.DRAFT
    assert proposal.loss_reason is None
    assert proposal.proposed_at is None
    assert not proposal.is_complete
    assert "system_type" in proposal.missing_required_fields


@pytest.mark.asyncio
async def test_create_proposal_rejects_lead_from_another_owner(session) -> None:
    owner_id = await _create_owner(session)
    other_owner_id = await _create_owner(session, "other@example.com")
    other_lead_id = await _create_lead(session, other_owner_id)

    with pytest.raises(AuthorizationError):
        await create_proposal(
            session,
            _proposal_payload(other_lead_id),
            created_by=owner_id,
        )


@pytest.mark.asyncio
async def test_list_get_and_update_proposals_are_user_scoped(session) -> None:
    owner_id = await _create_owner(session)
    other_owner_id = await _create_owner(session, "other@example.com")
    lead_id = await _create_lead(session, owner_id)
    other_lead_id = await _create_lead(session, other_owner_id)
    proposal = await create_proposal(
        session,
        _proposal_payload(lead_id),
        created_by=owner_id,
    )
    await create_proposal(
        session,
        _proposal_payload(other_lead_id, name="Other option"),
        created_by=other_owner_id,
    )

    proposals = await list_proposals(session, user_id=owner_id)
    updated = await update_proposal(
        session,
        proposal.id or 0,
        ProposalUpdate(total_price=Decimal("245000.00")),
        user_id=owner_id,
    )

    assert [item.id for item in proposals] == [proposal.id]
    assert updated.total_price == Decimal("245000.00")
    assert updated.pv_system is not None
    assert updated.pv_system.cost_watt == Decimal("21.1765")
    assert updated.pv_system.price_watt == Decimal("29.4118")
    assert await get_proposal(session, proposal.id or 0, user_id=owner_id) == updated
    with pytest.raises(AuthorizationError):
        await get_proposal(session, proposal.id or 0, user_id=other_owner_id)


@pytest.mark.asyncio
async def test_stage_transitions_set_proposed_at(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    proposal = await create_proposal(
        session,
        _proposal_payload(lead_id),
        created_by=owner_id,
    )

    sent = await move_to_stage(
        session,
        proposal.id or 0,
        stage=ProposalStage.SENT,
        user_id=owner_id,
    )
    sent_stage = sent.current_stage
    sent_at = sent.proposed_at
    negotiation = await move_to_stage(
        session,
        proposal.id or 0,
        stage=ProposalStage.NEGOTIATION,
        user_id=owner_id,
    )

    assert sent_stage == ProposalStage.SENT
    assert sent_at is not None
    assert negotiation.current_stage == ProposalStage.NEGOTIATION

    with pytest.raises(InvalidOperationError):
        await move_to_stage(
            session,
            proposal.id or 0,
            stage=ProposalStage.DRAFT,
            user_id=owner_id,
        )


@pytest.mark.asyncio
async def test_incomplete_proposal_cannot_leave_draft(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    proposal = await create_proposal(
        session,
        _minimal_proposal_payload(lead_id),
        created_by=owner_id,
    )

    with pytest.raises(InvalidOperationError) as exc_info:
        await move_to_stage(
            session,
            proposal.id or 0,
            stage=ProposalStage.SENT,
            user_id=owner_id,
        )

    assert "system_type" in exc_info.value.details["missing_required_fields"]


@pytest.mark.asyncio
async def test_unit_price_fields_are_required_by_system_type(session) -> None:
    owner_id = await _create_owner(session)
    pv_lead_id = await _create_lead(session, owner_id)
    bess_lead_id = await _create_lead(session, owner_id)
    pv_payload = _proposal_payload(pv_lead_id)
    assert pv_payload.pv_system is not None
    pv_system_data = pv_payload.pv_system.model_dump()
    pv_system_data["price_watt"] = None

    incomplete_pv = await create_proposal(
        session,
        pv_payload.model_copy(update={"pv_system": ProposalPVSystemPayload(**pv_system_data)}),
        created_by=owner_id,
    )
    bess = await create_proposal(
        session,
        ProposalCreate(
            lead_id=bess_lead_id,
            name="BESS option",
            version="1.0",
            installation_address=ProposalInstallationAddress(
                address_line="Av Solar 123",
                city="Monterrey",
                state="Nuevo Leon",
                postal_code="64000",
            ),
            tariff="GDMTH",
            contracted_demand=120,
            system_type=ProposalSystemType.BESS,
            total_price=Decimal("330000.00"),
            annual_savings=Decimal("64000.00"),
            currency="MXN",
            estimated_cost=Decimal("250000.00"),
            expected_profit=Decimal("80000.00"),
            submitted_at=datetime(2026, 6, 1, 12, 0),
            valid_until=date.today() + timedelta(days=30),
            bess_system=ProposalBESSSystemPayload(
                battery_model="PowerWall Commercial",
                battery_count=2,
                battery_power_kw=10,
                battery_storage_kwh=27,
                bess_primary_use="backup",
                technical_notes="Backup for critical loads.",
                cost_kwh=Decimal("9259.2593"),
                price_kwh=Decimal("12222.2222"),
            ),
        ),
        created_by=owner_id,
    )

    assert "pv_system.price_watt" in incomplete_pv.missing_required_fields
    assert bess.is_complete is True
    assert bess.bess_system is not None
    assert bess.bess_system.cost_kwh == Decimal("9259.2593")
    assert bess.bess_system.price_kwh == Decimal("12222.2222")


@pytest.mark.asyncio
async def test_mark_won_supersedes_active_siblings_and_closes_lead(session) -> None:
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
    await move_to_stage(session, winner.id or 0, stage=ProposalStage.SENT, user_id=owner_id)

    won = await mark_won(winner.id or 0, owner_id, session)
    superseded = await get_proposal(session, sibling.id or 0, user_id=owner_id)
    lead = await get_lead(session, lead_id, owner_id=owner_id)

    assert won.current_stage == ProposalStage.WON
    assert superseded.current_stage == ProposalStage.SUPERSEDED
    assert lead.current_stage == LeadStage.CLOSED_WON
    assert lead.outcome == LeadOutcome.WON
    assert lead.closed_at is not None

    with pytest.raises(InvalidOperationError):
        await mark_won(sibling.id or 0, owner_id, session)


@pytest.mark.asyncio
async def test_mark_lost_closes_lead_when_no_active_proposals_remain(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    first = await create_proposal(
        session,
        _proposal_payload(lead_id, name="First"),
        created_by=owner_id,
    )
    second = await create_proposal(
        session,
        _proposal_payload(lead_id, name="Second"),
        created_by=owner_id,
    )
    await move_to_stage(session, first.id or 0, stage=ProposalStage.SENT, user_id=owner_id)
    await move_to_stage(
        session,
        second.id or 0,
        stage=ProposalStage.SENT,
        user_id=owner_id,
    )

    lost_first = await mark_lost(
        session,
        first.id or 0,
        user_id=owner_id,
        loss_reason="Too expensive",
    )
    open_lead = await get_lead(session, lead_id, owner_id=owner_id)
    open_lead_stage = open_lead.current_stage
    lost_second = await mark_lost(
        session,
        second.id or 0,
        user_id=owner_id,
        loss_reason="No response",
    )
    closed_lead = await get_lead(session, lead_id, owner_id=owner_id)

    assert lost_first.current_stage == ProposalStage.LOST
    assert lost_first.loss_reason == "Too expensive"
    assert open_lead_stage == LeadStage.NEW
    assert lost_second.current_stage == ProposalStage.LOST
    assert closed_lead.current_stage == LeadStage.CLOSED_LOST
    assert closed_lead.outcome == LeadOutcome.LOST
    assert closed_lead.notes == "No response"


@pytest.mark.asyncio
async def test_terminal_actions_require_sent_proposal(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    proposal = await create_proposal(
        session,
        _proposal_payload(lead_id),
        created_by=owner_id,
    )
    proposal_id = proposal.id or 0

    with pytest.raises(InvalidOperationError):
        await mark_won(proposal_id, owner_id, session)
    with pytest.raises(InvalidOperationError):
        await mark_lost(
            session,
            proposal_id,
            user_id=owner_id,
            loss_reason="No response",
        )


@pytest.mark.asyncio
async def test_upload_and_list_classified_proposal_documents(
    session,
    tmp_path,
) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    proposal = await create_proposal(
        session,
        _proposal_payload(lead_id),
        created_by=owner_id,
    )

    document = await upload_document(
        session,
        proposal.id or 0,
        title="Cost breakdown",
        classification=ProposalDocumentClassification.COSTS,
        upload=FakeUpload(b"cost-data"),
        user_id=owner_id,
        storage_root=tmp_path,
    )
    documents = await list_documents(
        session,
        proposal.id or 0,
        user_id=owner_id,
        classification=ProposalDocumentClassification.COSTS,
    )

    assert document.id is not None
    assert document.title == "Cost breakdown"
    assert document.classification == ProposalDocumentClassification.COSTS
    assert document.original_filename == "costs.pdf"
    assert documents == [document]
