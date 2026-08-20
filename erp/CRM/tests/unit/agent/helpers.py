"""Test helpers for agent unit tests."""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from agent.providers.base import LLMProvider
from core.config import Settings
from core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from domains.contacts.models import ContactType
from domains.contacts.schemas import (
    CompanyContactPersonCreate,
    ContactCreate,
    PromoterCreate,
)
from domains.contacts.service import create_contact, create_promoter
from domains.leads.models import LeadInterestType
from domains.leads.schemas import LeadCreate
from domains.leads.service import create_lead
from domains.proposals.models import ProposalSystemType
from domains.proposals.schemas import (
    ProposalCreate,
    ProposalInstallationAddress,
    ProposalPVSystemPayload,
)
from domains.proposals.service import create_proposal
from helpers import create_iam_user
from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
from langchain_core.messages import BaseMessage
from pydantic import SecretStr


class ToolAwareFakeChatModel(FakeMessagesListChatModel):
    """Fake chat model that accepts tool binding in graph tests."""

    def bind_tools(self, tools, **kwargs):  # noqa: ANN001, ANN201
        return self


class FakeProvider(LLMProvider):
    """LLM provider that returns a deterministic fake chat model."""

    def __init__(self, responses: list[BaseMessage]) -> None:
        self._responses = responses

    def chat_model(self) -> ToolAwareFakeChatModel:
        return ToolAwareFakeChatModel(responses=self._responses)


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


async def create_owner(session, email: str = "owner@example.com"):
    user = await create_iam_user(session, email=email)
    assert user.id is not None
    return user


async def create_crm_fixture(session, owner_id: int):
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
            name="Acme Manufacturing",
            promoter_id=promoter.id,
            city="Monterrey",
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
    proposal = await create_proposal(
        session,
        ProposalCreate(
            lead_id=lead.id,
            name="Acme technical option",
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
        ),
        created_by=owner_id,
    )
    assert proposal.id is not None
    return contact, lead, proposal
