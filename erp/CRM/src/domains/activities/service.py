from collections.abc import Sequence
from datetime import UTC, datetime

from core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from domains.activities import repository
from domains.activities.models import Activity
from domains.activities.schemas import ActivityCreate, ActivityUpdate
from domains.contacts import repository as contacts_repository
from domains.leads import repository as leads_repository
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


async def _validate_user(session: AsyncSession, user_id: int) -> None:
    user = await users_repository.get(session, user_id)
    if user is None:
        raise NotFoundError("Assigned user not found")


async def create_activity(
    session: AsyncSession,
    payload: ActivityCreate,
    *,
    created_by: int,
) -> Activity:
    if payload.contact_id is not None:
        await _validate_contact(session, payload.contact_id, created_by)
    if payload.lead_id is not None:
        await _validate_lead(session, payload.lead_id, created_by)
    if payload.assigned_to is not None:
        await _validate_user(session, payload.assigned_to)

    activity = Activity(
        activity_type=payload.activity_type,
        title=payload.title.strip(),
        description=payload.description.strip() if payload.description else None,
        contact_id=payload.contact_id,
        lead_id=payload.lead_id,
        assigned_to=payload.assigned_to,
        scheduled_at=payload.scheduled_at,
        created_by=created_by,
    )
    return await repository.create(session, activity)


async def get_activity(
    session: AsyncSession,
    activity_id: int,
    *,
    owner_id: int,
) -> Activity:
    activity = await repository.get(session, activity_id)
    if activity is None:
        raise NotFoundError("Activity not found")
    if activity.created_by != owner_id:
        raise AuthorizationError("Activity belongs to another user")
    return activity


async def list_activities(
    session: AsyncSession,
    *,
    owner_id: int,
    activity_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Activity]:
    return await repository.list_by_owner(
        session, owner_id, activity_type=activity_type, limit=limit, offset=offset
    )


async def update_activity(
    session: AsyncSession,
    activity_id: int,
    payload: ActivityUpdate,
    *,
    owner_id: int,
) -> Activity:
    activity = await get_activity(session, activity_id, owner_id=owner_id)

    if activity.completed_at is not None:
        raise InvalidOperationError("Cannot update a completed activity")

    if payload.assigned_to is not None:
        await _validate_user(session, payload.assigned_to)

    for field in ("activity_type", "title", "description", "assigned_to", "scheduled_at"):
        value = getattr(payload, field, None)
        if value is not None:
            if field == "title":
                setattr(activity, field, value.strip())
            else:
                setattr(activity, field, value)

    activity.updated_at = datetime.now(UTC)
    return await repository.update(session, activity)


async def complete_activity(
    session: AsyncSession,
    activity_id: int,
    *,
    owner_id: int,
) -> Activity:
    activity = await get_activity(session, activity_id, owner_id=owner_id)

    if activity.completed_at is not None:
        raise InvalidOperationError("Activity is already completed")

    activity.completed_at = datetime.now(UTC)
    activity.updated_at = activity.completed_at
    return await repository.update(session, activity)


async def delete_activity(
    session: AsyncSession,
    activity_id: int,
    *,
    owner_id: int,
) -> None:
    activity = await get_activity(session, activity_id, owner_id=owner_id)
    await repository.delete(session, activity)
