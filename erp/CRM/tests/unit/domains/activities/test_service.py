import pytest
from core.config import Settings
from core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from core.exceptions import AuthorizationError, InvalidOperationError
from domains.activities.models import ActivityType
from domains.activities.schemas import ActivityCreate, ActivityUpdate
from domains.activities.service import (
    complete_activity,
    create_activity,
    delete_activity,
    get_activity,
    list_activities,
    update_activity,
)
from helpers import create_iam_user
from pydantic import SecretStr


@pytest.fixture()
async def session():
    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        jwt_secret_key=SecretStr("super-secret-for-tests"),
    )
    engine = build_async_engine(settings)
    await create_all(engine)
    session_factory = build_session_factory(engine)

    try:
        async with session_factory() as test_session:
            yield test_session
    finally:
        await drop_all(engine)
        await engine.dispose()


async def _create_owner(session, email: str = "owner@example.com") -> int:
    user = await create_iam_user(session, email=email)
    assert user.id is not None
    return user.id


@pytest.mark.asyncio
async def test_create_activity_assigns_owner(session) -> None:
    owner_id = await _create_owner(session)

    activity = await create_activity(
        session,
        ActivityCreate(
            activity_type=ActivityType.CALL,
            title="  Follow-up call  ",
            description="Check on proposal status",
        ),
        created_by=owner_id,
    )

    assert activity.id is not None
    assert activity.created_by == owner_id
    assert activity.title == "Follow-up call"
    assert activity.activity_type == ActivityType.CALL
    assert activity.completed_at is None
    assert activity.contact_id is None
    assert activity.lead_id is None


@pytest.mark.asyncio
async def test_list_activities_is_owner_scoped(session) -> None:
    owner_id = await _create_owner(session)
    other_id = await _create_owner(session, "other@example.com")

    await create_activity(
        session,
        ActivityCreate(activity_type=ActivityType.NOTE, title="My note"),
        created_by=owner_id,
    )
    await create_activity(
        session,
        ActivityCreate(activity_type=ActivityType.NOTE, title="Other note"),
        created_by=other_id,
    )

    activities = await list_activities(session, owner_id=owner_id)

    assert len(activities) == 1
    assert activities[0].title == "My note"


@pytest.mark.asyncio
async def test_get_activity_rejects_other_owner(session) -> None:
    owner_id = await _create_owner(session)
    other_id = await _create_owner(session, "other@example.com")

    activity = await create_activity(
        session,
        ActivityCreate(activity_type=ActivityType.EMAIL, title="My email"),
        created_by=owner_id,
    )
    assert activity.id is not None

    with pytest.raises(AuthorizationError):
        await get_activity(session, activity.id, owner_id=other_id)


@pytest.mark.asyncio
async def test_update_activity_changes_fields(session) -> None:
    owner_id = await _create_owner(session)

    activity = await create_activity(
        session,
        ActivityCreate(
            activity_type=ActivityType.MEETING,
            title="Initial meeting",
            description="First intro",
        ),
        created_by=owner_id,
    )
    assert activity.id is not None

    updated = await update_activity(
        session,
        activity.id,
        ActivityUpdate(
            title="Follow-up meeting",
            description="Second meeting to discuss proposal",
            activity_type=ActivityType.CALL,
        ),
        owner_id=owner_id,
    )

    assert updated.title == "Follow-up meeting"
    assert updated.description == "Second meeting to discuss proposal"
    assert updated.activity_type == ActivityType.CALL


@pytest.mark.asyncio
async def test_complete_activity_marks_completed(session) -> None:
    owner_id = await _create_owner(session)

    activity = await create_activity(
        session,
        ActivityCreate(activity_type=ActivityType.NOTE, title="Complete note"),
        created_by=owner_id,
    )
    assert activity.id is not None

    completed = await complete_activity(session, activity.id, owner_id=owner_id)

    assert completed.completed_at is not None

    with pytest.raises(InvalidOperationError):
        await complete_activity(session, activity.id, owner_id=owner_id)


@pytest.mark.asyncio
async def test_cannot_update_completed_activity(session) -> None:
    owner_id = await _create_owner(session)

    activity = await create_activity(
        session,
        ActivityCreate(activity_type=ActivityType.NOTE, title="Done note"),
        created_by=owner_id,
    )
    assert activity.id is not None

    await complete_activity(session, activity.id, owner_id=owner_id)

    with pytest.raises(InvalidOperationError):
        await update_activity(
            session,
            activity.id,
            ActivityUpdate(title="Changed"),
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_delete_activity_removes_it(session) -> None:
    owner_id = await _create_owner(session)

    activity = await create_activity(
        session,
        ActivityCreate(activity_type=ActivityType.EMAIL, title="Temp email"),
        created_by=owner_id,
    )
    assert activity.id is not None

    await delete_activity(session, activity.id, owner_id=owner_id)

    with pytest.raises(Exception):
        await get_activity(session, activity.id, owner_id=owner_id)
