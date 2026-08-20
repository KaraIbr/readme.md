"""Proposals business logic."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from core.exceptions import AuthorizationError, InvalidOperationError, NotFoundError
from core.storage import (
    UploadFileLike,
    delete_stored_file,
    save_upload,
)
from core.storage import (
    stored_file_path as resolve_stored_file_path,
)
from domains.leads import service as leads_service
from domains.leads.models import Lead, LeadOutcome, LeadStage
from domains.permissions import service as permissions_service
from domains.permissions.models import UserRole
from domains.pipeline import service as pipeline_service
from domains.pipeline.models import PipelineEntityType
from domains.proposals import repository
from domains.proposals.models import (
    Proposal,
    ProposalBESSSystem,
    ProposalCommercialDocument,
    ProposalDocument,
    ProposalDocumentClassification,
    ProposalPVSystem,
    ProposalStage,
    ProposalSystemType,
)
from domains.proposals.schemas import ProposalCreate, ProposalUpdate
from sqlmodel.ext.asyncio.session import AsyncSession

TERMINAL_STAGES = {
    ProposalStage.WON,
    ProposalStage.LOST,
    ProposalStage.SUPERSEDED,
}


def _ensure_non_terminal(proposal: Proposal) -> None:
    if proposal.current_stage in TERMINAL_STAGES:
        raise InvalidOperationError("Terminal proposals cannot be modified")


def _ensure_complete(proposal: Proposal) -> None:
    missing = proposal.missing_required_fields
    if missing:
        raise InvalidOperationError(
            "Proposal is incomplete and cannot advance beyond draft",
            details={"missing_required_fields": missing},
        )


def _ensure_system_detail_shape(proposal: Proposal) -> None:
    pv_system = proposal.__dict__.get("pv_system")
    bess_system = proposal.__dict__.get("bess_system")
    if proposal.system_type == ProposalSystemType.PV and bess_system is not None:
        raise InvalidOperationError("BESS details require system_type HIBRID or BESS")
    if proposal.system_type == ProposalSystemType.BESS and pv_system is not None:
        raise InvalidOperationError("PV details require system_type HIBRID or PV")


def _proposal_payload_data(
    payload: ProposalCreate | ProposalUpdate,
    *,
    exclude_unset: bool = False,
) -> dict[str, Any]:
    data = payload.model_dump(
        exclude_unset=exclude_unset,
        exclude={"pv_system", "bess_system"},
    )
    address = data.pop("installation_address", None)
    if address is not None:
        address_fields = {
            "address_line": "installation_address_line",
            "city": "installation_city",
            "state": "installation_state",
            "postal_code": "installation_postal_code",
        }
        for address_field, model_field in address_fields.items():
            if address_field in address:
                data[model_field] = address[address_field]
    return data


def _system_payload_data(
    payload: ProposalCreate | ProposalUpdate,
    field_name: str,
    *,
    exclude_unset: bool = False,
) -> dict[str, Any] | None:
    system_payload = getattr(payload, field_name)
    if system_payload is None:
        return None
    return system_payload.model_dump(exclude_unset=exclude_unset)


def _apply_proposal_updates(proposal: Proposal, updates: dict[str, Any]) -> None:
    for field, value in updates.items():
        setattr(proposal, field, value)


def _protected_price_permissions_needed(
    proposal: Proposal | None,
    payload: ProposalCreate | ProposalUpdate,
) -> set[str]:
    required: set[str] = set()

    def note_change(previous: Any, next_value: Any) -> None:
        if next_value is None or previous == next_value:
            return
        if previous is None:
            required.add("crm.proposals.price.set")
            return
        required.add("crm.proposals.price.update")

    if "total_price" in payload.model_fields_set:
        note_change(
            None if proposal is None else proposal.total_price,
            payload.total_price,
        )

    if "pv_system" in payload.model_fields_set and payload.pv_system is not None:
        pv_payload = payload.pv_system
        if "price_watt" in pv_payload.model_fields_set:
            current_pv = None if proposal is None else proposal.__dict__.get("pv_system")
            note_change(
                None if current_pv is None else current_pv.price_watt,
                pv_payload.price_watt,
            )

    if "bess_system" in payload.model_fields_set and payload.bess_system is not None:
        bess_payload = payload.bess_system
        if "price_kwh" in bess_payload.model_fields_set:
            current_bess = None if proposal is None else proposal.__dict__.get("bess_system")
            note_change(
                None if current_bess is None else current_bess.price_kwh,
                bess_payload.price_kwh,
            )

    return required


async def _require_price_permissions(
    session: AsyncSession,
    *,
    user_id: int,
    proposal: Proposal | None,
    payload: ProposalCreate | ProposalUpdate,
) -> None:
    for permission in sorted(_protected_price_permissions_needed(proposal, payload)):
        await permissions_service.require_permission(session, user_id, permission)


async def _upsert_pv_system(
    session: AsyncSession,
    proposal: Proposal,
    data: dict[str, Any],
) -> None:
    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    current_system = proposal.__dict__.get("pv_system")
    if current_system is None:
        proposal.pv_system = await repository.create_pv_system(
            session,
            ProposalPVSystem(proposal_id=proposal.id, **data),
        )
        return
    for field, value in data.items():
        setattr(current_system, field, value)
    session.add(current_system)


async def _upsert_bess_system(
    session: AsyncSession,
    proposal: Proposal,
    data: dict[str, Any],
) -> None:
    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    current_system = proposal.__dict__.get("bess_system")
    if current_system is None:
        proposal.bess_system = await repository.create_bess_system(
            session,
            ProposalBESSSystem(proposal_id=proposal.id, **data),
        )
        return
    for field, value in data.items():
        setattr(current_system, field, value)
    session.add(current_system)


async def _delete_pv_system(session: AsyncSession, proposal: Proposal) -> None:
    current_system = proposal.__dict__.get("pv_system")
    if current_system is not None:
        await repository.delete_pv_system(session, current_system)
        proposal.pv_system = None


async def _delete_bess_system(session: AsyncSession, proposal: Proposal) -> None:
    current_system = proposal.__dict__.get("bess_system")
    if current_system is not None:
        await repository.delete_bess_system(session, current_system)
        proposal.bess_system = None


async def _sync_pv_system_update(
    session: AsyncSession,
    proposal: Proposal,
    proposal_update: ProposalUpdate,
) -> None:
    if "pv_system" not in proposal_update.model_fields_set:
        return
    if proposal_update.pv_system is None:
        await _delete_pv_system(session, proposal)
        return
    pv_data = _system_payload_data(
        proposal_update,
        "pv_system",
        exclude_unset=True,
    )
    if pv_data is None:
        raise InvalidOperationError("PV system data was not provided")
    await _upsert_pv_system(session, proposal, pv_data)


async def _sync_bess_system_update(
    session: AsyncSession,
    proposal: Proposal,
    proposal_update: ProposalUpdate,
) -> None:
    if "bess_system" not in proposal_update.model_fields_set:
        return
    if proposal_update.bess_system is None:
        await _delete_bess_system(session, proposal)
        return
    bess_data = _system_payload_data(
        proposal_update,
        "bess_system",
        exclude_unset=True,
    )
    if bess_data is None:
        raise InvalidOperationError("BESS system data was not provided")
    await _upsert_bess_system(session, proposal, bess_data)


async def _sync_proposal_system_updates(
    session: AsyncSession,
    proposal: Proposal,
    proposal_update: ProposalUpdate,
) -> None:
    await _sync_pv_system_update(session, proposal, proposal_update)
    await _sync_bess_system_update(session, proposal, proposal_update)


async def _get_owned_lead(
    session: AsyncSession,
    *,
    lead_id: int,
    user_id: int,
) -> Lead:
    return await leads_service.get_lead(session, lead_id, owner_id=user_id)


def _ensure_sent_before_terminal(proposal: Proposal) -> None:
    if proposal.current_stage == ProposalStage.DRAFT:
        raise InvalidOperationError("Proposal must be sent before terminal outcome")


def _normalize_required_text(value: str, *, field_name: str = "value") -> str:
    normalized = value.strip()
    if not normalized:
        raise InvalidOperationError(f"{field_name} cannot be blank")
    return normalized


def stored_file_path(stored_path: str) -> Path:
    """Return an uploaded file path or raise if the blob is missing."""

    return resolve_stored_file_path(stored_path)


async def create_proposal(
    session: AsyncSession,
    proposal_create: ProposalCreate,
    *,
    created_by: int,
    enforce_price_permissions: bool = False,
) -> Proposal:
    """Create a proposal variant for an owned open lead."""

    try:
        if enforce_price_permissions:
            await _require_price_permissions(
                session,
                user_id=created_by,
                proposal=None,
                payload=proposal_create,
            )
        lead = await _get_owned_lead(
            session,
            lead_id=proposal_create.lead_id,
            user_id=created_by,
        )
        if lead.current_stage in {LeadStage.CLOSED_WON, LeadStage.CLOSED_LOST}:
            raise InvalidOperationError("Cannot create proposals for a closed lead")

        proposal = Proposal(
            created_by=created_by,
            **_proposal_payload_data(proposal_create),
        )
        proposal = await repository.create(session, proposal)
        if proposal.id is None:
            raise InvalidOperationError("Proposal was not saved properly")

        pv_data = _system_payload_data(proposal_create, "pv_system")
        if pv_data is not None:
            await _upsert_pv_system(session, proposal, pv_data)
        bess_data = _system_payload_data(proposal_create, "bess_system")
        if bess_data is not None:
            await _upsert_bess_system(session, proposal, bess_data)
        _ensure_system_detail_shape(proposal)

        await pipeline_service.record_initial_transition(
            session,
            PipelineEntityType.PROPOSAL,
            proposal.id,
            to_stage=proposal.current_stage,
            by=created_by,
            commit=False,
        )
        await session.commit()
        return await get_proposal(session, proposal.id, user_id=created_by)
    except Exception:
        await session.rollback()
        raise


async def get_proposal(
    session: AsyncSession,
    proposal_id: int,
    *,
    user_id: int,
) -> Proposal:
    """Return an owned proposal or raise a domain-level error."""

    proposal = await repository.get(session, proposal_id)
    if proposal is None:
        raise NotFoundError(
            "Proposal not found",
            details={"proposal_id": proposal_id},
        )
    if proposal.created_by != user_id and not await permissions_service.user_can_access_proposal(
        session,
        user_id=user_id,
        proposal_id=proposal_id,
    ):
        raise AuthorizationError("Proposal belongs to another user")
    return proposal


async def list_proposals(
    session: AsyncSession,
    *,
    user_id: int,
    lead_id: int | None = None,
    stage: ProposalStage | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Proposal]:
    """Return proposals created by the provided user."""

    role = await permissions_service.get_user_crm_role(session, user_id)
    if role == UserRole.SALES:
        proposals = await repository.list_for_lead_owner(
            session,
            user_id,
            lead_id=lead_id,
            stage=stage,
            limit=limit,
            offset=offset,
        )
    elif role == UserRole.TECH:
        proposals = await repository.list_for_assigned_tech(
            session,
            user_id,
            lead_id=lead_id,
            stage=stage,
            limit=limit,
            offset=offset,
        )
    elif role in {UserRole.ADMIN, UserRole.MANAGER}:
        proposals = await repository.list_all(
            session,
            lead_id=lead_id,
            stage=stage,
            limit=limit,
            offset=offset,
        )
    else:
        proposals = await repository.list_for_user(
            session,
            user_id,
            lead_id=lead_id,
            stage=stage,
            limit=limit,
            offset=offset,
        )
    return list(proposals)


async def search_proposals(
    session: AsyncSession,
    *,
    user_id: int,
    query: str,
    limit: int = 20,
) -> list[Proposal]:
    """Search proposals visible to the provided user."""

    role = await permissions_service.get_user_crm_role(session, user_id)
    if role == UserRole.SALES:
        proposals = await repository.search_for_lead_owner(
            session,
            user_id,
            query=query,
            limit=limit,
        )
    elif role == UserRole.TECH:
        proposals = await repository.search_for_assigned_tech(
            session,
            user_id,
            query=query,
            limit=limit,
        )
    elif role in {UserRole.ADMIN, UserRole.MANAGER}:
        proposals = await repository.search_all(
            session,
            query=query,
            limit=limit,
        )
    else:
        proposals = await repository.search_for_user(
            session,
            user_id,
            query=query,
            limit=limit,
        )
    return list(proposals)


async def update_proposal(
    session: AsyncSession,
    proposal_id: int,
    proposal_update: ProposalUpdate,
    *,
    user_id: int,
    enforce_price_permissions: bool = False,
) -> Proposal:
    """Partially update an owned non-terminal proposal."""

    try:
        proposal = await get_proposal(session, proposal_id, user_id=user_id)
        _ensure_non_terminal(proposal)
        await _get_owned_lead(session, lead_id=proposal.lead_id, user_id=user_id)
        if enforce_price_permissions:
            await _require_price_permissions(
                session,
                user_id=user_id,
                proposal=proposal,
                payload=proposal_update,
            )
        updates: dict[str, Any] = _proposal_payload_data(
            proposal_update,
            exclude_unset=True,
        )
        _apply_proposal_updates(proposal, updates)
        await _sync_proposal_system_updates(session, proposal, proposal_update)
        _ensure_system_detail_shape(proposal)
        if proposal.current_stage != ProposalStage.DRAFT:
            _ensure_complete(proposal)

        session.add(proposal)
        await session.flush()
        await session.commit()
        return await get_proposal(session, proposal_id, user_id=user_id)
    except Exception:
        await session.rollback()
        raise


async def move_to_stage(
    session: AsyncSession,
    proposal_id: int,
    *,
    stage: ProposalStage,
    user_id: int,
) -> Proposal:
    """Move an owned proposal through a valid non-terminal stage transition."""

    proposal = await get_proposal(session, proposal_id, user_id=user_id)
    _ensure_non_terminal(proposal)
    await _get_owned_lead(session, lead_id=proposal.lead_id, user_id=user_id)

    if stage in TERMINAL_STAGES:
        raise InvalidOperationError("Use a terminal proposal action for this stage")
    if stage == proposal.current_stage:
        return proposal
    if stage != ProposalStage.DRAFT:
        _ensure_complete(proposal)

    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    await pipeline_service.transition(
        session,
        PipelineEntityType.PROPOSAL,
        proposal.id,
        to_stage=stage,
        by=user_id,
        commit=False,
    )
    if stage == ProposalStage.SENT and proposal.proposed_at is None:
        proposal.proposed_at = datetime.now(UTC)

    session.add(proposal)
    await session.flush()
    await session.commit()
    return await get_proposal(session, proposal_id, user_id=user_id)


async def mark_won(proposal_id: int, user_id: int, session: AsyncSession) -> Proposal:
    """Mark one proposal as won, supersede active siblings, and close its lead."""

    try:
        proposal = await get_proposal(session, proposal_id, user_id=user_id)
        _ensure_non_terminal(proposal)
        _ensure_sent_before_terminal(proposal)
        _ensure_complete(proposal)
        lead = await _get_owned_lead(session, lead_id=proposal.lead_id, user_id=user_id)
        if lead.current_stage in {LeadStage.CLOSED_WON, LeadStage.CLOSED_LOST}:
            raise InvalidOperationError("Cannot win a proposal for a closed lead")

        existing_won = await repository.get_won_for_lead(
            session,
            lead_id=proposal.lead_id,
        )
        if existing_won is not None and existing_won.id != proposal.id:
            raise InvalidOperationError("Lead already has a winning proposal")

        if proposal.id is None:
            raise InvalidOperationError("Proposal was not saved properly")
        await pipeline_service.transition(
            session,
            PipelineEntityType.PROPOSAL,
            proposal.id,
            to_stage=ProposalStage.WON,
            by=user_id,
            reason="accepted",
            commit=False,
        )
        proposal.loss_reason = None
        session.add(proposal)

        siblings = await repository.list_active_siblings(
            session,
            lead_id=proposal.lead_id,
            exclude_id=proposal.id or 0,
        )
        for sibling in siblings:
            if sibling.id is None:
                raise InvalidOperationError("Sibling proposal was not saved properly")
            await pipeline_service.transition(
                session,
                PipelineEntityType.PROPOSAL,
                sibling.id,
                to_stage=ProposalStage.SUPERSEDED,
                by=user_id,
                reason=f"Lead won with proposal #{proposal.id}",
                commit=False,
            )
            session.add(sibling)

        await leads_service.close(
            session,
            proposal.lead_id,
            outcome=LeadOutcome.WON,
            by=user_id,
            commit=False,
        )
        await session.flush()
        await session.commit()
        return await get_proposal(session, proposal_id, user_id=user_id)
    except Exception:
        await session.rollback()
        raise


async def mark_lost(
    session: AsyncSession,
    proposal_id: int,
    *,
    user_id: int,
    loss_reason: str,
) -> Proposal:
    """Mark one proposal as lost and close the lead if no active options remain."""

    try:
        normalized_loss_reason = loss_reason.strip()
        if not normalized_loss_reason:
            raise InvalidOperationError("loss_reason is required when losing a proposal")

        proposal = await get_proposal(session, proposal_id, user_id=user_id)
        _ensure_non_terminal(proposal)
        _ensure_sent_before_terminal(proposal)
        _ensure_complete(proposal)
        lead = await _get_owned_lead(session, lead_id=proposal.lead_id, user_id=user_id)
        if lead.current_stage in {LeadStage.CLOSED_WON, LeadStage.CLOSED_LOST}:
            raise InvalidOperationError("Cannot lose a proposal for a closed lead")

        proposal.loss_reason = normalized_loss_reason
        session.add(proposal)
        if proposal.id is None:
            raise InvalidOperationError("Proposal was not saved properly")
        await pipeline_service.transition(
            session,
            PipelineEntityType.PROPOSAL,
            proposal.id,
            to_stage=ProposalStage.LOST,
            by=user_id,
            reason="rejected",
            notes=normalized_loss_reason,
            commit=False,
        )
        await session.flush()

        active_remaining = await repository.has_active_for_lead(
            session,
            lead_id=proposal.lead_id,
        )
        won_proposal = await repository.get_won_for_lead(
            session,
            lead_id=proposal.lead_id,
        )
        if not active_remaining and won_proposal is None:
            await leads_service.close(
                session,
                proposal.lead_id,
                outcome=LeadOutcome.LOST,
                by=user_id,
                notes=normalized_loss_reason,
                commit=False,
            )

        await session.commit()
        return await get_proposal(session, proposal_id, user_id=user_id)
    except Exception:
        await session.rollback()
        raise


async def delete_proposal(
    session: AsyncSession,
    proposal_id: int,
    *,
    user_id: int,
) -> None:
    """Delete an owned non-terminal proposal."""

    proposal = await get_proposal(session, proposal_id, user_id=user_id)
    _ensure_non_terminal(proposal)
    await _get_owned_lead(session, lead_id=proposal.lead_id, user_id=user_id)
    await _delete_pv_system(session, proposal)
    await _delete_bess_system(session, proposal)
    await repository.delete(session, proposal)
    await session.commit()


async def upload_commercial_document(
    session: AsyncSession,
    proposal_id: int,
    *,
    title: str,
    upload: UploadFileLike,
    user_id: int,
    storage_root: str | Path | None = None,
) -> ProposalCommercialDocument:
    """Upload the customer-facing commercial proposal PDF."""

    proposal = await get_proposal(session, proposal_id, user_id=user_id)
    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    normalized_title = _normalize_required_text(title, field_name="title")
    stored_upload = await save_upload(
        upload,
        directory_parts=(f"proposal-{proposal.id}", "commercial-pdf"),
        storage_root=storage_root,
    )
    document = ProposalCommercialDocument(
        proposal_id=proposal.id,
        title=normalized_title,
        original_filename=stored_upload.original_filename,
        content_type=stored_upload.content_type,
        stored_path=stored_upload.stored_path,
        size_bytes=stored_upload.size_bytes,
        uploaded_by=user_id,
    )
    try:
        document = await repository.create_commercial_document(session, document)
        await session.commit()
    except Exception:
        await session.rollback()
        delete_stored_file(stored_upload.stored_path)
        raise
    return document


async def list_commercial_documents(
    session: AsyncSession,
    proposal_id: int,
    *,
    user_id: int,
    limit: int = 100,
    offset: int = 0,
) -> list[ProposalCommercialDocument]:
    """List commercial PDFs attached to an owned proposal."""

    proposal = await get_proposal(session, proposal_id, user_id=user_id)
    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    documents = await repository.list_commercial_documents(
        session,
        proposal.id,
        limit=limit,
        offset=offset,
    )
    return list(documents)


async def get_commercial_document(
    session: AsyncSession,
    proposal_id: int,
    document_id: int,
    *,
    user_id: int,
) -> ProposalCommercialDocument:
    """Return one commercial PDF attached to an owned proposal."""

    proposal = await get_proposal(session, proposal_id, user_id=user_id)
    document = await repository.get_commercial_document(session, document_id)
    if document is None or document.proposal_id != proposal.id:
        raise NotFoundError(
            "Proposal commercial PDF not found",
            details={"proposal_id": proposal_id, "document_id": document_id},
        )
    return document


async def delete_commercial_document(
    session: AsyncSession,
    proposal_id: int,
    document_id: int,
    *,
    user_id: int,
) -> None:
    """Delete one commercial PDF attached to an owned proposal."""

    document = await get_commercial_document(
        session,
        proposal_id,
        document_id,
        user_id=user_id,
    )
    stored_path = document.stored_path
    try:
        await repository.delete_commercial_document(session, document)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    delete_stored_file(stored_path)


async def upload_document(
    session: AsyncSession,
    proposal_id: int,
    *,
    title: str,
    classification: ProposalDocumentClassification,
    upload: UploadFileLike,
    user_id: int,
    storage_root: str | Path | None = None,
) -> ProposalDocument:
    """Upload a cost, technical, or other document for an owned proposal."""

    proposal = await get_proposal(session, proposal_id, user_id=user_id)
    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    normalized_title = _normalize_required_text(title, field_name="title")
    stored_upload = await save_upload(
        upload,
        directory_parts=(
            f"proposal-{proposal.id}",
            "documents",
            classification.value.lower(),
        ),
        storage_root=storage_root,
    )
    document = ProposalDocument(
        proposal_id=proposal.id,
        title=normalized_title,
        classification=classification,
        original_filename=stored_upload.original_filename,
        content_type=stored_upload.content_type,
        stored_path=stored_upload.stored_path,
        size_bytes=stored_upload.size_bytes,
        uploaded_by=user_id,
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
    proposal_id: int,
    *,
    user_id: int,
    classification: ProposalDocumentClassification | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[ProposalDocument]:
    """List classified documents attached to an owned proposal."""

    proposal = await get_proposal(session, proposal_id, user_id=user_id)
    if proposal.id is None:
        raise InvalidOperationError("Proposal was not saved properly")
    documents = await repository.list_documents(
        session,
        proposal.id,
        classification=classification,
        limit=limit,
        offset=offset,
    )
    return list(documents)


async def get_document(
    session: AsyncSession,
    proposal_id: int,
    document_id: int,
    *,
    user_id: int,
) -> ProposalDocument:
    """Return one classified document attached to an owned proposal."""

    proposal = await get_proposal(session, proposal_id, user_id=user_id)
    document = await repository.get_document(session, document_id)
    if document is None or document.proposal_id != proposal.id:
        raise NotFoundError(
            "Proposal document not found",
            details={"proposal_id": proposal_id, "document_id": document_id},
        )
    return document


async def delete_document(
    session: AsyncSession,
    proposal_id: int,
    document_id: int,
    *,
    user_id: int,
) -> None:
    """Delete one classified document attached to an owned proposal."""

    document = await get_document(
        session,
        proposal_id,
        document_id,
        user_id=user_id,
    )
    stored_path = document.stored_path
    try:
        await repository.delete_document(session, document)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    delete_stored_file(stored_path)
