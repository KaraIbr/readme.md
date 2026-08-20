"""IAM service-access data access functions."""

from collections.abc import Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.domains.services.models import ServiceAccess


async def get_user_service_access(
    session: AsyncSession,
    user_id: int,
    service_key: str,
) -> ServiceAccess | None:
    """Return one service-access row for a user."""

    result = await session.exec(
        select(ServiceAccess).where(
            ServiceAccess.user_id == user_id,
            ServiceAccess.service_key == service_key,
        )
    )
    return result.first()


async def list_user_service_access(
    session: AsyncSession,
    user_id: int,
) -> Sequence[ServiceAccess]:
    """Return all service-access rows for one user."""

    result = await session.exec(select(ServiceAccess).where(ServiceAccess.user_id == user_id))
    return result.all()


async def save(
    session: AsyncSession,
    access: ServiceAccess,
) -> ServiceAccess:
    """Persist a service-access row."""

    session.add(access)
    await session.flush()
    await session.refresh(access)
    return access
