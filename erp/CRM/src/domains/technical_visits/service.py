"""Technical visits business logic."""

from datetime import UTC, datetime
from pathlib import Path

from core.exceptions import (
    AuthorizationError,
    ConflictError,
    InvalidOperationError,
    NotFoundError,
)
from core.storage import (
    UploadFileLike,
    delete_stored_file,
    save_upload,
)
from core.storage import (
    stored_file_path as resolve_stored_file_path,
)
from domains.leads import service as leads_service
from domains.leads.models import Lead, LeadStage, TechnicalVisitRequirement
from domains.permissions import service as permissions_service
from domains.permissions.models import UserRole
from domains.proposals import service as proposals_service
from domains.technical_visits import repository
from domains.technical_visits.models import (
    ProposalTechnicalVisit,
    TechnicalVisit,
    TechnicalVisitAssignee,
    TechnicalVisitAttachment,
    TechnicalVisitAttachmentKind,
    TechnicalVisitStatus,
)
from domains.technical_visits.schemas import (
    ProposalTechnicalVisitCreate,
    TechnicalVisitAssigneePayload,
    TechnicalVisitCancel,
    TechnicalVisitCreate,
    TechnicalVisitUpdate,
)
from domains.users import service as users_service
from sqlmodel.ext.asyncio.session import AsyncSession

SCHEDULE_FIELDS = {"scheduled_at", "receiver_name", "receiver_phone"}


def _normalize_required_text(value: str, *, field_name: str = "value") -> str:
    normalized = value.strip()
    if not normalized:
        raise InvalidOperationError(f"{field_name} cannot be blank")
    return normalized


def stored_file_path(stored_path: str) -> Path:
    """Return an uploaded file path or raise if the blob is missing."""

    return resolve_stored_file_path(stored_path)


def _is_closed(lead: Lead) -> bool:
    return lead.current_stage in {LeadStage.CLOSED_WON, LeadStage.CLOSED_LOST}


def _ensure_visit_editable(visit: TechnicalVisit) -> None:
    if visit.status == TechnicalVisitStatus.COMPLETED:
        raise InvalidOperationError("Completed technical visits cannot be modified")
    if visit.status == TechnicalVisitStatus.CANCELLED:
        raise InvalidOperationError("Cancelled technical visits cannot be modified")


def _schedule_parts(
    visit: TechnicalVisit,
    assignees: list[TechnicalVisitAssignee] | list[TechnicalVisitAssigneePayload],
) -> tuple[bool, bool, bool, bool]:
    return (
        visit.scheduled_at is not None,
        bool(visit.receiver_name),
        bool(visit.receiver_phone),
        bool(assignees),
    )


def _is_schedule_complete(
    visit: TechnicalVisit,
    assignees: list[TechnicalVisitAssignee] | list[TechnicalVisitAssigneePayload],
) -> bool:
    return all(_schedule_parts(visit, assignees))


def _validate_schedule_shape(
    visit: TechnicalVisit,
    assignees: list[TechnicalVisitAssignee] | list[TechnicalVisitAssigneePayload],
) -> None:
    parts = _schedule_parts(visit, assignees)
    if any(parts) and not all(parts):
        raise InvalidOperationError(
            "scheduled_at, receiver_name, receiver_phone, and at least one assignee "
            "are required to schedule a technical visit"
        )


async def _validate_assignee_users(
    session: AsyncSession,
    assignees: list[TechnicalVisitAssigneePayload],
) -> None:
    for assignee in assignees:
        if assignee.user_id is not None:
            await users_service.get_active_user(session, assignee.user_id)


async def _replace_assignees(
    session: AsyncSession,
    *,
    visit_id: int,
    assignees: list[TechnicalVisitAssigneePayload],
) -> list[TechnicalVisitAssignee]:
    await _validate_assignee_users(session, assignees)
    existing = await repository.list_assignees(session, visit_id)
    for assignee in existing:
        await repository.delete_assignee(session, assignee)

    created: list[TechnicalVisitAssignee] = []
    for assignee_payload in assignees:
        created.append(
            await repository.create_assignee(
                session,
                TechnicalVisitAssignee(
                    visit_id=visit_id,
                    name=assignee_payload.name,
                    user_id=assignee_payload.user_id,
                ),
            )
        )
    return created


def _apply_visit_updates(
    visit: TechnicalVisit,
    updates: dict[str, object],
) -> None:
    for field, value in updates.items():
        if field in SCHEDULE_FIELDS and value is None:
            raise InvalidOperationError(f"{field} cannot be cleared")
        setattr(visit, field, value)


async def _assignees_for_visit_update(
    session: AsyncSession,
    visit: TechnicalVisit,
    visit_update: TechnicalVisitUpdate,
) -> list[TechnicalVisitAssignee]:
    if visit.id is None:
        raise InvalidOperationError("Visit was not saved properly")
    if "assignees" in visit_update.model_fields_set:
        return await _replace_assignees(
            session,
            visit_id=visit.id,
            assignees=visit_update.assignees or [],
        )
    return list(await repository.list_assignees(session, visit.id))


def _visit_status_for_schedule(
    visit: TechnicalVisit,
    assignees: list[TechnicalVisitAssignee],
) -> TechnicalVisitStatus:
    if _is_schedule_complete(visit, assignees):
        return TechnicalVisitStatus.SCHEDULED
    return TechnicalVisitStatus.REQUESTED


async def set_lead_requirement(
    session: AsyncSession,
    lead_id: int,
    *,
    requirement: TechnicalVisitRequirement,
    owner_id: int,
) -> Lead:
    """Record whether an owned lead requires a technical visit."""

    lead = await leads_service.get_lead(session, lead_id, owner_id=owner_id)
    if _is_closed(lead):
        raise InvalidOperationError("Closed leads cannot be modified")

    if requirement != TechnicalVisitRequirement.REQUIRED:
        if lead.id is None:
            raise InvalidOperationError("Lead was not saved properly")
        existing_visits = await repository.list_visits_for_lead(session, lead.id)
        active_or_completed = [
            visit for visit in existing_visits if visit.status != TechnicalVisitStatus.CANCELLED
        ]
        if active_or_completed:
            raise InvalidOperationError(
                "Cannot clear the technical visit requirement while visits exist"
            )

    lead.technical_visit_requirement = requirement
    session.add(lead)
    await session.flush()
    await session.refresh(lead)
    await session.commit()
    return lead


async def create_visit(
    session: AsyncSession,
    lead_id: int,
    visit_create: TechnicalVisitCreate,
    *,
    owner_id: int,
) -> TechnicalVisit:
    """Create a technical visit for an owned open lead."""

    try:
        lead = await leads_service.get_lead(session, lead_id, owner_id=owner_id)
        if _is_closed(lead):
            raise InvalidOperationError("Cannot create visits for closed leads")
        if lead.technical_visit_requirement == TechnicalVisitRequirement.NOT_REQUIRED:
            raise InvalidOperationError("Lead is marked as not requiring a visit")

        if lead.id is None:
            raise InvalidOperationError("Lead was not saved properly")
        status = (
            TechnicalVisitStatus.SCHEDULED
            if visit_create.assignees
            else TechnicalVisitStatus.REQUESTED
        )
        visit = TechnicalVisit(
            lead_id=lead.id,
            status=status,
            scheduled_at=visit_create.scheduled_at,
            receiver_name=visit_create.receiver_name,
            receiver_phone=visit_create.receiver_phone,
            notes=visit_create.notes,
            created_by=owner_id,
        )
        visit = await repository.create_visit(session, visit)
        if visit.id is None:
            raise InvalidOperationError("Visit was not saved properly")
        assignees = await _replace_assignees(
            session,
            visit_id=visit.id,
            assignees=visit_create.assignees,
        )
        _validate_schedule_shape(visit, assignees)

        if _is_schedule_complete(visit, assignees):
            visit.status = TechnicalVisitStatus.SCHEDULED
        if lead.technical_visit_requirement == TechnicalVisitRequirement.UNDETERMINED:
            lead.technical_visit_requirement = TechnicalVisitRequirement.REQUIRED
            session.add(lead)

        session.add(visit)
        await session.flush()
        await session.commit()
        return await get_visit(session, visit.id, owner_id=owner_id)
    except Exception:
        await session.rollback()
        raise


async def get_visit(
    session: AsyncSession,
    visit_id: int,
    *,
    owner_id: int,
) -> TechnicalVisit:
    """Return one technical visit visible to the user."""

    visit = await repository.get_visit(session, visit_id)
    if visit is None:
        raise NotFoundError(
            "Technical visit not found",
            details={"visit_id": visit_id},
        )
    if not await permissions_service.user_can_access_technical_visit(
        session,
        user_id=owner_id,
        visit_id=visit_id,
    ):
        raise AuthorizationError("Technical visit belongs to another owner")
    return visit


async def list_visits(
    session: AsyncSession,
    *,
    owner_id: int,
    lead_id: int | None = None,
    status: TechnicalVisitStatus | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[TechnicalVisit]:
    """Return technical visits visible to the provided user."""

    role = await permissions_service.get_user_crm_role(session, owner_id)
    if lead_id is not None:
        await leads_service.get_lead(session, lead_id, owner_id=owner_id)
        if role in {UserRole.ADMIN, UserRole.MANAGER}:
            visits = await repository.list_all_visits(
                session,
                lead_id=lead_id,
                status=status,
                limit=limit,
                offset=offset,
            )
        elif role == UserRole.TECH:
            visits = await repository.list_visits_for_assignee_or_creator(
                session,
                owner_id,
                lead_id=lead_id,
                status=status,
                limit=limit,
                offset=offset,
            )
        else:
            visits = await repository.list_visits_for_lead(
                session,
                lead_id,
                status=status,
                limit=limit,
                offset=offset,
            )
        return list(visits)

    if role in {UserRole.ADMIN, UserRole.MANAGER}:
        visits = await repository.list_all_visits(
            session,
            status=status,
            limit=limit,
            offset=offset,
        )
    elif role == UserRole.TECH:
        visits = await repository.list_visits_for_assignee_or_creator(
            session,
            owner_id,
            status=status,
            limit=limit,
            offset=offset,
        )
    else:
        visits = await repository.list_visits_for_owner(
            session,
            owner_id,
            status=status,
            limit=limit,
            offset=offset,
        )
    return list(visits)


async def update_visit(
    session: AsyncSession,
    visit_id: int,
    visit_update: TechnicalVisitUpdate,
    *,
    owner_id: int,
) -> TechnicalVisit:
    """Update scheduling metadata for a requested or scheduled visit."""

    try:
        visit = await get_visit(session, visit_id, owner_id=owner_id)
        _ensure_visit_editable(visit)

        updates = visit_update.model_dump(exclude_unset=True, exclude={"assignees"})
        _apply_visit_updates(visit, updates)
        assignees = await _assignees_for_visit_update(session, visit, visit_update)
        _validate_schedule_shape(visit, assignees)
        visit.status = _visit_status_for_schedule(visit, assignees)
        visit.updated_at = datetime.now(UTC)
        session.add(visit)
        await session.flush()
        await session.commit()
        return await get_visit(session, visit_id, owner_id=owner_id)
    except Exception:
        await session.rollback()
        raise


async def complete_visit(
    session: AsyncSession,
    visit_id: int,
    *,
    owner_id: int,
) -> TechnicalVisit:
    """Mark a scheduled technical visit completed."""

    visit = await get_visit(session, visit_id, owner_id=owner_id)
    if visit.status == TechnicalVisitStatus.CANCELLED:
        raise InvalidOperationError("Cancelled technical visits cannot be completed")
    if visit.status == TechnicalVisitStatus.COMPLETED:
        raise InvalidOperationError("Technical visit is already completed")

    if visit.id is None:
        raise InvalidOperationError("Visit was not saved properly")
    assignees = list(await repository.list_assignees(session, visit.id))
    if not _is_schedule_complete(visit, assignees):
        raise InvalidOperationError("Only scheduled technical visits can be completed")
    attachments = await repository.list_attachments(session, visit.id, limit=1)
    if not attachments:
        raise InvalidOperationError(
            "At least one attachment is required to complete a technical visit"
        )

    visit.status = TechnicalVisitStatus.COMPLETED
    visit.completed_at = datetime.now(UTC)
    visit.updated_at = visit.completed_at
    session.add(visit)
    await session.flush()
    await session.commit()
    return await get_visit(session, visit_id, owner_id=owner_id)


async def cancel_visit(
    session: AsyncSession,
    visit_id: int,
    visit_cancel: TechnicalVisitCancel,
    *,
    owner_id: int,
) -> TechnicalVisit:
    """Cancel a requested or scheduled technical visit."""

    visit = await get_visit(session, visit_id, owner_id=owner_id)
    if visit.status == TechnicalVisitStatus.COMPLETED:
        raise InvalidOperationError("Completed technical visits cannot be cancelled")
    if visit.status == TechnicalVisitStatus.CANCELLED:
        raise InvalidOperationError("Technical visit is already cancelled")

    visit.status = TechnicalVisitStatus.CANCELLED
    visit.cancelled_at = datetime.now(UTC)
    visit.cancellation_reason = visit_cancel.reason
    visit.updated_at = visit.cancelled_at
    session.add(visit)
    await session.flush()
    await session.commit()
    return await get_visit(session, visit_id, owner_id=owner_id)


async def upload_attachment(
    session: AsyncSession,
    visit_id: int,
    *,
    title: str,
    file_kind: TechnicalVisitAttachmentKind,
    upload: UploadFileLike,
    owner_id: int,
    storage_root: str | Path | None = None,
) -> TechnicalVisitAttachment:
    """Upload a document, photo, or other evidence file for a technical visit."""

    visit = await get_visit(session, visit_id, owner_id=owner_id)
    if visit.status == TechnicalVisitStatus.CANCELLED:
        raise InvalidOperationError("Cannot upload attachments to a cancelled visit")
    if visit.id is None:
        raise InvalidOperationError("Visit was not saved properly")

    normalized_title = _normalize_required_text(title, field_name="title")
    stored_upload = await save_upload(
        upload,
        directory_parts=(
            f"technical-visit-{visit.id}",
            "attachments",
            file_kind.value.lower(),
        ),
        storage_root=storage_root,
    )
    attachment = TechnicalVisitAttachment(
        visit_id=visit.id,
        title=normalized_title,
        file_kind=file_kind,
        original_filename=stored_upload.original_filename,
        content_type=stored_upload.content_type,
        stored_path=stored_upload.stored_path,
        size_bytes=stored_upload.size_bytes,
        uploaded_by=owner_id,
    )
    try:
        attachment = await repository.create_attachment(session, attachment)
        await session.commit()
    except Exception:
        await session.rollback()
        delete_stored_file(stored_upload.stored_path)
        raise
    return attachment


async def list_attachments(
    session: AsyncSession,
    visit_id: int,
    *,
    owner_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[TechnicalVisitAttachment]:
    """List attachments for an owned technical visit."""

    visit = await get_visit(session, visit_id, owner_id=owner_id)
    if visit.id is None:
        raise InvalidOperationError("Visit was not saved properly")
    attachments = await repository.list_attachments(
        session,
        visit.id,
        limit=limit,
        offset=offset,
    )
    return list(attachments)


async def get_attachment(
    session: AsyncSession,
    visit_id: int,
    attachment_id: int,
    *,
    owner_id: int,
) -> TechnicalVisitAttachment:
    """Return one attachment for an owned technical visit."""

    visit = await get_visit(session, visit_id, owner_id=owner_id)
    attachment = await repository.get_attachment(session, attachment_id)
    if attachment is None or attachment.visit_id != visit.id:
        raise NotFoundError(
            "Technical visit attachment not found",
            details={"visit_id": visit_id, "attachment_id": attachment_id},
        )
    return attachment


async def delete_attachment(
    session: AsyncSession,
    visit_id: int,
    attachment_id: int,
    *,
    owner_id: int,
) -> None:
    """Delete one technical visit attachment."""

    attachment = await get_attachment(
        session,
        visit_id,
        attachment_id,
        owner_id=owner_id,
    )
    stored_path = attachment.stored_path
    try:
        await repository.delete_attachment(session, attachment)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    delete_stored_file(stored_path)


async def link_proposal_visit(
    session: AsyncSession,
    proposal_id: int,
    link_create: ProposalTechnicalVisitCreate,
    *,
    owner_id: int,
) -> ProposalTechnicalVisit:
    """Link a proposal to technical visit evidence from the same lead."""

    proposal = await proposals_service.get_proposal(
        session,
        proposal_id,
        user_id=owner_id,
    )
    visit = await get_visit(
        session,
        link_create.technical_visit_id,
        owner_id=owner_id,
    )
    if proposal.lead_id != visit.lead_id:
        raise InvalidOperationError("Proposal and technical visit must belong to the same lead")

    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    if visit.id is None:
        raise InvalidOperationError("Visit was not saved properly")
    existing = await repository.get_proposal_link(
        session,
        proposal_id=proposal.id,
        technical_visit_id=visit.id,
    )
    if existing is not None:
        raise ConflictError("Proposal is already linked to this technical visit")

    link = ProposalTechnicalVisit(
        proposal_id=proposal.id,
        technical_visit_id=visit.id,
        relationship_type=link_create.relationship_type,
        notes=link_create.notes,
        linked_by=owner_id,
    )
    link = await repository.create_proposal_link(session, link)
    await session.commit()
    return link


async def list_proposal_visit_links(
    session: AsyncSession,
    proposal_id: int,
    *,
    owner_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[ProposalTechnicalVisit]:
    """List technical visit evidence links for an owned proposal."""

    proposal = await proposals_service.get_proposal(
        session,
        proposal_id,
        user_id=owner_id,
    )
    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    links = await repository.list_links_for_proposal(
        session,
        proposal.id,
        limit=limit,
        offset=offset,
    )
    return list(links)


async def unlink_proposal_visit(
    session: AsyncSession,
    proposal_id: int,
    technical_visit_id: int,
    *,
    owner_id: int,
) -> None:
    """Remove a Proposal-to-TechnicalVisit relationship."""

    proposal = await proposals_service.get_proposal(
        session,
        proposal_id,
        user_id=owner_id,
    )
    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    link = await repository.get_proposal_link(
        session,
        proposal_id=proposal.id,
        technical_visit_id=technical_visit_id,
    )
    if link is None:
        raise NotFoundError(
            "Proposal technical visit link not found",
            details={
                "proposal_id": proposal_id,
                "technical_visit_id": technical_visit_id,
            },
        )
    await repository.delete_proposal_link(session, link)
    await session.commit()
