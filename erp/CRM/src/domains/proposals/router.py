"""Proposals HTTP router."""

from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from domains.permissions import service as permissions_service
from domains.proposals import schemas, service
from domains.proposals.models import ProposalDocumentClassification, ProposalStage
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


def _user_id(current_user: CurrentUser) -> int:
    user_id = current_user.id
    assert user_id is not None
    return user_id


@router.post("/", response_model=schemas.ProposalRead, status_code=status.HTTP_201_CREATED)
async def create_proposal(
    payload: schemas.ProposalCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalRead:
    """Create a proposal variant for an owned lead."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.create",
    )
    proposal = await service.create_proposal(
        session,
        payload,
        created_by=_user_id(current_user),
        enforce_price_permissions=True,
    )
    return schemas.ProposalRead.model_validate(proposal)


@router.get("/", response_model=list[schemas.ProposalRead])
async def list_proposals(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    lead_id: Annotated[int | None, Query(gt=0)] = None,
    stage: ProposalStage | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.ProposalRead]:
    """Return proposals created by the authenticated user."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.read",
    )
    proposals = await service.list_proposals(
        session,
        user_id=_user_id(current_user),
        lead_id=lead_id,
        stage=stage,
        limit=limit,
        offset=offset,
    )
    return [schemas.ProposalRead.model_validate(proposal) for proposal in proposals]


@router.get("/{proposal_id}", response_model=schemas.ProposalRead)
async def read_proposal(
    proposal_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalRead:
    """Return one owned proposal."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.read",
    )
    proposal = await service.get_proposal(
        session,
        proposal_id,
        user_id=_user_id(current_user),
    )
    return schemas.ProposalRead.model_validate(proposal)


@router.post(
    "/{proposal_id}/commercial-pdf",
    response_model=schemas.ProposalCommercialDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_proposal_commercial_pdf(
    proposal_id: int,
    title: Annotated[str, Form(min_length=1, max_length=255)],
    file: Annotated[UploadFile, File()],
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalCommercialDocumentRead:
    """Upload the customer-facing commercial proposal PDF."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.commercial_documents.create",
    )
    document = await service.upload_commercial_document(
        session,
        proposal_id,
        title=title,
        upload=file,
        user_id=_user_id(current_user),
    )
    return schemas.ProposalCommercialDocumentRead.model_validate(document)


@router.get(
    "/{proposal_id}/commercial-pdf",
    response_model=list[schemas.ProposalCommercialDocumentRead],
)
async def list_proposal_commercial_pdfs(
    proposal_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.ProposalCommercialDocumentRead]:
    """Return commercial PDFs uploaded for one owned proposal."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.commercial_documents.read",
    )
    documents = await service.list_commercial_documents(
        session,
        proposal_id,
        user_id=_user_id(current_user),
        limit=limit,
        offset=offset,
    )
    return [
        schemas.ProposalCommercialDocumentRead.model_validate(document) for document in documents
    ]


@router.get(
    "/{proposal_id}/commercial-pdf/{document_id}",
    response_model=schemas.ProposalCommercialDocumentRead,
)
async def read_proposal_commercial_pdf(
    proposal_id: int,
    document_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalCommercialDocumentRead:
    """Return metadata for one uploaded commercial proposal PDF."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.commercial_documents.read",
    )
    document = await service.get_commercial_document(
        session,
        proposal_id,
        document_id,
        user_id=_user_id(current_user),
    )
    return schemas.ProposalCommercialDocumentRead.model_validate(document)


@router.get("/{proposal_id}/commercial-pdf/{document_id}/download")
async def download_proposal_commercial_pdf(
    proposal_id: int,
    document_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FileResponse:
    """Download one uploaded commercial proposal PDF."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.commercial_documents.read",
    )
    document = await service.get_commercial_document(
        session,
        proposal_id,
        document_id,
        user_id=_user_id(current_user),
    )
    return FileResponse(
        service.stored_file_path(document.stored_path),
        media_type=document.content_type or "application/pdf",
        filename=document.original_filename,
    )


@router.delete(
    "/{proposal_id}/commercial-pdf/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_proposal_commercial_pdf(
    proposal_id: int,
    document_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Delete one uploaded commercial proposal PDF."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.commercial_documents.delete",
    )
    await service.delete_commercial_document(
        session,
        proposal_id,
        document_id,
        user_id=_user_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{proposal_id}/documents",
    response_model=schemas.ProposalDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_proposal_document(
    proposal_id: int,
    title: Annotated[str, Form(min_length=1, max_length=255)],
    classification: Annotated[ProposalDocumentClassification, Form()],
    file: Annotated[UploadFile, File()],
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalDocumentRead:
    """Upload a cost, technical, or other internal proposal document."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.documents.create",
    )
    document = await service.upload_document(
        session,
        proposal_id,
        title=title,
        classification=classification,
        upload=file,
        user_id=_user_id(current_user),
    )
    return schemas.ProposalDocumentRead.model_validate(document)


@router.get("/{proposal_id}/documents", response_model=list[schemas.ProposalDocumentRead])
async def list_proposal_documents(
    proposal_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    classification: ProposalDocumentClassification | None = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.ProposalDocumentRead]:
    """Return classified documents uploaded for one owned proposal."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.documents.read",
    )
    documents = await service.list_documents(
        session,
        proposal_id,
        user_id=_user_id(current_user),
        classification=classification,
        limit=limit,
        offset=offset,
    )
    return [schemas.ProposalDocumentRead.model_validate(document) for document in documents]


@router.get(
    "/{proposal_id}/documents/{document_id}",
    response_model=schemas.ProposalDocumentRead,
)
async def read_proposal_document(
    proposal_id: int,
    document_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalDocumentRead:
    """Return metadata for one uploaded proposal document."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.documents.read",
    )
    document = await service.get_document(
        session,
        proposal_id,
        document_id,
        user_id=_user_id(current_user),
    )
    return schemas.ProposalDocumentRead.model_validate(document)


@router.get("/{proposal_id}/documents/{document_id}/download")
async def download_proposal_document(
    proposal_id: int,
    document_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FileResponse:
    """Download one uploaded proposal document."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.documents.read",
    )
    document = await service.get_document(
        session,
        proposal_id,
        document_id,
        user_id=_user_id(current_user),
    )
    return FileResponse(
        service.stored_file_path(document.stored_path),
        media_type=document.content_type or "application/octet-stream",
        filename=document.original_filename,
    )


@router.delete(
    "/{proposal_id}/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_proposal_document(
    proposal_id: int,
    document_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Delete one uploaded proposal document."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.documents.delete",
    )
    await service.delete_document(
        session,
        proposal_id,
        document_id,
        user_id=_user_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{proposal_id}", response_model=schemas.ProposalRead)
async def update_proposal(
    proposal_id: int,
    payload: schemas.ProposalUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalRead:
    """Partially update one owned non-terminal proposal."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.update",
    )
    proposal = await service.update_proposal(
        session,
        proposal_id,
        payload,
        user_id=_user_id(current_user),
        enforce_price_permissions=True,
    )
    return schemas.ProposalRead.model_validate(proposal)


@router.post("/{proposal_id}/stage", response_model=schemas.ProposalRead)
async def move_proposal_stage(
    proposal_id: int,
    payload: schemas.ProposalStageChange,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalRead:
    """Move one owned proposal through a non-terminal stage transition."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.stage.update",
    )
    proposal = await service.move_to_stage(
        session,
        proposal_id,
        stage=payload.stage,
        user_id=_user_id(current_user),
    )
    return schemas.ProposalRead.model_validate(proposal)


@router.post("/{proposal_id}/won", response_model=schemas.ProposalRead)
async def mark_proposal_won(
    proposal_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalRead:
    """Mark one owned proposal as won."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.mark_won",
    )
    proposal = await service.mark_won(
        proposal_id,
        _user_id(current_user),
        session,
    )
    return schemas.ProposalRead.model_validate(proposal)


@router.post("/{proposal_id}/lost", response_model=schemas.ProposalRead)
async def mark_proposal_lost(
    proposal_id: int,
    payload: schemas.ProposalLost,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ProposalRead:
    """Mark one owned proposal as lost."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.mark_lost",
    )
    proposal = await service.mark_lost(
        session,
        proposal_id,
        user_id=_user_id(current_user),
        loss_reason=payload.loss_reason,
    )
    return schemas.ProposalRead.model_validate(proposal)


@router.delete("/{proposal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proposal(
    proposal_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Delete one owned non-terminal proposal."""

    await permissions_service.require_permission(
        session,
        _user_id(current_user),
        "crm.proposals.delete",
    )
    await service.delete_proposal(
        session,
        proposal_id,
        user_id=_user_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
