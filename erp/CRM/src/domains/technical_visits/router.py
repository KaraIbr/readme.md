"""Technical visits HTTP routers."""

from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from domains.leads import schemas as lead_schemas
from domains.permissions import service as permissions_service
from domains.technical_visits import schemas, service
from domains.technical_visits.models import (
    TechnicalVisitAttachmentKind,
    TechnicalVisitStatus,
)
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()
lead_router = APIRouter()
proposal_router = APIRouter()


def _owner_id(current_user: CurrentUser) -> int:
    owner_id = current_user.id
    assert owner_id is not None
    return owner_id


@lead_router.post(
    "/{lead_id}/technical-visit-requirement",
    response_model=lead_schemas.LeadRead,
)
async def set_lead_technical_visit_requirement(
    lead_id: int,
    payload: schemas.TechnicalVisitRequirementUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> lead_schemas.LeadRead:
    """Set whether an owned lead requires a technical visit."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.update",
    )
    lead = await service.set_lead_requirement(
        session,
        lead_id,
        requirement=payload.requirement,
        owner_id=_owner_id(current_user),
    )
    return lead_schemas.LeadRead.model_validate(lead)


@lead_router.post(
    "/{lead_id}/technical-visits",
    response_model=schemas.TechnicalVisitRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead_technical_visit(
    lead_id: int,
    payload: schemas.TechnicalVisitCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TechnicalVisitRead:
    """Create a technical visit for one owned lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.create",
    )
    if payload.assignees:
        await permissions_service.require_permission(
            session,
            _owner_id(current_user),
            "crm.technical_visits.assign",
        )
    visit = await service.create_visit(
        session,
        lead_id,
        payload,
        owner_id=_owner_id(current_user),
    )
    return schemas.TechnicalVisitRead.model_validate(visit)


@lead_router.get(
    "/{lead_id}/technical-visits",
    response_model=list[schemas.TechnicalVisitRead],
)
async def list_lead_technical_visits(
    lead_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    status_filter: Annotated[TechnicalVisitStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.TechnicalVisitRead]:
    """Return technical visits for one owned lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.read",
    )
    visits = await service.list_visits(
        session,
        owner_id=_owner_id(current_user),
        lead_id=lead_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return [schemas.TechnicalVisitRead.model_validate(visit) for visit in visits]


@router.get("/", response_model=list[schemas.TechnicalVisitRead])
async def list_technical_visits(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    lead_id: Annotated[int | None, Query(gt=0)] = None,
    status_filter: Annotated[TechnicalVisitStatus | None, Query(alias="status")] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.TechnicalVisitRead]:
    """Return technical visits across owned leads."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.read",
    )
    visits = await service.list_visits(
        session,
        owner_id=_owner_id(current_user),
        lead_id=lead_id,
        status=status_filter,
        limit=limit,
        offset=offset,
    )
    return [schemas.TechnicalVisitRead.model_validate(visit) for visit in visits]


@router.get("/{visit_id}", response_model=schemas.TechnicalVisitRead)
async def read_technical_visit(
    visit_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TechnicalVisitRead:
    """Return one owned technical visit."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.read",
    )
    visit = await service.get_visit(
        session,
        visit_id,
        owner_id=_owner_id(current_user),
    )
    return schemas.TechnicalVisitRead.model_validate(visit)


@router.patch("/{visit_id}", response_model=schemas.TechnicalVisitRead)
async def update_technical_visit(
    visit_id: int,
    payload: schemas.TechnicalVisitUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TechnicalVisitRead:
    """Update scheduling metadata for one owned technical visit."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.update",
    )
    if "assignees" in payload.model_fields_set:
        await permissions_service.require_permission(
            session,
            _owner_id(current_user),
            "crm.technical_visits.assign",
        )
    visit = await service.update_visit(
        session,
        visit_id,
        payload,
        owner_id=_owner_id(current_user),
    )
    return schemas.TechnicalVisitRead.model_validate(visit)


@router.post("/{visit_id}/complete", response_model=schemas.TechnicalVisitRead)
async def complete_technical_visit(
    visit_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TechnicalVisitRead:
    """Mark one owned technical visit completed."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.complete",
    )
    visit = await service.complete_visit(
        session,
        visit_id,
        owner_id=_owner_id(current_user),
    )
    return schemas.TechnicalVisitRead.model_validate(visit)


@router.post("/{visit_id}/cancel", response_model=schemas.TechnicalVisitRead)
async def cancel_technical_visit(
    visit_id: int,
    payload: schemas.TechnicalVisitCancel,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TechnicalVisitRead:
    """Cancel one owned technical visit."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.cancel",
    )
    visit = await service.cancel_visit(
        session,
        visit_id,
        payload,
        owner_id=_owner_id(current_user),
    )
    return schemas.TechnicalVisitRead.model_validate(visit)


@router.post(
    "/{visit_id}/attachments",
    response_model=schemas.TechnicalVisitAttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_technical_visit_attachment(
    visit_id: int,
    title: Annotated[str, Form(min_length=1, max_length=255)],
    file_kind: Annotated[TechnicalVisitAttachmentKind, Form()],
    file: Annotated[UploadFile, File()],
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TechnicalVisitAttachmentRead:
    """Upload evidence for one owned technical visit."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.attachments.create",
    )
    attachment = await service.upload_attachment(
        session,
        visit_id,
        title=title,
        file_kind=file_kind,
        upload=file,
        owner_id=_owner_id(current_user),
    )
    return schemas.TechnicalVisitAttachmentRead.model_validate(attachment)


@router.get(
    "/{visit_id}/attachments",
    response_model=list[schemas.TechnicalVisitAttachmentRead],
)
async def list_technical_visit_attachments(
    visit_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.TechnicalVisitAttachmentRead]:
    """Return evidence attachments for one owned technical visit."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.attachments.read",
    )
    attachments = await service.list_attachments(
        session,
        visit_id,
        owner_id=_owner_id(current_user),
        limit=limit,
        offset=offset,
    )
    return [
        schemas.TechnicalVisitAttachmentRead.model_validate(attachment)
        for attachment in attachments
    ]


@router.get(
    "/{visit_id}/attachments/{attachment_id}",
    response_model=schemas.TechnicalVisitAttachmentRead,
)
async def read_technical_visit_attachment(
    visit_id: int,
    attachment_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.TechnicalVisitAttachmentRead:
    """Return metadata for one technical visit attachment."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.attachments.read",
    )
    attachment = await service.get_attachment(
        session,
        visit_id,
        attachment_id,
        owner_id=_owner_id(current_user),
    )
    return schemas.TechnicalVisitAttachmentRead.model_validate(attachment)


@router.get("/{visit_id}/attachments/{attachment_id}/download")
async def download_technical_visit_attachment(
    visit_id: int,
    attachment_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FileResponse:
    """Download one technical visit attachment."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.attachments.read",
    )
    attachment = await service.get_attachment(
        session,
        visit_id,
        attachment_id,
        owner_id=_owner_id(current_user),
    )
    return FileResponse(
        service.stored_file_path(attachment.stored_path),
        media_type=attachment.content_type or "application/octet-stream",
        filename=attachment.original_filename,
    )


@router.delete(
    "/{visit_id}/attachments/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_technical_visit_attachment(
    visit_id: int,
    attachment_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Delete one technical visit attachment."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.technical_visits.attachments.delete",
    )
    await service.delete_attachment(
        session,
        visit_id,
        attachment_id,
        owner_id=_owner_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@proposal_router.post(
    "/{proposal_id}/technical-visits",
    response_model=schemas.ProposalTechnicalVisitRead,
    status_code=status.HTTP_201_CREATED,
)
async def link_proposal_technical_visit(
    proposal_id: int,
    payload: schemas.ProposalTechnicalVisitCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalTechnicalVisitRead:
    """Link an owned proposal to technical visit evidence."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.proposals.technical_visits.link",
    )
    link = await service.link_proposal_visit(
        session,
        proposal_id,
        payload,
        owner_id=_owner_id(current_user),
    )
    return schemas.ProposalTechnicalVisitRead.model_validate(link)


@proposal_router.get(
    "/{proposal_id}/technical-visits",
    response_model=list[schemas.ProposalTechnicalVisitRead],
)
async def list_proposal_technical_visit_links(
    proposal_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.ProposalTechnicalVisitRead]:
    """Return technical visit evidence links for one owned proposal."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.proposals.technical_visits.read",
    )
    links = await service.list_proposal_visit_links(
        session,
        proposal_id,
        owner_id=_owner_id(current_user),
        limit=limit,
        offset=offset,
    )
    return [schemas.ProposalTechnicalVisitRead.model_validate(link) for link in links]


@proposal_router.delete(
    "/{proposal_id}/technical-visits/{technical_visit_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unlink_proposal_technical_visit(
    proposal_id: int,
    technical_visit_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Remove a proposal-to-technical-visit evidence link."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.proposals.technical_visits.unlink",
    )
    await service.unlink_proposal_visit(
        session,
        proposal_id,
        technical_visit_id,
        owner_id=_owner_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
