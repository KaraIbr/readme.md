from datetime import datetime, timedelta

import pytest
from core.config import Settings
from core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from domains.contacts.models import ContactType
from domains.contacts.schemas import (
    CompanyContactPersonCreate,
    ContactCreate,
    PromoterCreate,
)
from domains.contacts.service import create_contact, create_promoter
from domains.leads.models import LeadInterestType
from domains.leads.schemas import LeadCreate
from domains.leads.service import create_lead
from domains.opportunities.schemas import OpportunityCreate
from domains.opportunities.service import create_opportunity
from domains.tasks.models import TaskPriority, TaskStatus
from domains.tasks.schemas import TaskCreate, TaskUpdate
from domains.tasks.service import (
    create_task,
    delete_task,
    get_task,
    list_tasks,
    update_task,
    update_task_status,
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


async def _create_contact(session, owner_id: int) -> int:
    promoter = await create_promoter(
        session,
        PromoterCreate(name="Referral Partner", phone="+52 81 5555 0000"),
        owner_id=owner_id,
    )
    assert promoter.id is not None
    contact = await create_contact(
        session,
        ContactCreate(
            type=ContactType.COMPANY,
            name="Acme Solar",
            promoter_id=promoter.id,
            industry="Manufacturing",
            company_people=[
                CompanyContactPersonCreate(
                    name="Jane Manager",
                    phone="+52 81 5555 0101",
                    position="Facility Manager",
                )
            ],
        ),
        owner_id=owner_id,
    )
    assert contact.id is not None
    return contact.id


async def _create_lead(session, owner_id: int, contact_id: int) -> int:
    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact_id,
            title="Solar 8kW - Acme",
            interest_type=LeadInterestType.PHOTOVOLTAIC,
        ),
        owner_id=owner_id,
    )
    assert lead.id is not None
    return lead.id


async def _create_opportunity(session, owner_id: int, contact_id: int) -> int:
    opportunity = await create_opportunity(
        session,
        OpportunityCreate(name="Acme expansion", contact_id=contact_id),
        owner_id=owner_id,
    )
    assert opportunity.id is not None
    return opportunity.id


@pytest.mark.asyncio
async def test_create_task_assigns_creator_and_defaults(session) -> None:
    owner_id = await _create_owner(session)

    task = await create_task(
        session,
        TaskCreate(title="  Call Acme  ", description="  Discuss quotes  "),
        created_by=owner_id,
    )

    assert task.id is not None
    assert task.created_by == owner_id
    assert task.title == "Call Acme"
    assert task.description == "Discuss quotes"
    assert task.status == TaskStatus.TODO
    assert task.priority == TaskPriority.MEDIUM
    assert task.completed_at is None
    assert task.contact_id is None
    assert task.lead_id is None
    assert task.opportunity_id is None
    assert task.assigned_to is None


@pytest.mark.asyncio
async def test_create_task_validates_linked_entities_ownership(session) -> None:
    owner_id = await _create_owner(session)
    other_owner_id = await _create_owner(session, "other@example.com")
    other_contact_id = await _create_contact(session, other_owner_id)

    with pytest.raises(AuthorizationError):
        await create_task(
            session,
            TaskCreate(title="Wrong contact", contact_id=other_contact_id),
            created_by=owner_id,
        )

    with pytest.raises(NotFoundError):
        await create_task(
            session,
            TaskCreate(title="Missing contact", contact_id=9999),
            created_by=owner_id,
        )

    with pytest.raises(NotFoundError):
        await create_task(
            session,
            TaskCreate(title="Missing lead", lead_id=9999),
            created_by=owner_id,
        )

    with pytest.raises(NotFoundError):
        await create_task(
            session,
            TaskCreate(title="Missing opportunity", opportunity_id=9999),
            created_by=owner_id,
        )


@pytest.mark.asyncio
async def test_create_task_accepts_owned_linked_entities_and_validates_user(session) -> None:
    owner_id = await _create_owner(session)
    assignee_id = await _create_owner(session, "assignee@example.com")
    contact_id = await _create_contact(session, owner_id)
    lead_id = await _create_lead(session, owner_id, contact_id)
    opportunity_id = await _create_opportunity(session, owner_id, contact_id)

    task = await create_task(
        session,
        TaskCreate(
            title="Follow up",
            contact_id=contact_id,
            lead_id=lead_id,
            opportunity_id=opportunity_id,
            assigned_to=assignee_id,
        ),
        created_by=owner_id,
    )

    assert task.contact_id == contact_id
    assert task.lead_id == lead_id
    assert task.opportunity_id == opportunity_id
    assert task.assigned_to == assignee_id

    with pytest.raises(NotFoundError):
        await create_task(
            session,
            TaskCreate(title="Bad assignee", assigned_to=9999),
            created_by=owner_id,
        )


@pytest.mark.asyncio
async def test_get_and_list_tasks_are_owner_scoped(session) -> None:
    owner_id = await _create_owner(session)
    other_owner_id = await _create_owner(session, "other@example.com")
    task = await create_task(
        session,
        TaskCreate(title="Owner task"),
        created_by=owner_id,
    )
    await create_task(
        session,
        TaskCreate(title="Other task"),
        created_by=other_owner_id,
    )

    tasks = await list_tasks(session, owner_id=owner_id)

    assert [item.id for item in tasks] == [task.id]
    assert await get_task(session, task.id or 0, owner_id=owner_id) == task
    with pytest.raises(AuthorizationError):
        await get_task(session, task.id or 0, owner_id=other_owner_id)
    with pytest.raises(NotFoundError):
        await get_task(session, 9999, owner_id=owner_id)


@pytest.mark.asyncio
async def test_list_tasks_filters_status_priority_and_paginates(session) -> None:
    owner_id = await _create_owner(session)
    await create_task(
        session,
        TaskCreate(title="Low todo", priority=TaskPriority.LOW),
        created_by=owner_id,
    )
    done = await create_task(
        session,
        TaskCreate(title="Urgent done", priority=TaskPriority.URGENT),
        created_by=owner_id,
    )
    await update_task_status(
        session,
        done.id or 0,
        owner_id=owner_id,
        status=TaskStatus.DONE,
    )
    in_progress = await create_task(
        session,
        TaskCreate(title="High in progress", priority=TaskPriority.HIGH),
        created_by=owner_id,
    )
    await update_task_status(
        session,
        in_progress.id or 0,
        owner_id=owner_id,
        status=TaskStatus.IN_PROGRESS,
    )

    todo_tasks = await list_tasks(session, owner_id=owner_id, status=TaskStatus.TODO)
    urgent_tasks = await list_tasks(
        session,
        owner_id=owner_id,
        status=TaskStatus.DONE,
        priority=TaskPriority.URGENT,
    )
    single = await list_tasks(session, owner_id=owner_id, limit=1)

    assert len(todo_tasks) == 1
    assert todo_tasks[0].title == "Low todo"
    assert [item.id for item in urgent_tasks] == [done.id]
    assert len(single) == 1


@pytest.mark.asyncio
async def test_update_task_updates_fields_and_validates_assignee(session) -> None:
    owner_id = await _create_owner(session)
    assignee_id = await _create_owner(session, "assignee@example.com")
    task = await create_task(
        session,
        TaskCreate(title="Original"),
        created_by=owner_id,
    )
    due_date = datetime.now() + timedelta(days=2)

    updated = await update_task(
        session,
        task.id or 0,
        TaskUpdate(
            title="  Renamed  ",
            description="More context",
            priority=TaskPriority.HIGH,
            due_date=due_date,
            assigned_to=assignee_id,
        ),
        owner_id=owner_id,
    )

    assert updated.title == "Renamed"
    assert updated.description == "More context"
    assert updated.priority == TaskPriority.HIGH
    assert updated.due_date == due_date
    assert updated.assigned_to == assignee_id
    assert updated.updated_at >= task.updated_at

    with pytest.raises(NotFoundError):
        await update_task(
            session,
            task.id or 0,
            TaskUpdate(assigned_to=9999),
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_update_task_rejects_completed_task(session) -> None:
    owner_id = await _create_owner(session)
    task = await create_task(
        session,
        TaskCreate(title="Done task"),
        created_by=owner_id,
    )
    await update_task_status(
        session,
        task.id or 0,
        owner_id=owner_id,
        status=TaskStatus.DONE,
    )

    with pytest.raises(InvalidOperationError):
        await update_task(
            session,
            task.id or 0,
            TaskUpdate(title="No edits"),
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_status_transition_to_done_sets_completed_at(session) -> None:
    owner_id = await _create_owner(session)
    task = await create_task(
        session,
        TaskCreate(title="Work item"),
        created_by=owner_id,
    )

    done = await update_task_status(
        session,
        task.id or 0,
        owner_id=owner_id,
        status=TaskStatus.DONE,
    )
    assert done.status == TaskStatus.DONE
    assert done.completed_at is not None


@pytest.mark.asyncio
async def test_completed_task_is_frozen(session) -> None:
    owner_id = await _create_owner(session)
    task = await create_task(
        session,
        TaskCreate(title="Frozen task"),
        created_by=owner_id,
    )
    await update_task_status(
        session,
        task.id or 0,
        owner_id=owner_id,
        status=TaskStatus.DONE,
    )

    with pytest.raises(InvalidOperationError):
        await update_task_status(
            session,
            task.id or 0,
            owner_id=owner_id,
            status=TaskStatus.IN_PROGRESS,
        )

    with pytest.raises(InvalidOperationError):
        await update_task_status(
            session,
            task.id or 0,
            owner_id=owner_id,
            status=TaskStatus.CANCELLED,
        )


@pytest.mark.asyncio
async def test_delete_task_removes_it(session) -> None:
    owner_id = await _create_owner(session)
    task = await create_task(
        session,
        TaskCreate(title="To delete"),
        created_by=owner_id,
    )

    await delete_task(session, task.id or 0, owner_id=owner_id)

    with pytest.raises(NotFoundError):
        await get_task(session, task.id or 0, owner_id=owner_id)
