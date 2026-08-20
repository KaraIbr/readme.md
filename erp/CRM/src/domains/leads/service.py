"""Leads business logic."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from core.storage import (
    ALLOWED_DOCUMENT_MIME_TYPES,
    UploadFileLike,
    delete_stored_file,
    save_upload,
)
from core.storage import (
    stored_file_path as resolve_stored_file_path,
)
from domains.contacts.service import get_contact
from domains.leads import repository
from domains.leads.models import (
    Lead,
    LeadDocument,
    LeadElectricityBill,
    LeadInteraction,
    LeadOutcome,
    LeadStage,
)
from domains.leads.schemas import (
    LeadCreate,
    LeadInteractionCreate,
    LeadInteractionUpdate,
    LeadUpdate,
)
from domains.permissions import service as permissions_service
from domains.permissions.models import UserRole
from domains.pipeline import service as pipeline_service
from domains.pipeline.models import PipelineEntityType
from sqlmodel.ext.asyncio.session import AsyncSession


def _stage_for_outcome(outcome: LeadOutcome) -> LeadStage:
    if outcome == LeadOutcome.WON:
        return LeadStage.CLOSED_WON
    return LeadStage.CLOSED_LOST


def _ensure_open(lead: Lead) -> None:
    if lead.current_stage in {LeadStage.CLOSED_WON, LeadStage.CLOSED_LOST}:
        raise InvalidOperationError("Closed leads cannot be modified")


async def _validate_owned_contact(
    session: AsyncSession,
    *,
    contact_id: int,
    owner_id: int,
) -> None:
    await get_contact(session, contact_id, owner_id=owner_id)


def _normalize_required_text(value: str, *, field_name: str = "value") -> str:
    normalized = value.strip()
    if not normalized:
        raise InvalidOperationError(f"{field_name} cannot be blank")
    return normalized


def stored_file_path(stored_path: str) -> Path:
    """Return an uploaded file path or raise if the blob is missing."""

    return resolve_stored_file_path(stored_path)


async def create_lead(
    session: AsyncSession,
    lead_create: LeadCreate,
    *,
    owner_id: int,
) -> Lead:
    """Create a lead for an owned contact."""

    await _validate_owned_contact(
        session,
        contact_id=lead_create.contact_id,
        owner_id=owner_id,
    )

    lead = Lead(owner_id=owner_id, **lead_create.model_dump())
    lead = await repository.create(session, lead)
    if lead.id is None:
        raise InvalidOperationError("Lead was not saved properly")
    await pipeline_service.record_initial_transition(
        session,
        PipelineEntityType.LEAD,
        lead.id,
        to_stage=lead.current_stage,
        by=owner_id,
        commit=False,
    )
    await session.commit()
    return lead


async def get_lead(
    session: AsyncSession,
    lead_id: int,
    *,
    owner_id: int,
) -> Lead:
    """Return an owned lead or raise a domain-level error."""

    lead = await repository.get(session, lead_id)
    if lead is None:
        raise NotFoundError("Lead not found", details={"lead_id": lead_id})
    if lead.owner_id != owner_id and not await permissions_service.user_can_access_lead(
        session,
        user_id=owner_id,
        lead_id=lead_id,
    ):
        raise AuthorizationError("Lead belongs to another owner")
    return lead


async def list_leads(
    session: AsyncSession,
    *,
    owner_id: int,
    contact_id: int | None = None,
    stage: LeadStage | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Lead]:
    """Return leads owned by the provided user."""

    role = await permissions_service.get_user_crm_role(session, owner_id)
    if role in {UserRole.ADMIN, UserRole.MANAGER}:
        leads = await repository.list_all(
            session,
            contact_id=contact_id,
            stage=stage,
            limit=limit,
            offset=offset,
        )
    elif role == UserRole.TECH:
        leads = await repository.list_for_assigned_tech(
            session,
            owner_id,
            contact_id=contact_id,
            stage=stage,
            limit=limit,
            offset=offset,
        )
    else:
        leads = await repository.list_for_owner(
            session,
            owner_id,
            contact_id=contact_id,
            stage=stage,
            limit=limit,
            offset=offset,
        )
    return list(leads)


async def search_leads(
    session: AsyncSession,
    *,
    owner_id: int,
    query: str,
    limit: int = 20,
) -> list[Lead]:
    """Search leads visible to the provided user."""

    role = await permissions_service.get_user_crm_role(session, owner_id)
    if role in {UserRole.ADMIN, UserRole.MANAGER}:
        leads = await repository.search_all(
            session,
            query=query,
            limit=limit,
        )
    elif role == UserRole.TECH:
        leads = await repository.search_for_assigned_tech(
            session,
            owner_id,
            query=query,
            limit=limit,
        )
    else:
        leads = await repository.search_for_owner(
            session,
            owner_id,
            query=query,
            limit=limit,
        )
    return list(leads)


async def upload_document(
    session: AsyncSession,
    lead_id: int,
    *,
    title: str,
    upload: UploadFileLike,
    owner_id: int,
    storage_root: str | Path | None = None,
) -> LeadDocument:
    """Upload a general project document for an owned lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    if lead.id is None:
        raise InvalidOperationError("Lead was not saved properly")
    normalized_title = _normalize_required_text(title, field_name="title")
    stored_upload = await save_upload(
        upload,
        directory_parts=(f"lead-{lead.id}", "documents"),
        storage_root=storage_root,
        allowed_mime_types=ALLOWED_DOCUMENT_MIME_TYPES,
    )
    document = LeadDocument(
        lead_id=lead.id,
        title=normalized_title,
        original_filename=stored_upload.original_filename,
        content_type=stored_upload.content_type,
        stored_path=stored_upload.stored_path,
        size_bytes=stored_upload.size_bytes,
        uploaded_by=owner_id,
    )
    try:
        document = await repository.create_document(session, document)
        await session.commit()
    except Exception:
        await session.rollback()
        delete_stored_file(stored_upload.stored_path)
        raise
    return document


async def list_documents(
    session: AsyncSession,
    lead_id: int,
    *,
    owner_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[LeadDocument]:
    """List general documents attached to an owned lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    if lead.id is None:
        raise InvalidOperationError("Lead was not saved properly")
    documents = await repository.list_documents(
        session,
        lead.id,
        limit=limit,
        offset=offset,
    )
    return list(documents)


async def get_document(
    session: AsyncSession,
    lead_id: int,
    document_id: int,
    *,
    owner_id: int,
) -> LeadDocument:
    """Return one general document attached to an owned lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    document = await repository.get_document(session, document_id)
    if document is None or document.lead_id != lead.id:
        raise NotFoundError(
            "Lead document not found",
            details={"lead_id": lead_id, "document_id": document_id},
        )
    return document


async def delete_document(
    session: AsyncSession,
    lead_id: int,
    document_id: int,
    *,
    owner_id: int,
) -> None:
    """Delete one general document attached to an owned lead."""

    document = await get_document(
        session,
        lead_id,
        document_id,
        owner_id=owner_id,
    )
    stored_path = document.stored_path
    try:
        await repository.delete_document(session, document)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    delete_stored_file(stored_path)


async def upload_electricity_bill(
    session: AsyncSession,
    lead_id: int,
    *,
    title: str,
    upload: UploadFileLike,
    owner_id: int,
    storage_root: str | Path | None = None,
) -> LeadElectricityBill:
    """Upload an electricity bill for an owned lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    if lead.id is None:
        raise InvalidOperationError("Lead was not saved properly")
    normalized_title = _normalize_required_text(title, field_name="title")
    stored_upload = await save_upload(
        upload,
        directory_parts=(f"lead-{lead.id}", "electricity-bills"),
        storage_root=storage_root,
        allowed_mime_types=ALLOWED_DOCUMENT_MIME_TYPES,
    )
    bill = LeadElectricityBill(
        lead_id=lead.id,
        title=normalized_title,
        original_filename=stored_upload.original_filename,
        content_type=stored_upload.content_type,
        stored_path=stored_upload.stored_path,
        size_bytes=stored_upload.size_bytes,
        uploaded_by=owner_id,
    )
    try:
        bill = await repository.create_electricity_bill(session, bill)
        await session.commit()
    except Exception:
        await session.rollback()
        delete_stored_file(stored_upload.stored_path)
        raise
    return bill


async def list_electricity_bills(
    session: AsyncSession,
    lead_id: int,
    *,
    owner_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[LeadElectricityBill]:
    """List electricity bills attached to an owned lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    if lead.id is None:
        raise InvalidOperationError("Lead was not saved properly")
    bills = await repository.list_electricity_bills(
        session,
        lead.id,
        limit=limit,
        offset=offset,
    )
    return list(bills)


async def get_electricity_bill(
    session: AsyncSession,
    lead_id: int,
    bill_id: int,
    *,
    owner_id: int,
) -> LeadElectricityBill:
    """Return one electricity bill attached to an owned lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    bill = await repository.get_electricity_bill(session, bill_id)
    if bill is None or bill.lead_id != lead.id:
        raise NotFoundError(
            "Lead electricity bill not found",
            details={"lead_id": lead_id, "bill_id": bill_id},
        )
    return bill


async def delete_electricity_bill(
    session: AsyncSession,
    lead_id: int,
    bill_id: int,
    *,
    owner_id: int,
) -> None:
    """Delete one electricity bill attached to an owned lead."""

    bill = await get_electricity_bill(
        session,
        lead_id,
        bill_id,
        owner_id=owner_id,
    )
    stored_path = bill.stored_path
    try:
        await repository.delete_electricity_bill(session, bill)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    delete_stored_file(stored_path)


async def create_interaction(
    session: AsyncSession,
    lead_id: int,
    interaction_create: LeadInteractionCreate,
    *,
    owner_id: int,
) -> LeadInteraction:
    """Document a sales interaction or negotiation for an owned lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    if lead.id is None:
        raise InvalidOperationError("Lead was not saved properly")
    interaction = LeadInteraction(
        lead_id=lead.id,
        interaction_type=interaction_create.interaction_type,
        title=interaction_create.title,
        notes=interaction_create.notes,
        interaction_date=interaction_create.interaction_date,
        created_by=owner_id,
    )
    interaction = await repository.create_interaction(session, interaction)
    await session.commit()
    return interaction


async def list_interactions(
    session: AsyncSession,
    lead_id: int,
    *,
    owner_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[LeadInteraction]:
    """List documented interactions for an owned lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    if lead.id is None:
        raise InvalidOperationError("Lead was not saved properly")
    interactions = await repository.list_interactions(
        session,
        lead.id,
        limit=limit,
        offset=offset,
    )
    return list(interactions)


async def get_interaction(
    session: AsyncSession,
    lead_id: int,
    interaction_id: int,
    *,
    owner_id: int,
) -> LeadInteraction:
    """Return one documented lead interaction."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    interaction = await repository.get_interaction(session, interaction_id)
    if interaction is None or interaction.lead_id != lead.id:
        raise NotFoundError(
            "Lead interaction not found",
            details={"lead_id": lead_id, "interaction_id": interaction_id},
        )
    return interaction


async def update_interaction(
    session: AsyncSession,
    lead_id: int,
    interaction_id: int,
    interaction_update: LeadInteractionUpdate,
    *,
    owner_id: int,
) -> LeadInteraction:
    """Update a documented lead interaction."""

    interaction = await get_interaction(
        session,
        lead_id,
        interaction_id,
        owner_id=owner_id,
    )
    updates = interaction_update.model_dump(exclude_unset=True)
    for field, value in updates.items():
        if value is not None:
            setattr(interaction, field, value)
    interaction.updated_at = datetime.now(UTC)
    session.add(interaction)
    await session.flush()
    await session.refresh(interaction)
    await session.commit()
    return interaction


async def delete_interaction(
    session: AsyncSession,
    lead_id: int,
    interaction_id: int,
    *,
    owner_id: int,
) -> None:
    """Delete one documented lead interaction."""

    interaction = await get_interaction(
        session,
        lead_id,
        interaction_id,
        owner_id=owner_id,
    )
    await repository.delete_interaction(session, interaction)
    await session.commit()


async def update_lead(
    session: AsyncSession,
    lead_id: int,
    lead_update: LeadUpdate,
    *,
    owner_id: int,
) -> Lead:
    """Partially update an owned open lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    _ensure_open(lead)
    updates: dict[str, Any] = lead_update.model_dump(exclude_unset=True)

    next_contact_id = updates.get("contact_id")
    if next_contact_id is not None:
        await _validate_owned_contact(
            session,
            contact_id=next_contact_id,
            owner_id=owner_id,
        )

    for field, value in updates.items():
        setattr(lead, field, value)

    session.add(lead)
    await session.flush()
    await session.refresh(lead)
    await session.commit()
    return lead


async def move_to_stage(
    session: AsyncSession,
    lead_id: int,
    *,
    stage: LeadStage,
    owner_id: int,
) -> Lead:
    """Move an owned lead through a valid open-stage transition."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    _ensure_open(lead)
    if stage in {LeadStage.CLOSED_WON, LeadStage.CLOSED_LOST}:
        raise InvalidOperationError("Use close to move a lead to a terminal stage")
    if stage == lead.current_stage:
        return lead
    pipeline_service.ensure_transition_allowed(
        entity_type=PipelineEntityType.LEAD,
        from_stage=lead.current_stage,
        to_stage=stage,
    )

    if lead.id is None:
        raise InvalidOperationError("Lead was not saved properly")
    await pipeline_service.transition(
        session,
        PipelineEntityType.LEAD,
        lead.id,
        to_stage=stage,
        by=owner_id,
        commit=False,
    )
    await session.flush()
    await session.refresh(lead)
    await session.commit()
    return lead


async def close(
    session: AsyncSession,
    lead_id: int,
    *,
    outcome: LeadOutcome,
    by: int,
    notes: str | None = None,
    commit: bool = True,
) -> Lead:
    """Close a lead with an outcome reflected from proposal or abandonment flow."""

    lead = await get_lead(session, lead_id, owner_id=by)
    _ensure_open(lead)
    target_stage = _stage_for_outcome(outcome)
    if lead.id is None:
        raise InvalidOperationError("Lead was not saved properly")
    await pipeline_service.transition(
        session,
        PipelineEntityType.LEAD,
        lead.id,
        to_stage=target_stage,
        by=by,
        reason=f"outcome:{outcome.value}",
        notes=notes,
        commit=False,
    )
    lead.outcome = outcome
    lead.closed_at = datetime.now(UTC)
    if notes is not None:
        lead.notes = notes

    session.add(lead)
    await session.flush()
    await session.refresh(lead)
    if commit:
        await session.commit()
    return lead


async def delete_lead(
    session: AsyncSession,
    lead_id: int,
    *,
    owner_id: int,
) -> None:
    """Delete an owned open lead."""

    lead = await get_lead(session, lead_id, owner_id=owner_id)
    _ensure_open(lead)
    await repository.delete(session, lead)
    await session.commit()
