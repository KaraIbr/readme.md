"""IAM permission data access functions."""

from collections.abc import Sequence

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from iam.domains.permissions.models import IAMUserPermissionOverride


async def list_user_overrides(
    session: AsyncSession,
    user_id: int,
) -> Sequence[IAMUserPermissionOverride]:
    """Return IAM permission overrides for one user."""

    result = await session.exec(
        select(IAMUserPermissionOverride).where(IAMUserPermissionOverride.user_id == user_id)
    )
    return result.all()


async def get_user_override(
    session: AsyncSession,
    user_id: int,
    permission: str,
) -> IAMUserPermissionOverride | None:
    """Return one IAM permission override."""

    result = await session.exec(
        select(IAMUserPermissionOverride).where(
            IAMUserPermissionOverride.user_id == user_id,
            IAMUserPermissionOverride.permission == permission,
        )
    )
    return result.first()


async def save_override(
    session: AsyncSession,
    override: IAMUserPermissionOverride,
) -> IAMUserPermissionOverride:
    """Persist an IAM permission override."""

    session.add(override)
    await session.flush()
    await session.refresh(override)
    return override


async def delete_override(
    session: AsyncSession,
    override: IAMUserPermissionOverride,
) -> None:
    """Delete one IAM permission override."""

    await session.delete(override)
