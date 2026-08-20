from collections.abc import Sequence
from datetime import UTC, datetime

from core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from domains.contacts import repository as contacts_repository
from domains.opportunities import repository
from domains.opportunities.models import Opportunity, OpportunityOutcome, OpportunityStage
from domains.opportunities.schemas import (
    OpportunityClose,
    OpportunityCreate,
    OpportunityStageChange,
    OpportunityUpdate,
)
from sqlmodel.ext.asyncio.session import AsyncSession

FORWARD_TRANSITIONS: dict[OpportunityStage, set[OpportunityStage]] = {
    OpportunityStage.PROSPECTING: {OpportunityStage.QUALIFIED},
    OpportunityStage.QUALIFIED: {OpportunityStage.PROPOSAL},
    OpportunityStage.PROPOSAL: {OpportunityStage.NEGOTIATION},
    OpportunityStage.NEGOTIATION: {OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST},
}

TERMINAL_STAGES = {OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST}


async def create_opportunity(
    session: AsyncSession,
    payload: OpportunityCreate,
    *,
    owner_id: int,
) -> Opportunity:
    contact = await contacts_repository.get(session, payload.contact_id)
    if contact is None:
        raise NotFoundError("Contact not found")
    if contact.owner_id != owner_id:
        raise AuthorizationError("Contact belongs to another user")

    opportunity = Opportunity(
        name=payload.name.strip(),
        contact_id=payload.contact_id,
        lead_id=payload.lead_id,
        value=payload.value,
        currency=payload.currency,
        expected_close_date=payload.expected_close_date,
        notes=payload.notes,
        owner_id=owner_id,
        current_stage=OpportunityStage.PROSPECTING,
    )
    opportunity = await repository.create(session, opportunity)

    return opportunity


async def get_opportunity(
    session: AsyncSession,
    opportunity_id: int,
    *,
    owner_id: int,
) -> Opportunity:
    opportunity = await repository.get(session, opportunity_id)
    if opportunity is None:
        raise NotFoundError("Opportunity not found")
    if opportunity.owner_id != owner_id:
        raise AuthorizationError("Opportunity belongs to another user")
    return opportunity


async def list_opportunities(
    session: AsyncSession,
    *,
    owner_id: int,
    stage: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Opportunity]:
    return await repository.list_by_owner(
        session, owner_id, stage=stage, limit=limit, offset=offset
    )


async def update_opportunity(
    session: AsyncSession,
    opportunity_id: int,
    payload: OpportunityUpdate,
    *,
    owner_id: int,
) -> Opportunity:
    opportunity = await get_opportunity(session, opportunity_id, owner_id=owner_id)

    if opportunity.current_stage in TERMINAL_STAGES:
        raise InvalidOperationError("Cannot update a closed opportunity")

    for field in ("name", "value", "currency", "expected_close_date", "notes"):
        value = getattr(payload, field, None)
        if value is not None:
            setattr(opportunity, field, value.strip() if field == "name" else value)

    opportunity.updated_at = datetime.now(UTC)
    return await repository.update(session, opportunity)


async def move_to_stage(
    session: AsyncSession,
    opportunity_id: int,
    payload: OpportunityStageChange,
    *,
    owner_id: int,
) -> Opportunity:
    opportunity = await get_opportunity(session, opportunity_id, owner_id=owner_id)

    if opportunity.current_stage in TERMINAL_STAGES:
        raise InvalidOperationError("Cannot move a closed opportunity")

    target = payload.stage
    allowed = FORWARD_TRANSITIONS.get(opportunity.current_stage, set())
    if target not in allowed:
        raise InvalidOperationError(
            f"Cannot move from {opportunity.current_stage.value} to {target.value}"
        )

    opportunity.current_stage = target
    opportunity.updated_at = datetime.now(UTC)
    if target in TERMINAL_STAGES:
        opportunity.closed_at = opportunity.updated_at
        opportunity.outcome = (
            OpportunityOutcome.WON
            if target == OpportunityStage.CLOSED_WON
            else OpportunityOutcome.LOST
        )

    result = await repository.update(session, opportunity)

    return result


async def close_opportunity(
    session: AsyncSession,
    opportunity_id: int,
    payload: OpportunityClose,
    *,
    owner_id: int,
) -> Opportunity:
    opportunity = await get_opportunity(session, opportunity_id, owner_id=owner_id)

    if opportunity.current_stage in TERMINAL_STAGES:
        raise InvalidOperationError("Opportunity is already closed")

    if payload.outcome == "WON" and opportunity.current_stage != OpportunityStage.NEGOTIATION:
        raise InvalidOperationError("WON can only come from NEGOTIATION stage")

    if payload.outcome == "WON":
        target = OpportunityStage.CLOSED_WON
    elif payload.outcome == "LOST":
        target = OpportunityStage.CLOSED_LOST
    else:
        raise InvalidOperationError(f"Invalid outcome: {payload.outcome}")

    opportunity.current_stage = target
    opportunity.outcome = OpportunityOutcome(payload.outcome)
    opportunity.closed_at = datetime.now(UTC)
    opportunity.updated_at = opportunity.closed_at
    if payload.notes:
        opportunity.notes = (opportunity.notes or "") + f"\n[Closed: {payload.notes}]"

    return await repository.update(session, opportunity)


async def delete_opportunity(
    session: AsyncSession,
    opportunity_id: int,
    *,
    owner_id: int,
) -> None:
    opportunity = await get_opportunity(session, opportunity_id, owner_id=owner_id)
    await repository.delete(session, opportunity)
