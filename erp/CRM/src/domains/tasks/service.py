from collections.abc import Sequence
from datetime import UTC, datetime

from core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from domains.contacts import repository as contacts_repository
from domains.leads import repository as leads_repository
from domains.opportunities import repository as opportunities_repository
from domains.tasks import repository
from domains.tasks.models import Task, TaskPriority, TaskStatus
from domains.tasks.schemas import TaskCreate, TaskUpdate
from domains.users import repository as users_repository
from sqlmodel.ext.asyncio.session import AsyncSession


async def _validate_contact(session: AsyncSession, contact_id: int, owner_id: int) -> None:
    contact = await contacts_repository.get(session, contact_id)
    if contact is None:
        raise NotFoundError("Contact not found")
    if contact.owner_id != owner_id:
        raise AuthorizationError("Contact does not belong to you")


async def _validate_lead(session: AsyncSession, lead_id: int, owner_id: int) -> None:
    lead = await leads_repository.get(session, lead_id)
    if lead is None:
        raise NotFoundError("Lead not found")
    if lead.owner_id != owner_id:
        raise AuthorizationError("Lead does not belong to you")


async def _validate_opportunity(session: AsyncSession, opportunity_id: int, owner_id: int) -> None:
    opportunity = await opportunities_repository.get(session, opportunity_id)
    if opportunity is None:
        raise NotFoundError("Opportunity not found")
    if opportunity.owner_id != owner_id:
        raise AuthorizationError("Opportunity does not belong to you")


async def _validate_user(session: AsyncSession, user_id: int) -> None:
    user = await users_repository.get(session, user_id)
    if user is None:
        raise NotFoundError("Assigned user not found")


async def create_task(
    session: AsyncSession,
    payload: TaskCreate,
    *,
    created_by: int,
) -> Task:
    if payload.contact_id is not None:
        await _validate_contact(session, payload.contact_id, created_by)
    if payload.lead_id is not None:
        await _validate_lead(session, payload.lead_id, created_by)
    if payload.opportunity_id is not None:
        await _validate_opportunity(session, payload.opportunity_id, created_by)
    if payload.assigned_to is not None:
        await _validate_user(session, payload.assigned_to)

    task = Task(
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        status=payload.status,
        priority=payload.priority,
        due_date=payload.due_date,
        contact_id=payload.contact_id,
        lead_id=payload.lead_id,
        opportunity_id=payload.opportunity_id,
        assigned_to=payload.assigned_to,
        created_by=created_by,
    )
    return await repository.create(session, task)


async def get_task(
    session: AsyncSession,
    task_id: int,
    *,
    owner_id: int,
) -> Task:
    task = await repository.get(session, task_id)
    if task is None:
        raise NotFoundError("Task not found")
    if task.created_by != owner_id:
        raise AuthorizationError("Task belongs to another user")
    return task


async def list_tasks(
    session: AsyncSession,
    *,
    owner_id: int,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Task]:
    return await repository.list_by_owner(
        session, owner_id, status=status, priority=priority, limit=limit, offset=offset
    )


async def update_task(
    session: AsyncSession,
    task_id: int,
    payload: TaskUpdate,
    *,
    owner_id: int,
) -> Task:
    task = await get_task(session, task_id, owner_id=owner_id)

    if task.completed_at is not None:
        raise InvalidOperationError("Cannot update a completed task")

    if payload.assigned_to is not None:
        await _validate_user(session, payload.assigned_to)

    for field in ("title", "description", "priority", "due_date", "assigned_to"):
        value = getattr(payload, field, None)
        if value is not None:
            if field == "title":
                setattr(task, field, value.strip())
            else:
                setattr(task, field, value)

    task.updated_at = datetime.now(UTC)
    return await repository.update(session, task)


async def update_task_status(
    session: AsyncSession,
    task_id: int,
    *,
    owner_id: int,
    status: TaskStatus,
) -> Task:
    task = await get_task(session, task_id, owner_id=owner_id)

    if task.completed_at is not None and status != TaskStatus.CANCELLED:
        raise InvalidOperationError("Cannot change status of a completed task")
    if status == TaskStatus.CANCELLED and task.completed_at is not None:
        raise InvalidOperationError("Cannot cancel a completed task")

    task.status = status
    if status == TaskStatus.DONE:
        task.completed_at = datetime.now(UTC)
    elif status == TaskStatus.TODO and task.completed_at is not None:
        task.completed_at = None
    task.updated_at = datetime.now(UTC)
    return await repository.update(session, task)


async def delete_task(
    session: AsyncSession,
    task_id: int,
    *,
    owner_id: int,
) -> None:
    task = await get_task(session, task_id, owner_id=owner_id)
    await repository.delete(session, task)
