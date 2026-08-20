from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from domains.permissions import service as permissions_service
from domains.tasks import schemas, service
from domains.tasks.models import TaskPriority, TaskStatus
from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.TaskRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    payload: schemas.TaskCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TaskRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.tasks.create",
    )
    task = await service.create_task(
        session,
        payload,
        created_by=owner_id,
    )
    return schemas.TaskRead.model_validate(task)


@router.get("/", response_model=list[schemas.TaskRead])
async def list_tasks(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.TaskRead]:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.tasks.read",
    )
    tasks = await service.list_tasks(
        session,
        owner_id=owner_id,
        status=status,
        priority=priority,
        limit=limit,
        offset=offset,
    )
    return [schemas.TaskRead.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=schemas.TaskRead)
async def read_task(
    task_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TaskRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.tasks.read",
    )
    task = await service.get_task(session, task_id, owner_id=owner_id)
    return schemas.TaskRead.model_validate(task)


@router.patch("/{task_id}", response_model=schemas.TaskRead)
async def update_task(
    task_id: int,
    payload: schemas.TaskUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TaskRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.tasks.update",
    )
    task = await service.update_task(
        session,
        task_id,
        payload,
        owner_id=owner_id,
    )
    return schemas.TaskRead.model_validate(task)


@router.post("/{task_id}/status", response_model=schemas.TaskRead)
async def change_task_status(
    task_id: int,
    body: schemas.TaskStatusChange,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TaskRead:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.tasks.update",
    )
    task = await service.update_task_status(
        session,
        task_id,
        owner_id=owner_id,
        status=body.status,
    )
    return schemas.TaskRead.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.tasks.delete",
    )
    await service.delete_task(session, task_id, owner_id=owner_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
