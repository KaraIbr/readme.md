from datetime import datetime, timedelta
from pathlib import Path

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
from domains.leads.models import (
    LeadInteractionType,
    LeadInterestType,
    LeadOutcome,
    LeadStage,
)
from domains.leads.schemas import (
    LeadCreate,
    LeadInteractionCreate,
    LeadInteractionUpdate,
    LeadUpdate,
)
from domains.leads.service import (
    close,
    create_interaction,
    create_lead,
    delete_document,
    get_lead,
    list_documents,
    list_electricity_bills,
    list_interactions,
    list_leads,
    move_to_stage,
    update_interaction,
    update_lead,
    upload_document,
    upload_electricity_bill,
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


async def _create_contact(session, owner_id: int) -> int:
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
    return contact.id


class FakeUpload:
    def __init__(
        self,
        filename: str,
        content: bytes,
        content_type: str = "application/pdf",
    ) -> None:
        self.filename = filename
        self.content_type = content_type
        self._content = content
        self._offset = 0

    async def read(self, size: int = -1) -> bytes:
        if self._offset >= len(self._content):
            return b""
        if size < 0:
            size = len(self._content) - self._offset
        chunk = self._content[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk


@pytest.mark.asyncio
async def test_create_lead_assigns_owner_and_defaults_stage(session) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)

    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact_id,
            title="  Solar 8kW - Acme  ",
            interest_type="  Photovoltaic  ",
            qualification_score=75,
        ),
        owner_id=owner_id,
    )

    assert lead.id is not None
    assert lead.owner_id == owner_id
    assert lead.contact_id == contact_id
    assert lead.title == "Solar 8kW - Acme"
    assert lead.interest_type == LeadInterestType.PHOTOVOLTAIC
    assert lead.current_stage == LeadStage.NEW
    assert lead.outcome is None
    assert lead.closed_at is None


@pytest.mark.asyncio
async def test_create_lead_rejects_contact_from_another_owner(session) -> None:
    owner_id = await _create_owner(session)
    other_owner_id = await _create_owner(session, "other@example.com")
    other_contact_id = await _create_contact(session, other_owner_id)

    with pytest.raises(AuthorizationError):
        await create_lead(
            session,
            LeadCreate(
                contact_id=other_contact_id,
                title="Solar 8kW - Acme",
                interest_type="Photovoltaic",
            ),
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_list_get_and_update_leads_are_owner_scoped(session) -> None:
    owner_id = await _create_owner(session)
    other_owner_id = await _create_owner(session, "other@example.com")
    contact_id = await _create_contact(session, owner_id)
    other_contact_id = await _create_contact(session, other_owner_id)
    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact_id,
            title="Solar 8kW - Acme",
            interest_type="Photovoltaic",
        ),
        owner_id=owner_id,
    )
    await create_lead(
        session,
        LeadCreate(
            contact_id=other_contact_id,
            title="Other lead",
            interest_type="BESS",
        ),
        owner_id=other_owner_id,
    )

    leads = await list_leads(session, owner_id=owner_id)
    updated = await update_lead(
        session,
        lead.id or 0,
        LeadUpdate(notes="Needs bill review", qualification_score=80),
        owner_id=owner_id,
    )

    assert [item.id for item in leads] == [lead.id]
    assert updated.notes == "Needs bill review"
    assert updated.qualification_score == 80
    assert await get_lead(session, lead.id or 0, owner_id=owner_id) == updated
    with pytest.raises(AuthorizationError):
        await get_lead(session, lead.id or 0, owner_id=other_owner_id)


@pytest.mark.asyncio
async def test_stage_transitions_and_close(session) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)
    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact_id,
            title="Solar 8kW - Acme",
            interest_type="Photovoltaic",
        ),
        owner_id=owner_id,
    )

    qualifying = await move_to_stage(
        session,
        lead.id or 0,
        stage=LeadStage.QUALIFYING,
        owner_id=owner_id,
    )
    qualifying_stage = qualifying.current_stage
    proposal_phase = await move_to_stage(
        session,
        lead.id or 0,
        stage=LeadStage.PROPOSAL_PHASE,
        owner_id=owner_id,
    )
    proposal_phase_stage = proposal_phase.current_stage
    closed = await close(
        session,
        lead.id or 0,
        outcome=LeadOutcome.LOST,
        by=owner_id,
        notes="No response",
    )

    assert qualifying_stage == LeadStage.QUALIFYING
    assert proposal_phase_stage == LeadStage.PROPOSAL_PHASE
    assert closed.current_stage == LeadStage.CLOSED_LOST
    assert closed.outcome == LeadOutcome.LOST
    assert closed.closed_at is not None
    assert closed.notes == "No response"

    with pytest.raises(InvalidOperationError):
        await update_lead(
            session,
            lead.id or 0,
            LeadUpdate(notes="Reopened"),
            owner_id=owner_id,
        )

    with pytest.raises(InvalidOperationError):
        await close(
            session,
            lead.id or 0,
            outcome=LeadOutcome.WON,
            by=owner_id,
        )


@pytest.mark.asyncio
async def test_stage_transitions_reject_skipping_qualifying(session) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)
    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact_id,
            title="Solar 8kW - Acme",
            interest_type="Photovoltaic",
        ),
        owner_id=owner_id,
    )

    with pytest.raises(InvalidOperationError):
        await move_to_stage(
            session,
            lead.id or 0,
            stage=LeadStage.PROPOSAL_PHASE,
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_documents_and_electricity_bills_are_stored_separately(
    session,
    tmp_path: Path,
) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)
    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact_id,
            title="Solar 8kW - Acme",
            interest_type="Photovoltaic",
        ),
        owner_id=owner_id,
    )
    assert lead.id is not None

    document = await upload_document(
        session,
        lead.id,
        title="Project requirements",
        upload=FakeUpload("requirements.pdf", b"project docs"),
        owner_id=owner_id,
        storage_root=tmp_path,
    )
    bill = await upload_electricity_bill(
        session,
        lead.id,
        title="March CFE receipt",
        upload=FakeUpload("cfe-march.pdf", b"bill docs"),
        owner_id=owner_id,
        storage_root=tmp_path,
    )

    documents = await list_documents(session, lead.id, owner_id=owner_id)
    bills = await list_electricity_bills(session, lead.id, owner_id=owner_id)

    assert [item.id for item in documents] == [document.id]
    assert [item.id for item in bills] == [bill.id]
    assert Path(document.stored_path).read_bytes() == b"project docs"
    assert Path(bill.stored_path).read_bytes() == b"bill docs"
    assert "documents" in document.stored_path
    assert "electricity-bills" in bill.stored_path

    await delete_document(session, lead.id, document.id or 0, owner_id=owner_id)

    assert not Path(document.stored_path).exists()
    assert await list_documents(session, lead.id, owner_id=owner_id) == []


@pytest.mark.asyncio
async def test_interactions_document_sales_negotiation_history(session) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)
    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact_id,
            title="Hybrid system - Acme",
            interest_type="Hibrid",
        ),
        owner_id=owner_id,
    )
    assert lead.id is not None
    interaction_date = datetime.now() + timedelta(days=3)

    interaction = await create_interaction(
        session,
        lead.id,
        LeadInteractionCreate(
            interaction_type="NEGOTIATION",
            title="Initial negotiation",
            notes="Customer asked for phased delivery.",
            interaction_date=interaction_date,
        ),
        owner_id=owner_id,
    )
    updated_date = interaction_date + timedelta(days=1)
    updated = await update_interaction(
        session,
        lead.id,
        interaction.id or 0,
        LeadInteractionUpdate(
            notes="Customer asked for phased delivery and O&M.",
            interaction_date=updated_date,
        ),
        owner_id=owner_id,
    )
    interactions = await list_interactions(session, lead.id, owner_id=owner_id)

    assert interaction.interaction_type == LeadInteractionType.NEGOTIATION
    assert updated.notes == "Customer asked for phased delivery and O&M."
    assert updated.interaction_date == updated_date
    assert [item.id for item in interactions] == [interaction.id]
