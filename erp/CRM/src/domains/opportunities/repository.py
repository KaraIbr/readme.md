from collections.abc import Sequence

from domains.opportunities.models import Opportunity
from sqlalchemy import desc
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def create(session: AsyncSession, opportunity: Opportunity) -> Opportunity:
    session.add(opportunity)
    await session.commit()
    await session.refresh(opportunity)
    return opportunity


async def get(session: AsyncSession, opportunity_id: int) -> Opportunity | None:
    return await session.get(Opportunity, opportunity_id)


async def list_by_owner(
    session: AsyncSession,
    owner_id: int,
    *,
    stage: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Opportunity]:
    query = (
        select(Opportunity)
        .where(Opportunity.owner_id == owner_id)
        .order_by(desc(Opportunity.created_at))  # type: ignore[arg-type]
        .offset(offset)
        .limit(limit)
    )
    if stage:
        query = query.where(Opportunity.current_stage == stage)
    result = await session.exec(query)
    return result.all()


async def update(session: AsyncSession, opportunity: Opportunity) -> Opportunity:
    session.add(opportunity)
    await session.commit()
    await session.refresh(opportunity)
    return opportunity


async def delete(session: AsyncSession, opportunity: Opportunity) -> None:
    await session.delete(opportunity)
    await session.commit()
