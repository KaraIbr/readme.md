"""IAM service-access business logic."""

from datetime import UTC, datetime
from typing import Final

from sqlmodel.ext.asyncio.session import AsyncSession

from iam.core.exceptions import InvalidOperationError
from iam.domains.permissions import service as permissions_service
from iam.domains.services import repository
from iam.domains.services.models import ServiceAccess
from iam.domains.services.schemas import normalize_service_key
from iam.domains.users.service import get_active_user

SERVICES: Final[dict[str, str]] = {
    "crm": "Renewable-energy CRM service",
}


def _validate_service_key(service_key: str) -> str:
    normalized = normalize_service_key(service_key)
    if normalized not in SERVICES:
        raise InvalidOperationError(
            "Unknown VERP service",
            details={"service_key": normalized},
        )
    return normalized


async def list_services() -> dict[str, str]:
    """Return the known VERP service catalog."""

    return SERVICES


async def grant_service_access(
    session: AsyncSession,
    *,
    actor_id: int,
    user_id: int,
    service_key: str,
) -> ServiceAccess:
    """Grant or reactivate access to one VERP service."""

    await permissions_service.require_permission(
        session,
        actor_id,
        "iam.services.manage",
    )
    await get_active_user(session, user_id)
    normalized_key = _validate_service_key(service_key)
    existing = await repository.get_user_service_access(
        session,
        user_id,
        normalized_key,
    )
    if existing is not None:
        existing.is_active = True
        existing.granted_by = actor_id
        existing.updated_at = datetime.now(UTC)
        access = await repository.save(session, existing)
        await session.commit()
        return access

    access = await repository.save(
        session,
        ServiceAccess(
            user_id=user_id,
            service_key=normalized_key,
            granted_by=actor_id,
        ),
    )
    await session.commit()
    return access


async def revoke_service_access(
    session: AsyncSession,
    *,
    actor_id: int,
    user_id: int,
    service_key: str,
) -> None:
    """Revoke access to one VERP service without deleting history."""

    await permissions_service.require_permission(
        session,
        actor_id,
        "iam.services.manage",
    )
    await get_active_user(session, user_id)
    normalized_key = _validate_service_key(service_key)
    access = await repository.get_user_service_access(session, user_id, normalized_key)
    if access is None:
        return
    access.is_active = False
    access.updated_at = datetime.now(UTC)
    await repository.save(session, access)
    await session.commit()


async def list_user_service_access(
    session: AsyncSession,
    *,
    actor_id: int,
    user_id: int,
) -> list[ServiceAccess]:
    """Return service-access rows for one user."""

    await permissions_service.require_permission(session, actor_id, "iam.services.read")
    await get_active_user(session, user_id)
    return list(await repository.list_user_service_access(session, user_id))


async def user_has_service_access(
    session: AsyncSession,
    *,
    user_id: int,
    service_key: str,
) -> bool:
    """Return whether one active user has active access to a service."""

    await get_active_user(session, user_id)
    normalized_key = _validate_service_key(service_key)
    access = await repository.get_user_service_access(session, user_id, normalized_key)
    return access is not None and access.is_active
