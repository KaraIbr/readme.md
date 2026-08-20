from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from domains.opportunities import schemas, service
from domains.permissions import service as permissions_service
from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.OpportunityRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_opportunity(
    payload: schemas.OpportunityCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OpportunityRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.opportunities.create",
    )
    opportunity = await service.create_opportunity(
        session,
        payload,
        owner_id=owner_id,
    )
    return schemas.OpportunityRead.model_validate(opportunity)


@router.get("/", response_model=list[schemas.OpportunityRead])
async def list_opportunities(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    stage: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.OpportunityRead]:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.opportunities.read",
    )
    opportunities = await service.list_opportunities(
        session,
        owner_id=owner_id,
        stage=stage,
        limit=limit,
        offset=offset,
    )
    return [schemas.OpportunityRead.model_validate(o) for o in opportunities]


@router.get("/{opportunity_id}", response_model=schemas.OpportunityRead)
async def read_opportunity(
    opportunity_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OpportunityRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.opportunities.read",
    )
    opportunity = await service.get_opportunity(
        session,
        opportunity_id,
        owner_id=owner_id,
    )
    return schemas.OpportunityRead.model_validate(opportunity)


@router.patch("/{opportunity_id}", response_model=schemas.OpportunityRead)
async def update_opportunity(
    opportunity_id: int,
    payload: schemas.OpportunityUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OpportunityRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.opportunities.update",
    )
    opportunity = await service.update_opportunity(
        session,
        opportunity_id,
        payload,
        owner_id=owner_id,
    )
    return schemas.OpportunityRead.model_validate(opportunity)


@router.post(
    "/{opportunity_id}/stage",
    response_model=schemas.OpportunityRead,
)
async def move_opportunity_stage(
    opportunity_id: int,
    payload: schemas.OpportunityStageChange,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OpportunityRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.opportunities.stage.update",
    )
    opportunity = await service.move_to_stage(
        session,
        opportunity_id,
        payload,
        owner_id=owner_id,
    )
    return schemas.OpportunityRead.model_validate(opportunity)


@router.post(
    "/{opportunity_id}/close",
    response_model=schemas.OpportunityRead,
)
async def close_opportunity(
    opportunity_id: int,
    payload: schemas.OpportunityClose,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OpportunityRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.opportunities.close",
    )
    opportunity = await service.close_opportunity(
        session,
        opportunity_id,
        payload,
        owner_id=owner_id,
    )
    return schemas.OpportunityRead.model_validate(opportunity)


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_opportunity(
    opportunity_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.opportunities.delete",
    )
    await service.delete_opportunity(session, opportunity_id, owner_id=owner_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
