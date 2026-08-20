"""IAM service-access HTTP router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.api.dependencies import CurrentUser, get_db_session
from iam.domains.permissions import service as permissions_service
from iam.domains.services import schemas, service

router = APIRouter()


def _user_id(current_user: CurrentUser) -> int:
    user_id = current_user.id
    assert user_id is not None
    return user_id


@router.get("/", response_model=list[schemas.ServiceRead])
async def list_services(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[schemas.ServiceRead]:
    """Return the known VERP service catalog."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "iam.services.read",
    )
    return [
        schemas.ServiceRead(key=key, description=description)
        for key, description in sorted((await service.list_services()).items())
    ]


@router.get("/users/{user_id}", response_model=list[schemas.ServiceAccessRead])
async def list_user_service_access(
    user_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[schemas.ServiceAccessRead]:
    """Return service access rows for one user."""

    rows = await service.list_user_service_access(
        session,
        actor_id=_user_id(current_user),
        user_id=user_id,
    )
    return [schemas.ServiceAccessRead.model_validate(row) for row in rows]


@router.post(
    "/users/{user_id}/access",
    response_model=schemas.ServiceAccessRead,
    status_code=status.HTTP_201_CREATED,
)
async def grant_service_access(
    user_id: int,
    payload: schemas.ServiceAccessCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ServiceAccessRead:
    """Grant one user access to a VERP service."""

    access = await service.grant_service_access(
        session,
        actor_id=_user_id(current_user),
        user_id=user_id,
        service_key=payload.service_key,
    )
    return schemas.ServiceAccessRead.model_validate(access)


@router.delete(
    "/users/{user_id}/access/{service_key}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def revoke_service_access(
    user_id: int,
    service_key: str,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Revoke one user's access to a VERP service."""

    await service.revoke_service_access(
        session,
        actor_id=_user_id(current_user),
        user_id=user_id,
        service_key=service_key,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
