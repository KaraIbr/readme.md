from collections.abc import Sequence

from domains.tasks.models import Task, TaskPriority, TaskStatus
from sqlalchemy import desc
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


async def create(session: AsyncSession, task: Task) -> Task:
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get(session: AsyncSession, task_id: int) -> Task | None:
    return await session.get(Task, task_id)


async def list_by_owner(
    session: AsyncSession,
    owner_id: int,
    *,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Task]:
    query = (
        select(Task)
        .where(Task.created_by == owner_id)
        .order_by(desc(Task.created_at))  # type: ignore[arg-type]
        .offset(offset)
        .limit(limit)
    )
    if status:
        query = query.where(Task.status == status)
    if priority:
        query = query.where(Task.priority == priority)
    result = await session.exec(query)
    return result.all()


async def update(session: AsyncSession, task: Task) -> Task:
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def delete(session: AsyncSession, task: Task) -> None:
    await session.delete(task)
    await session.commit()
