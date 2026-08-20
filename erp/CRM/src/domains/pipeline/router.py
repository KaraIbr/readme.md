"""Pipeline HTTP router."""

from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from domains.permissions import service as permissions_service
from domains.pipeline import schemas, service
from domains.pipeline.models import PipelineEntityType
from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


def _user_id(current_user: CurrentUser) -> int:
    user_id = current_user.id
    assert user_id is not None
    return user_id


@router.get("/transitions", response_model=list[schemas.StageTransitionRead])
async def list_transitions(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    entity_type: PipelineEntityType | None = None,
    entity_id: Annotated[int | None, Query(gt=0)] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.StageTransitionRead]:
    """Return stage transition history for the authenticated user."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.pipeline.read",
    )
    transitions = await service.list_transitions(
        session,
        user_id=_user_id(current_user),
        entity_type=entity_type,
        entity_id=entity_id,
        limit=limit,
        offset=offset,
    )
    return [schemas.StageTransitionRead.model_validate(item) for item in transitions]


@router.get("/summary/{entity_type}/{entity_id}", response_model=schemas.PipelineSummary)
async def summarize_entity(
    entity_type: PipelineEntityType,
    entity_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.PipelineSummary:
    """Return a compact pipeline summary for one entity."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.pipeline.read",
    )
    return await service.summarize_entity(
        session,
        user_id=_user_id(current_user),
        entity_type=entity_type,
        entity_id=entity_id,
    )
