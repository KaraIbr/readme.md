from collections.abc import Sequence

from domains.activities.models import Activity
from sqlalchemy import desc
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def create(session: AsyncSession, activity: Activity) -> Activity:
    session.add(activity)
    await session.commit()
    await session.refresh(activity)
    return activity


async def get(session: AsyncSession, activity_id: int) -> Activity | None:
    return await session.get(Activity, activity_id)


async def list_by_owner(
    session: AsyncSession,
    owner_id: int,
    *,
    activity_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Activity]:
    query = (
        select(Activity)
        .where(Activity.created_by == owner_id)
        .order_by(desc(Activity.created_at))  # type: ignore[arg-type]
        .offset(offset)
        .limit(limit)
    )
    if activity_type:
        query = query.where(Activity.activity_type == activity_type)
    result = await session.exec(query)
    return result.all()


async def update(session: AsyncSession, activity: Activity) -> Activity:
    session.add(activity)
    await session.commit()
    await session.refresh(activity)
    return activity


async def delete(session: AsyncSession, activity: Activity) -> None:
    await session.delete(activity)
    await session.commit()
