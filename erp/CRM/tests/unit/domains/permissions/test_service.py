from decimal import Decimal
from typing import cast

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
from domains.leads.schemas import LeadCreate
from domains.leads.service import create_lead
from domains.permissions import repository
from domains.permissions.models import CRMUserPermissionEffect, UserRole
from domains.permissions.service import (
    ALL_PERMISSIONS,
    assign_lead,
    assign_proposal,
    assign_role,
    effective_permissions,
    get_lead_assignment,
    get_user_crm_role,
    grant_and_assign_role,
    list_proposal_assignments,
    read_user_permissions,
    require_permission,
    role_permissions,
    set_user_permission_overrides,
    unassign_lead,
    unassign_proposal,
    user_can_access_contact,
    user_can_access_lead,
    user_can_access_proposal,
    user_can_access_technical_visit,
)
from domains.proposals.models import Proposal
from domains.technical_visits.models import (
    TechnicalVisit,
    TechnicalVisitAssignee,
    TechnicalVisitStatus,
)
from domains.users.repository import get_service_access
from domains.users.service import CRM_SERVICE_KEY
from helpers import assign_crm_role, create_iam_user
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


async def _create_user(session, email: str, role: UserRole) -> int:
    user = await create_iam_user(session, email=email)
    assert user.id is not None
    await assign_crm_role(session, user_id=user.id, role=role)
    return user.id


async def _create_lead(session, owner_id: int) -> tuple[int, int]:
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
    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact.id,
            title="Solar 8kW - Acme",
            interest_type="Photovoltaic",
        ),
        owner_id=owner_id,
    )
    assert lead.id is not None
    return contact.id, lead.id


async def _create_proposal(
    session,
    *,
    lead_id: int,
    created_by: int,
) -> Proposal:
    proposal = Proposal(
        lead_id=lead_id,
        name="Acme technical option",
        total_price=Decimal("250000.00"),
        currency="USD",
        created_by=created_by,
    )
    session.add(proposal)
    await session.commit()
    await session.refresh(proposal)
    assert proposal.id is not None
    return proposal


@pytest.mark.asyncio
async def test_role_permissions_matrix(session) -> None:
    admin = role_permissions(UserRole.ADMIN)
    manager = role_permissions(UserRole.MANAGER)
    sales = role_permissions(UserRole.SALES)
    tech = role_permissions(UserRole.TECH)

    assert admin == set(ALL_PERMISSIONS)
    assert manager == set(ALL_PERMISSIONS)
    assert "crm.leads.read" in sales
    assert "crm.contacts.create" in sales
    assert "crm.proposals.read" in sales
    assert "crm.proposals.price.set" not in sales
    assert "crm.proposals.create" not in sales
    assert "crm.technical_visits.complete" in tech
    assert "crm.contacts.create" not in tech
    assert "crm.proposals.price.update" not in tech
    assert role_permissions(cast(UserRole, "custom")) == set()


@pytest.mark.asyncio
async def test_bootstrap_first_access_assigns_admin(session) -> None:
    owner = await create_iam_user(session, email="admin@example.com")
    assert owner.id is not None

    access = await assign_role(
        session,
        actor_id=owner.id,
        target_user_id=owner.id,
        role=UserRole.ADMIN,
    )

    assert access.role == UserRole.ADMIN
    assert access.is_active
    assert await repository.count_user_accesses(session) == 1


@pytest.mark.asyncio
async def test_bootstrap_rejects_non_admin_first_access(session) -> None:
    owner = await create_iam_user(session, email="owner@example.com")
    other = await create_iam_user(session, email="other@example.com")
    assert owner.id is not None
    assert other.id is not None

    with pytest.raises(AuthorizationError):
        await assign_role(
            session,
            actor_id=owner.id,
            target_user_id=owner.id,
            role=UserRole.SALES,
        )
    with pytest.raises(AuthorizationError):
        await assign_role(
            session,
            actor_id=owner.id,
            target_user_id=other.id,
            role=UserRole.ADMIN,
        )


@pytest.mark.asyncio
async def test_assign_role_to_user(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    target = await create_iam_user(session, email="sales@example.com")
    assert target.id is not None

    access = await assign_role(
        session,
        actor_id=admin_id,
        target_user_id=target.id,
        role=UserRole.SALES,
    )

    assert access.role == UserRole.SALES
    assert access.is_active
    assert await get_user_crm_role(session, target.id) == UserRole.SALES


@pytest.mark.asyncio
async def test_assign_role_only_admins_can_assign_admin(session) -> None:
    await _create_user(session, "admin@example.com", UserRole.ADMIN)
    manager_id = await _create_user(session, "manager@example.com", UserRole.MANAGER)
    target = await create_iam_user(session, email="target@example.com")
    assert target.id is not None

    with pytest.raises(AuthorizationError):
        await assign_role(
            session,
            actor_id=manager_id,
            target_user_id=target.id,
            role=UserRole.ADMIN,
        )

    access = await assign_role(
        session,
        actor_id=manager_id,
        target_user_id=target.id,
        role=UserRole.SALES,
    )
    assert access.role == UserRole.SALES
    assert access.user_id == target.id
    assert access.changed_by == manager_id


@pytest.mark.asyncio
async def test_cannot_modify_own_permissions(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)

    with pytest.raises(AuthorizationError):
        await set_user_permission_overrides(
            session,
            actor_id=admin_id,
            target_user_id=admin_id,
            grant={"crm.leads.read"},
            deny=set(),
            clear=set(),
        )


@pytest.mark.asyncio
async def test_grant_and_assign_role_grants_iam_service_access(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    target_id = await _create_user(session, "tech@example.com", UserRole.ADMIN)

    access = await grant_and_assign_role(
        session,
        actor_id=admin_id,
        target_user_id=target_id,
        role=UserRole.TECH,
    )

    assert access.role == UserRole.TECH
    service_access = await get_service_access(
        session,
        user_id=target_id,
        service_key=CRM_SERVICE_KEY,
    )
    assert service_access is not None
    assert service_access.is_active


@pytest.mark.asyncio
async def test_effective_permissions_apply_overrides(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    sales_id = await _create_user(session, "sales@example.com", UserRole.SALES)

    initial = await effective_permissions(session, sales_id)
    assert "crm.leads.read" in initial
    assert "crm.proposals.create" not in initial

    await set_user_permission_overrides(
        session,
        actor_id=admin_id,
        target_user_id=sales_id,
        grant={"crm.proposals.create"},
        deny={"crm.leads.read"},
        clear=set(),
    )

    updated = await effective_permissions(session, sales_id)
    assert "crm.proposals.create" in updated
    assert "crm.leads.read" not in updated
    overrides = await repository.list_user_overrides(session, sales_id)
    assert {o.effect for o in overrides} == {
        CRMUserPermissionEffect.GRANT,
        CRMUserPermissionEffect.DENY,
    }


@pytest.mark.asyncio
async def test_set_user_permission_overrides_validates_inputs(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    target_id = await _create_user(session, "target@example.com", UserRole.ADMIN)

    with pytest.raises(InvalidOperationError):
        await set_user_permission_overrides(
            session,
            actor_id=admin_id,
            target_user_id=target_id,
            grant={"crm.bogus.perm"},
            deny=set(),
            clear=set(),
        )
    with pytest.raises(InvalidOperationError):
        await set_user_permission_overrides(
            session,
            actor_id=admin_id,
            target_user_id=target_id,
            grant={"crm.leads.read"},
            deny={"crm.leads.read"},
            clear=set(),
        )


@pytest.mark.asyncio
async def test_set_user_permission_overrides_requires_manage_permission(session) -> None:
    sales_id = await _create_user(session, "sales@example.com", UserRole.SALES)
    target_id = await _create_user(session, "target@example.com", UserRole.ADMIN)

    with pytest.raises(AuthorizationError):
        await set_user_permission_overrides(
            session,
            actor_id=sales_id,
            target_user_id=target_id,
            grant={"crm.leads.read"},
            deny=set(),
            clear=set(),
        )


@pytest.mark.asyncio
async def test_cannot_grant_permissions_actor_does_not_have(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    sales_id = await _create_user(session, "sales@example.com", UserRole.SALES)
    target_id = await _create_user(session, "target@example.com", UserRole.ADMIN)

    await set_user_permission_overrides(
        session,
        actor_id=admin_id,
        target_user_id=sales_id,
        grant={"crm.permissions.manage"},
        deny=set(),
        clear=set(),
    )

    with pytest.raises(AuthorizationError):
        await set_user_permission_overrides(
            session,
            actor_id=sales_id,
            target_user_id=target_id,
            grant={"crm.proposals.price.set"},
            deny=set(),
            clear=set(),
        )


@pytest.mark.asyncio
async def test_manager_cannot_modify_admin_user(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    manager_id = await _create_user(session, "manager@example.com", UserRole.MANAGER)

    with pytest.raises(AuthorizationError):
        await set_user_permission_overrides(
            session,
            actor_id=manager_id,
            target_user_id=admin_id,
            grant={"crm.leads.read"},
            deny=set(),
            clear=set(),
        )


@pytest.mark.asyncio
async def test_require_permission_enforces_and_returns_unknown(session) -> None:
    sales_id = await _create_user(session, "sales@example.com", UserRole.SALES)

    await require_permission(session, sales_id, "crm.leads.read")

    with pytest.raises(AuthorizationError):
        await require_permission(session, sales_id, "crm.proposals.create")
    with pytest.raises(InvalidOperationError):
        await require_permission(session, sales_id, "crm.bogus.read")


@pytest.mark.asyncio
async def test_user_without_crm_role_has_no_permissions(session) -> None:
    plain_id = await _create_user(session, "plain@example.com", UserRole.ADMIN)
    await repository.get_user_access(session, plain_id)
    access = await repository.get_user_access(session, plain_id)
    assert access is not None
    assert await get_user_crm_role(session, plain_id) == UserRole.ADMIN


@pytest.mark.asyncio
async def test_inactive_access_has_no_role(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)

    access = await repository.get_user_access(session, admin_id)
    assert access is not None
    access.is_active = False
    await session.commit()

    assert await get_user_crm_role(session, admin_id) is None
    assert await effective_permissions(session, admin_id) == set()


@pytest.mark.asyncio
async def test_assign_lead_transfers_ownership_and_history(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    sales_a_id = await _create_user(session, "sales-a@example.com", UserRole.SALES)
    sales_b_id = await _create_user(session, "sales-b@example.com", UserRole.SALES)
    _, lead_id = await _create_lead(session, sales_a_id)

    assignment = await assign_lead(
        session,
        actor_id=admin_id,
        lead_id=lead_id,
        user_id=sales_b_id,
    )
    assert assignment.user_id == sales_b_id
    assert assignment.is_active
    assert await get_lead_assignment(session, actor_id=admin_id, lead_id=lead_id) == assignment

    duplicate = await assign_lead(
        session,
        actor_id=admin_id,
        lead_id=lead_id,
        user_id=sales_b_id,
    )
    assert duplicate.id == assignment.id
    assert duplicate.is_active


@pytest.mark.asyncio
async def test_assign_lead_only_to_sales_users(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    tech_id = await _create_user(session, "tech@example.com", UserRole.TECH)
    _, lead_id = await _create_lead(session, admin_id)

    with pytest.raises(InvalidOperationError):
        await assign_lead(
            session,
            actor_id=admin_id,
            lead_id=lead_id,
            user_id=tech_id,
        )


@pytest.mark.asyncio
async def test_sales_cannot_assign_foreign_lead(session) -> None:
    sales_a_id = await _create_user(session, "sales-a@example.com", UserRole.SALES)
    sales_b_id = await _create_user(session, "sales-b@example.com", UserRole.SALES)
    sales_c_id = await _create_user(session, "sales-c@example.com", UserRole.SALES)
    _, lead_id = await _create_lead(session, sales_a_id)

    with pytest.raises(AuthorizationError):
        await assign_lead(
            session,
            actor_id=sales_b_id,
            lead_id=lead_id,
            user_id=sales_c_id,
        )


@pytest.mark.asyncio
async def test_unassign_lead_requires_active_assignment(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    sales_id = await _create_user(session, "sales@example.com", UserRole.SALES)
    _, lead_id = await _create_lead(session, admin_id)

    with pytest.raises(NotFoundError):
        await unassign_lead(session, actor_id=admin_id, lead_id=lead_id)

    await assign_lead(session, actor_id=admin_id, lead_id=lead_id, user_id=sales_id)
    await unassign_lead(session, actor_id=admin_id, lead_id=lead_id)

    assert await get_lead_assignment(session, actor_id=admin_id, lead_id=lead_id) is None


@pytest.mark.asyncio
async def test_assign_proposal_to_tech_and_scope(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    sales_id = await _create_user(session, "sales@example.com", UserRole.SALES)
    tech_id = await _create_user(session, "tech@example.com", UserRole.TECH)
    other_sales_id = await _create_user(session, "other@example.com", UserRole.SALES)
    _, lead_id = await _create_lead(session, sales_id)
    proposal = await _create_proposal(session, lead_id=lead_id, created_by=admin_id)

    assignment = await assign_proposal(
        session,
        actor_id=admin_id,
        proposal_id=proposal.id or 0,
        user_id=tech_id,
    )
    assert assignment.user_id == tech_id
    assert assignment.is_active
    assert await list_proposal_assignments(
        session,
        actor_id=admin_id,
        proposal_id=proposal.id or 0,
    ) == [assignment]

    assert await user_can_access_proposal(session, user_id=admin_id, proposal_id=proposal.id or 0)
    assert await user_can_access_proposal(session, user_id=sales_id, proposal_id=proposal.id or 0)
    assert await user_can_access_proposal(session, user_id=tech_id, proposal_id=proposal.id or 0)
    assert not await user_can_access_proposal(
        session, user_id=other_sales_id, proposal_id=proposal.id or 0
    )

    await unassign_proposal(
        session,
        actor_id=admin_id,
        proposal_id=proposal.id or 0,
        user_id=tech_id,
    )
    assert (
        await list_proposal_assignments(
            session,
            actor_id=admin_id,
            proposal_id=proposal.id or 0,
        )
        == []
    )
    with pytest.raises(NotFoundError):
        await unassign_proposal(
            session,
            actor_id=admin_id,
            proposal_id=proposal.id or 0,
            user_id=tech_id,
        )


@pytest.mark.asyncio
async def test_assign_proposal_only_to_tech_users(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    sales_id = await _create_user(session, "sales@example.com", UserRole.SALES)
    _, lead_id = await _create_lead(session, sales_id)
    proposal = await _create_proposal(session, lead_id=lead_id, created_by=admin_id)

    with pytest.raises(InvalidOperationError):
        await assign_proposal(
            session,
            actor_id=admin_id,
            proposal_id=proposal.id or 0,
            user_id=sales_id,
        )


@pytest.mark.asyncio
async def test_user_can_access_lead_contact_and_visit_scopes(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    sales_id = await _create_user(session, "sales@example.com", UserRole.SALES)
    tech_id = await _create_user(session, "tech@example.com", UserRole.TECH)
    other_id = await _create_user(session, "other@example.com", UserRole.SALES)
    contact_id, lead_id = await _create_lead(session, sales_id)
    proposal = await _create_proposal(session, lead_id=lead_id, created_by=admin_id)
    await assign_proposal(
        session,
        actor_id=admin_id,
        proposal_id=proposal.id or 0,
        user_id=tech_id,
    )

    assert await user_can_access_lead(session, user_id=admin_id, lead_id=lead_id)
    assert await user_can_access_lead(session, user_id=sales_id, lead_id=lead_id)
    assert await user_can_access_lead(session, user_id=tech_id, lead_id=lead_id)
    assert not await user_can_access_lead(session, user_id=other_id, lead_id=lead_id)

    assert await user_can_access_contact(session, user_id=admin_id, contact_id=contact_id)
    assert await user_can_access_contact(session, user_id=sales_id, contact_id=contact_id)
    assert await user_can_access_contact(session, user_id=tech_id, contact_id=contact_id)
    assert not await user_can_access_contact(session, user_id=other_id, contact_id=contact_id)

    visit = TechnicalVisit(
        lead_id=lead_id,
        status=TechnicalVisitStatus.SCHEDULED,
        created_by=sales_id,
    )
    session.add(visit)
    await session.commit()
    await session.refresh(visit)
    assert visit.id is not None
    session.add(TechnicalVisitAssignee(visit_id=visit.id, user_id=tech_id, name="Tech Engineer"))
    await session.commit()

    assert await user_can_access_technical_visit(session, user_id=admin_id, visit_id=visit.id)
    assert await user_can_access_technical_visit(session, user_id=tech_id, visit_id=visit.id)
    assert not await user_can_access_technical_visit(session, user_id=other_id, visit_id=visit.id)


@pytest.mark.asyncio
async def test_read_user_permissions_reports_grants_denials_effective(session) -> None:
    admin_id = await _create_user(session, "admin@example.com", UserRole.ADMIN)
    sales_id = await _create_user(session, "sales@example.com", UserRole.SALES)

    await set_user_permission_overrides(
        session,
        actor_id=admin_id,
        target_user_id=sales_id,
        grant={"crm.proposals.create"},
        deny={"crm.leads.delete"},
        clear=set(),
    )

    user, access, grants, denials, effective = await read_user_permissions(
        session,
        sales_id,
    )

    assert user.id == sales_id
    assert access is not None and access.role == UserRole.SALES
    assert grants == {"crm.proposals.create"}
    assert denials == {"crm.leads.delete"}
    assert "crm.proposals.create" in effective
    assert "crm.leads.delete" not in effective
