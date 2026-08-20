"""IAM users HTTP router."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import text
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.api.dependencies import CurrentUser, get_db_session
from iam.core.config import Settings, get_settings
from iam.core.exceptions import AuthenticationError
from iam.core.security import InvalidTokenError, decode_token
from iam.domains.users import schemas, service
from iam.domains.users.models import User

router = APIRouter()
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    auto_error=False,
)


def _user_id(current_user: CurrentUser) -> int:
    user_id = current_user.id
    assert user_id is not None
    return user_id


async def _optional_current_user(
    token: Annotated[str | None, Depends(optional_oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> User | None:
    if settings.dev_bootstrap_enabled and not settings.is_development:
        raise RuntimeError("DEV_BOOTSTRAP_ENABLED=true is not allowed outside development")

    if token is None:
        if settings.is_development and settings.dev_bootstrap_enabled:
            from sqlmodel import select

            from iam.domains.users.models import User

            result = await session.exec(select(User).where(User.is_active).limit(1))
            return result.first()
        return None
    try:
        payload = decode_token(token, expected_type="access")
        user_id = int(payload["sub"])
    except (InvalidTokenError, KeyError, TypeError, ValueError) as exc:
        raise AuthenticationError("Invalid authentication credentials") from exc
    return await service.get_active_user(session, user_id)


@router.get("/", response_model=list[schemas.AdminUserRead])
async def list_users(
    session: Annotated[AsyncSession, Depends(get_db_session)],
    actor: Annotated[User | None, Depends(_optional_current_user)],
) -> list[schemas.AdminUserRead]:
    """List all central users (admin endpoint, optionally authenticated in dev)."""

    users = await service.list_users(session)

    # Cross-service: read CRM roles from shared database
    result = await session.execute(text("SELECT user_id, role FROM crm_user_access"))
    role_map: dict[int, str | None] = {}
    for row in result:
        role_map[row[0]] = row[1].upper() if row[1] else None

    admins: list[schemas.AdminUserRead] = []
    for u in users:
        if u.id is None:
            continue
        admins.append(
            schemas.AdminUserRead(
                id=u.id,
                email=u.email,
                full_name=u.full_name,
                is_active=u.is_active,
                role=role_map.get(u.id),
                last_login=None,
                created_at=u.created_at.isoformat(),
            )
        )
    return admins


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: schemas.UserCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    actor: Annotated[User | None, Depends(_optional_current_user)],
) -> schemas.UserRead:
    """Create a central VERP user account."""

    user = await service.create_bootstrap_or_permitted_user(
        session,
        payload,
        actor=actor,
    )
    return schemas.UserRead.model_validate(user)


@router.get("/me", response_model=schemas.UserRead)
async def read_me(current_user: CurrentUser) -> schemas.UserRead:
    """Return the authenticated central IAM user."""

    return schemas.UserRead.model_validate(current_user)


@router.get("/{user_id}", response_model=schemas.UserRead)
async def read_user(
    user_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.UserRead:
    """Return one central IAM user."""

    user = await service.read_user(
        session,
        actor_id=_user_id(current_user),
        user_id=user_id,
    )
    return schemas.UserRead.model_validate(user)


@router.patch("/{user_id}", response_model=schemas.UserRead)
async def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.UserRead:
    """Update one central IAM user."""

    user = await service.update_user(
        session,
        actor_id=_user_id(current_user),
        user_id=user_id,
        user_update=payload,
    )
    return schemas.UserRead.model_validate(user)


@router.post("/{user_id}/activate", response_model=schemas.UserRead)
async def activate_user(
    user_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.UserRead:
    """Activate one central IAM user."""

    user = await service.set_user_active(
        session,
        actor_id=_user_id(current_user),
        user_id=user_id,
        is_active=True,
    )
    return schemas.UserRead.model_validate(user)


@router.delete("/{user_id}", response_model=schemas.UserRead)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.UserRead:
    """Permanently delete one central IAM user."""

    user = await service.delete_user_permanently(
        session,
        actor_id=_user_id(current_user),
        user_id=user_id,
    )
    return schemas.UserRead.model_validate(user)


@router.post("/{user_id}/deactivate", response_model=schemas.UserRead)
async def deactivate_user(
    user_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.UserRead:
    """Deactivate one central IAM user."""

    user = await service.set_user_active(
        session,
        actor_id=_user_id(current_user),
        user_id=user_id,
        is_active=False,
    )
    return schemas.UserRead.model_validate(user)
