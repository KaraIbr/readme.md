"""Pipeline transition orchestration."""

from enum import StrEnum
from typing import cast

from core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from domains.leads.models import Lead, LeadStage
from domains.permissions import service as permissions_service
from domains.pipeline import repository
from domains.pipeline.models import PipelineEntityType, StageTransition
from domains.pipeline.schemas import PipelineSummary
from domains.proposals.models import Proposal, ProposalStage
from sqlmodel.ext.asyncio.session import AsyncSession

LEAD_STAGE_TRANSITIONS: dict[str, set[str]] = {
    LeadStage.NEW.value: {
        LeadStage.QUALIFYING.value,
        LeadStage.CLOSED_WON.value,
        LeadStage.CLOSED_LOST.value,
    },
    LeadStage.QUALIFYING.value: {
        LeadStage.PROPOSAL_PHASE.value,
        LeadStage.CLOSED_WON.value,
        LeadStage.CLOSED_LOST.value,
    },
    LeadStage.PROPOSAL_PHASE.value: {
        LeadStage.CLOSED_WON.value,
        LeadStage.CLOSED_LOST.value,
    },
    LeadStage.CLOSED_WON.value: set(),
    LeadStage.CLOSED_LOST.value: set(),
}

PROPOSAL_STAGE_TRANSITIONS: dict[str, set[str]] = {
    ProposalStage.DRAFT.value: {
        ProposalStage.SENT.value,
        ProposalStage.SUPERSEDED.value,
    },
    ProposalStage.SENT.value: {
        ProposalStage.NEGOTIATION.value,
        ProposalStage.WON.value,
        ProposalStage.LOST.value,
        ProposalStage.SUPERSEDED.value,
    },
    ProposalStage.NEGOTIATION.value: {
        ProposalStage.WON.value,
        ProposalStage.LOST.value,
        ProposalStage.SUPERSEDED.value,
    },
    ProposalStage.WON.value: set(),
    ProposalStage.LOST.value: set(),
    ProposalStage.SUPERSEDED.value: set(),
}

ALLOWED_TRANSITIONS = {
    PipelineEntityType.LEAD: LEAD_STAGE_TRANSITIONS,
    PipelineEntityType.PROPOSAL: PROPOSAL_STAGE_TRANSITIONS,
}


def _stage_value(stage: str | StrEnum) -> str:
    if isinstance(stage, StrEnum):
        return stage.value
    return stage


def _normalize_entity_type(entity_type: PipelineEntityType | str) -> PipelineEntityType:
    try:
        return PipelineEntityType(entity_type)
    except ValueError as exc:
        raise InvalidOperationError(
            "Unsupported pipeline entity type",
            details={"entity_type": str(entity_type)},
        ) from exc


async def _get_entity(
    session: AsyncSession,
    entity_type: PipelineEntityType,
    entity_id: int,
) -> Lead | Proposal:
    entity = await repository.get_entity(
        session,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    if entity is None:
        raise NotFoundError(
            "Pipeline entity not found",
            details={"entity_type": entity_type, "entity_id": entity_id},
        )
    return entity


def _current_stage(entity: Lead | Proposal) -> str:
    return entity.current_stage.value


async def _ensure_visible_to_user(
    session: AsyncSession,
    entity: Lead | Proposal,
    *,
    user_id: int,
) -> None:
    if isinstance(entity, Lead):
        assert entity.id is not None
        if not await permissions_service.user_can_access_lead(
            session,
            user_id=user_id,
            lead_id=entity.id,
        ):
            raise AuthorizationError("Pipeline entity belongs to another owner")
        return
    assert entity.id is not None
    if not await permissions_service.user_can_access_proposal(
        session,
        user_id=user_id,
        proposal_id=entity.id,
    ):
        raise AuthorizationError("Pipeline entity belongs to another user")


def _set_current_stage(
    entity: Lead | Proposal,
    *,
    entity_type: PipelineEntityType,
    stage: str,
) -> None:
    if entity_type == PipelineEntityType.LEAD:
        cast(Lead, entity).current_stage = LeadStage(stage)
        return
    cast(Proposal, entity).current_stage = ProposalStage(stage)


def ensure_transition_allowed(
    *,
    entity_type: PipelineEntityType | str,
    from_stage: str | StrEnum,
    to_stage: str | StrEnum,
) -> None:
    """Raise when a pipeline transition is not allowed."""

    normalized_type = _normalize_entity_type(entity_type)
    from_stage_value = _stage_value(from_stage)
    to_stage_value = _stage_value(to_stage)
    allowed = ALLOWED_TRANSITIONS[normalized_type].get(from_stage_value, set())
    if to_stage_value not in allowed:
        raise InvalidOperationError(
            "Invalid pipeline stage transition",
            details={
                "entity_type": normalized_type,
                "from_stage": from_stage_value,
                "to_stage": to_stage_value,
            },
        )


async def transition(
    session: AsyncSession,
    entity_type: PipelineEntityType | str,
    entity_id: int,
    *,
    to_stage: str | StrEnum,
    by: int,
    reason: str | None = None,
    notes: str | None = None,
    commit: bool = True,
) -> StageTransition | None:
    """Validate, apply, and audit a stage transition."""

    normalized_type = _normalize_entity_type(entity_type)
    entity = await _get_entity(session, normalized_type, entity_id)
    from_stage = _current_stage(entity)
    to_stage_value = _stage_value(to_stage)

    await _ensure_visible_to_user(session, entity, user_id=by)
    if from_stage == to_stage_value:
        return None

    ensure_transition_allowed(
        entity_type=normalized_type,
        from_stage=from_stage,
        to_stage=to_stage_value,
    )
    _set_current_stage(entity, entity_type=normalized_type, stage=to_stage_value)

    stage_transition = await repository.create(
        session,
        StageTransition(
            entity_type=normalized_type,
            entity_id=entity_id,
            from_stage=from_stage,
            to_stage=to_stage_value,
            transitioned_by=by,
            reason=reason,
            notes=notes,
        ),
    )
    session.add(entity)
    await session.flush()
    if commit:
        await session.commit()
    return stage_transition


async def record_initial_transition(
    session: AsyncSession,
    entity_type: PipelineEntityType | str,
    entity_id: int,
    *,
    to_stage: str | StrEnum,
    by: int,
    reason: str = "created",
    notes: str | None = None,
    commit: bool = True,
) -> StageTransition:
    """Record the initial pipeline state for a newly created entity."""

    normalized_type = _normalize_entity_type(entity_type)
    to_stage_value = _stage_value(to_stage)
    valid_stages = set(ALLOWED_TRANSITIONS[normalized_type])
    if to_stage_value not in valid_stages:
        raise InvalidOperationError(
            "Invalid initial pipeline stage",
            details={
                "entity_type": normalized_type,
                "to_stage": to_stage_value,
            },
        )

    stage_transition = await repository.create(
        session,
        StageTransition(
            entity_type=normalized_type,
            entity_id=entity_id,
            from_stage=None,
            to_stage=to_stage_value,
            transitioned_by=by,
            reason=reason,
            notes=notes,
        ),
    )
    if commit:
        await session.commit()
    return stage_transition


async def list_transitions(
    session: AsyncSession,
    *,
    user_id: int,
    entity_type: PipelineEntityType | None = None,
    entity_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[StageTransition]:
    """Return user-visible transition history."""

    transitions = await repository.list_all(
        session,
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )
    visible: list[StageTransition] = []
    for transition_item in transitions:
        entity = await repository.get_entity(
            session,
            entity_type=transition_item.entity_type,
            entity_id=transition_item.entity_id,
        )
        if entity is None:
            continue
        try:
            await _ensure_visible_to_user(session, entity, user_id=user_id)
        except AuthorizationError:
            continue
        visible.append(transition_item)
    return visible


async def summarize_entity(
    session: AsyncSession,
    *,
    user_id: int,
    entity_type: PipelineEntityType,
    entity_id: int,
) -> PipelineSummary:
    """Return a compact transition summary for one entity."""

    entity = await _get_entity(session, entity_type, entity_id)
    await _ensure_visible_to_user(session, entity, user_id=user_id)
    transition_count = await repository.count_for_entity(
        session,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    latest = await repository.latest_for_entity(
        session,
        entity_type=entity_type,
        entity_id=entity_id,
    )
    return PipelineSummary(
        entity_type=entity_type,
        entity_id=entity_id,
        current_stage=_current_stage(entity),
        transition_count=transition_count,
        last_transition_at=latest.transitioned_at if latest else None,
    )
