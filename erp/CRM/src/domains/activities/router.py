from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from domains.activities import schemas, service
from domains.permissions import service as permissions_service
from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.ActivityRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_activity(
    payload: schemas.ActivityCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ActivityRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.activities.create",
    )
    activity = await service.create_activity(
        session,
        payload,
        created_by=owner_id,
    )
    return schemas.ActivityRead.model_validate(activity)


@router.get("/", response_model=list[schemas.ActivityRead])
async def list_activities(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    activity_type: str | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.ActivityRead]:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.activities.read",
    )
    activities = await service.list_activities(
        session,
        owner_id=owner_id,
        activity_type=activity_type,
        limit=limit,
        offset=offset,
    )
    return [schemas.ActivityRead.model_validate(a) for a in activities]


@router.get("/{activity_id}", response_model=schemas.ActivityRead)
async def read_activity(
    activity_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ActivityRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.activities.read",
    )
    activity = await service.get_activity(
        session,
        activity_id,
        owner_id=owner_id,
    )
    return schemas.ActivityRead.model_validate(activity)


@router.patch("/{activity_id}", response_model=schemas.ActivityRead)
async def update_activity(
    activity_id: int,
    payload: schemas.ActivityUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ActivityRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.activities.update",
    )
    activity = await service.update_activity(
        session,
        activity_id,
        payload,
        owner_id=owner_id,
    )
    return schemas.ActivityRead.model_validate(activity)


@router.post(
    "/{activity_id}/complete",
    response_model=schemas.ActivityRead,
)
async def complete_activity(
    activity_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ActivityRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.activities.update",
    )
    activity = await service.complete_activity(
        session,
        activity_id,
        owner_id=owner_id,
    )
    return schemas.ActivityRead.model_validate(activity)


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.activities.delete",
    )
    await service.delete_activity(session, activity_id, owner_id=owner_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
