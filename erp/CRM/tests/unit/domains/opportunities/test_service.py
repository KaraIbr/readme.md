import pytest
from core.config import Settings
from core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from domains.contacts.models import ContactType
from domains.contacts.schemas import (
    CompanyContactPersonCreate,
    ContactCreate,
    PromoterCreate,
)
from domains.contacts.service import create_contact, create_promoter
from domains.opportunities.models import OpportunityStage
from domains.opportunities.schemas import (
    OpportunityClose,
    OpportunityCreate,
    OpportunityStageChange,
    OpportunityUpdate,
)
from domains.opportunities.service import (
    close_opportunity,
    create_opportunity,
    delete_opportunity,
    get_opportunity,
    list_opportunities,
    move_to_stage,
    update_opportunity,
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


@pytest.mark.asyncio
async def test_create_opportunity_assigns_owner_and_default_stage(session) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)

    opportunity = await create_opportunity(
        session,
        OpportunityCreate(
            name="  Solar Project - Acme  ",
            contact_id=contact_id,
            value=50000.0,
            currency="MXN",
        ),
        owner_id=owner_id,
    )

    assert opportunity.id is not None
    assert opportunity.owner_id == owner_id
    assert opportunity.name == "Solar Project - Acme"
    assert opportunity.current_stage == OpportunityStage.PROSPECTING
    assert opportunity.value == 50000.0
    assert opportunity.outcome is None
    assert opportunity.closed_at is None


@pytest.mark.asyncio
async def test_create_opportunity_rejects_other_owner_contact(session) -> None:
    owner_id = await _create_owner(session)
    other_id = await _create_owner(session, "other@example.com")
    other_contact_id = await _create_contact(session, other_id)

    with pytest.raises(AuthorizationError):
        await create_opportunity(
            session,
            OpportunityCreate(
                name="Solar Project",
                contact_id=other_contact_id,
            ),
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_list_opportunities_is_owner_scoped(session) -> None:
    owner_id = await _create_owner(session)
    other_id = await _create_owner(session, "other@example.com")
    contact_id = await _create_contact(session, owner_id)
    other_contact_id = await _create_contact(session, other_id)

    await create_opportunity(
        session,
        OpportunityCreate(name="My opp", contact_id=contact_id),
        owner_id=owner_id,
    )
    await create_opportunity(
        session,
        OpportunityCreate(name="Other opp", contact_id=other_contact_id),
        owner_id=other_id,
    )

    opportunities = await list_opportunities(session, owner_id=owner_id)

    assert len(opportunities) == 1
    assert opportunities[0].name == "My opp"


@pytest.mark.asyncio
async def test_stage_transitions_forward(session) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)

    opp = await create_opportunity(
        session,
        OpportunityCreate(name="Project", contact_id=contact_id),
        owner_id=owner_id,
    )
    assert opp.id is not None

    qualified = await move_to_stage(
        session,
        opp.id,
        OpportunityStageChange(stage=OpportunityStage.QUALIFIED),
        owner_id=owner_id,
    )
    assert qualified.current_stage == OpportunityStage.QUALIFIED

    proposal = await move_to_stage(
        session,
        opp.id,
        OpportunityStageChange(stage=OpportunityStage.PROPOSAL),
        owner_id=owner_id,
    )
    assert proposal.current_stage == OpportunityStage.PROPOSAL

    with pytest.raises(InvalidOperationError):
        await move_to_stage(
            session,
            opp.id,
            OpportunityStageChange(stage=OpportunityStage.CLOSED_WON),
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_cannot_update_closed_opportunity(session) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)

    opp = await create_opportunity(
        session,
        OpportunityCreate(name="Project", contact_id=contact_id),
        owner_id=owner_id,
    )
    assert opp.id is not None

    # Move to NEGOTIATION first
    for stage in [
        OpportunityStage.QUALIFIED,
        OpportunityStage.PROPOSAL,
        OpportunityStage.NEGOTIATION,
    ]:
        opp = await move_to_stage(
            session,
            opp.id,
            OpportunityStageChange(stage=stage),
            owner_id=owner_id,
        )

    closed = await close_opportunity(
        session,
        opp.id,
        OpportunityClose(outcome="WON"),
        owner_id=owner_id,
    )
    assert closed.current_stage == OpportunityStage.CLOSED_WON

    with pytest.raises(InvalidOperationError):
        await update_opportunity(
            session,
            opp.id,
            OpportunityUpdate(name="Changed"),
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_close_opportunity(session) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)

    opp = await create_opportunity(
        session,
        OpportunityCreate(name="Project", contact_id=contact_id),
        owner_id=owner_id,
    )
    assert opp.id is not None

    for stage in [
        OpportunityStage.QUALIFIED,
        OpportunityStage.PROPOSAL,
        OpportunityStage.NEGOTIATION,
    ]:
        opp = await move_to_stage(
            session,
            opp.id,
            OpportunityStageChange(stage=stage),
            owner_id=owner_id,
        )

    closed = await close_opportunity(
        session,
        opp.id,
        OpportunityClose(outcome="WON", notes="Deal signed"),
        owner_id=owner_id,
    )
    assert closed.current_stage == OpportunityStage.CLOSED_WON
    assert closed.outcome == "WON"
    assert closed.closed_at is not None
    assert "Deal signed" in (closed.notes or "")


@pytest.mark.asyncio
async def test_delete_opportunity(session) -> None:
    owner_id = await _create_owner(session)
    contact_id = await _create_contact(session, owner_id)

    opp = await create_opportunity(
        session,
        OpportunityCreate(name="Delete me", contact_id=contact_id),
        owner_id=owner_id,
    )
    assert opp.id is not None

    await delete_opportunity(session, opp.id, owner_id=owner_id)

    with pytest.raises(NotFoundError):
        await get_opportunity(session, opp.id, owner_id=owner_id)
