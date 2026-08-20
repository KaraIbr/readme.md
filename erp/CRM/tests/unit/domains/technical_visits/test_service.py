from datetime import datetime
from pathlib import Path

import pytest
from core.config import Settings
from core.database import (
    build_async_engine,
    build_session_factory,
    create_all,
    drop_all,
)
from core.exceptions import ConflictError, InvalidOperationError
from domains.contacts.models import ContactType
from domains.contacts.schemas import (
    CompanyContactPersonCreate,
    ContactCreate,
    PromoterCreate,
)
from domains.contacts.service import create_contact, create_promoter
from domains.leads.models import LeadInterestType, TechnicalVisitRequirement
from domains.leads.schemas import LeadCreate
from domains.leads.service import create_lead, get_lead
from domains.proposals.schemas import ProposalCreate
from domains.proposals.service import create_proposal
from domains.technical_visits.models import (
    ProposalTechnicalVisitRelationshipType,
    TechnicalVisitAttachmentKind,
    TechnicalVisitStatus,
)
from domains.technical_visits.schemas import (
    ProposalTechnicalVisitCreate,
    TechnicalVisitAssigneePayload,
    TechnicalVisitCancel,
    TechnicalVisitCreate,
)
from domains.technical_visits.service import (
    cancel_visit,
    complete_visit,
    create_visit,
    link_proposal_visit,
    list_attachments,
    list_proposal_visit_links,
    set_lead_requirement,
    unlink_proposal_visit,
    upload_attachment,
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


async def _create_lead(session, owner_id: int, title: str = "Solar 8kW - Acme") -> int:
    contact_id = await _create_contact(session, owner_id)
    lead = await create_lead(
        session,
        LeadCreate(
            contact_id=contact_id,
            title=title,
            interest_type=LeadInterestType.PHOTOVOLTAIC,
        ),
        owner_id=owner_id,
    )
    assert lead.id is not None
    return lead.id


class FakeUpload:
    def __init__(
        self,
        filename: str,
        content: bytes,
        content_type: str = "application/pdf",
    ) -> None:
        self.filename: str | None = filename
        self.content_type: str | None = content_type
        self._content = content
        self._offset = 0

    async def read(self, size: int = -1) -> bytes:
        if self._offset >= len(self._content):
            return b""
        if size < 0:
            size = len(self._content) - self._offset
        chunk = self._content[self._offset : self._offset + size]
        self._offset += len(chunk)
        return chunk


def _scheduled_visit_payload() -> TechnicalVisitCreate:
    return TechnicalVisitCreate(
        scheduled_at=datetime(2026, 6, 20, 16, 30),
        receiver_name="Jane Manager",
        receiver_phone="+52 81 5555 0101",
        notes="Access through loading dock.",
        assignees=[
            TechnicalVisitAssigneePayload(name="Engineer One"),
            TechnicalVisitAssigneePayload(name="Engineer Two"),
        ],
    )


@pytest.mark.asyncio
async def test_requirement_visit_completion_and_attachment_flow(session, tmp_path) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)

    lead = await set_lead_requirement(
        session,
        lead_id,
        requirement=TechnicalVisitRequirement.REQUIRED,
        owner_id=owner_id,
    )
    visit = await create_visit(
        session,
        lead_id,
        _scheduled_visit_payload(),
        owner_id=owner_id,
    )
    scheduled_status = visit.status
    assignee_names = [assignee.name for assignee in visit.assignees]
    attachment = await upload_attachment(
        session,
        visit.id or 0,
        title="Inspection report",
        file_kind=TechnicalVisitAttachmentKind.DOCUMENT,
        upload=FakeUpload("inspection.pdf", b"visit evidence"),
        owner_id=owner_id,
        storage_root=tmp_path,
    )
    completed = await complete_visit(session, visit.id or 0, owner_id=owner_id)
    attachments = await list_attachments(
        session,
        visit.id or 0,
        owner_id=owner_id,
    )

    assert lead.technical_visit_requirement == TechnicalVisitRequirement.REQUIRED
    assert scheduled_status == TechnicalVisitStatus.SCHEDULED
    assert assignee_names == [
        "Engineer One",
        "Engineer Two",
    ]
    assert completed.status == TechnicalVisitStatus.COMPLETED
    assert completed.completed_at is not None
    assert attachment.title == "Inspection report"
    assert Path(attachment.stored_path).is_file()
    assert [item.id for item in attachments] == [attachment.id]


@pytest.mark.asyncio
async def test_complete_visit_requires_attachment(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    visit = await create_visit(
        session,
        lead_id,
        _scheduled_visit_payload(),
        owner_id=owner_id,
    )

    with pytest.raises(InvalidOperationError):
        await complete_visit(session, visit.id or 0, owner_id=owner_id)


@pytest.mark.asyncio
async def test_create_visit_sets_undetermined_lead_to_required(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)

    original = await get_lead(session, lead_id, owner_id=owner_id)
    original_requirement = original.technical_visit_requirement
    visit = await create_visit(
        session,
        lead_id,
        _scheduled_visit_payload(),
        owner_id=owner_id,
    )
    updated = await get_lead(session, lead_id, owner_id=owner_id)

    assert original_requirement == TechnicalVisitRequirement.UNDETERMINED
    assert visit.status == TechnicalVisitStatus.SCHEDULED
    assert updated.technical_visit_requirement == TechnicalVisitRequirement.REQUIRED


@pytest.mark.asyncio
async def test_not_required_lead_rejects_visits(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    await set_lead_requirement(
        session,
        lead_id,
        requirement=TechnicalVisitRequirement.NOT_REQUIRED,
        owner_id=owner_id,
    )

    with pytest.raises(InvalidOperationError):
        await create_visit(
            session,
            lead_id,
            _scheduled_visit_payload(),
            owner_id=owner_id,
        )


@pytest.mark.asyncio
async def test_cancelled_visit_rejects_attachment_upload(session, tmp_path) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    visit = await create_visit(
        session,
        lead_id,
        _scheduled_visit_payload(),
        owner_id=owner_id,
    )
    await cancel_visit(
        session,
        visit.id or 0,
        TechnicalVisitCancel(reason="Customer unavailable"),
        owner_id=owner_id,
    )

    with pytest.raises(InvalidOperationError):
        await upload_attachment(
            session,
            visit.id or 0,
            title="Inspection report",
            file_kind=TechnicalVisitAttachmentKind.DOCUMENT,
            upload=FakeUpload("inspection.pdf", b"visit evidence"),
            owner_id=owner_id,
            storage_root=tmp_path,
        )


@pytest.mark.asyncio
async def test_proposal_technical_visit_links_stay_within_same_lead(session) -> None:
    owner_id = await _create_owner(session)
    lead_id = await _create_lead(session, owner_id)
    other_lead_id = await _create_lead(session, owner_id, title="Solar 5kW - Other")
    visit = await create_visit(
        session,
        lead_id,
        _scheduled_visit_payload(),
        owner_id=owner_id,
    )
    proposal = await create_proposal(
        session,
        ProposalCreate(lead_id=lead_id, name="Acme PV v1"),
        created_by=owner_id,
    )
    other_proposal = await create_proposal(
        session,
        ProposalCreate(lead_id=other_lead_id, name="Other PV v1"),
        created_by=owner_id,
    )

    link = await link_proposal_visit(
        session,
        proposal.id or 0,
        ProposalTechnicalVisitCreate(
            technical_visit_id=visit.id or 0,
            relationship_type=ProposalTechnicalVisitRelationshipType.BASED_ON,
            notes="Version based on field measurements.",
        ),
        owner_id=owner_id,
    )
    links = await list_proposal_visit_links(
        session,
        proposal.id or 0,
        owner_id=owner_id,
    )

    assert link.proposal_id == proposal.id
    assert link.technical_visit_id == visit.id
    assert [item.id for item in links] == [link.id]

    with pytest.raises(ConflictError):
        await link_proposal_visit(
            session,
            proposal.id or 0,
            ProposalTechnicalVisitCreate(
                technical_visit_id=visit.id or 0,
                relationship_type=ProposalTechnicalVisitRelationshipType.VALIDATED_BY,
            ),
            owner_id=owner_id,
        )

    with pytest.raises(InvalidOperationError):
        await link_proposal_visit(
            session,
            other_proposal.id or 0,
            ProposalTechnicalVisitCreate(
                technical_visit_id=visit.id or 0,
                relationship_type=ProposalTechnicalVisitRelationshipType.BASED_ON,
            ),
            owner_id=owner_id,
        )

    await unlink_proposal_visit(
        session,
        proposal.id or 0,
        visit.id or 0,
        owner_id=owner_id,
    )
    assert (
        await list_proposal_visit_links(
            session,
            proposal.id or 0,
            owner_id=owner_id,
        )
        == []
    )
