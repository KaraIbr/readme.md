"""Pipeline data access functions."""

from collections.abc import Sequence
from typing import Any, cast

from domains.leads.models import Lead
from domains.pipeline.models import PipelineEntityType, StageTransition
from domains.proposals.models import Proposal
from sqlalchemy import desc
from sqlalchemy.sql.elements import ColumnElement
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def create(
    session: AsyncSession,
    transition: StageTransition,
) -> StageTransition:
    """Persist and refresh a stage transition audit record."""

    session.add(transition)
    await session.flush()
    await session.refresh(transition)
    return transition


async def get_entity(
    session: AsyncSession,
    *,
    entity_type: PipelineEntityType,
    entity_id: int,
) -> Lead | Proposal | None:
    """Return the pipeline-backed domain entity by type and primary key."""

    if entity_type == PipelineEntityType.LEAD:
        return await session.get(Lead, entity_id)
    return await session.get(Proposal, entity_id)


async def list_for_user(
    session: AsyncSession,
    user_id: int,
    *,
    entity_type: PipelineEntityType | None = None,
    entity_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[StageTransition]:
    """Return transition history written by a user."""

    statement = (
        select(StageTransition)
        .where(StageTransition.transitioned_by == user_id)
        .order_by(
            desc(cast(ColumnElement[Any], StageTransition.transitioned_at)),
            desc(cast(ColumnElement[Any], StageTransition.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if entity_type is not None:
        statement = statement.where(StageTransition.entity_type == entity_type)
    if entity_id is not None:
        statement = statement.where(StageTransition.entity_id == entity_id)

    result = await session.exec(statement)
    return result.all()


async def list_all(
    session: AsyncSession,
    *,
    entity_type: PipelineEntityType | None = None,
    entity_id: int | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[StageTransition]:
    """Return transition history across users."""

    statement = (
        select(StageTransition)
        .order_by(
            desc(cast(ColumnElement[Any], StageTransition.transitioned_at)),
            desc(cast(ColumnElement[Any], StageTransition.id)),
        )
        .limit(limit)
        .offset(offset)
    )
    if entity_type is not None:
        statement = statement.where(StageTransition.entity_type == entity_type)
    if entity_id is not None:
        statement = statement.where(StageTransition.entity_id == entity_id)

    result = await session.exec(statement)
    return result.all()


async def count_for_entity(
    session: AsyncSession,
    *,
    entity_type: PipelineEntityType,
    entity_id: int,
) -> int:
    """Return the number of transitions for one entity."""

    statement = select(StageTransition).where(
        StageTransition.entity_type == entity_type,
        StageTransition.entity_id == entity_id,
    )
    result = await session.exec(statement)
    return len(result.all())


async def latest_for_entity(
    session: AsyncSession,
    *,
    entity_type: PipelineEntityType,
    entity_id: int,
) -> StageTransition | None:
    """Return the latest transition for one entity."""

    statement = (
        select(StageTransition)
        .where(
            StageTransition.entity_type == entity_type,
            StageTransition.entity_id == entity_id,
        )
        .order_by(
            desc(cast(ColumnElement[Any], StageTransition.transitioned_at)),
            desc(cast(ColumnElement[Any], StageTransition.id)),
        )
    )
    result = await session.exec(statement)
    return result.first()
