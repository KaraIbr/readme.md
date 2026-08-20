"""Leads HTTP router."""

from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from domains.leads import schemas, service
from domains.leads.models import LeadStage
from domains.permissions import service as permissions_service
from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


def _owner_id(current_user: CurrentUser) -> int:
    owner_id = current_user.id
    assert owner_id is not None
    return owner_id


@router.post("/", response_model=schemas.LeadRead, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: schemas.LeadCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadRead:
    """Create a lead owned by the authenticated user."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.create",
    )
    lead = await service.create_lead(
        session,
        payload,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadRead.model_validate(lead)


@router.get("/", response_model=list[schemas.LeadRead])
async def list_leads(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    contact_id: Annotated[int | None, Query(gt=0)] = None,
    stage: LeadStage | None = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.LeadRead]:
    """Return leads owned by the authenticated user."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.read",
    )
    if q:
        leads = await service.search_leads(
            session,
            owner_id=_owner_id(current_user),
            query=q,
            limit=limit,
        )
    else:
        leads = await service.list_leads(
            session,
            owner_id=_owner_id(current_user),
            contact_id=contact_id,
            stage=stage,
            limit=limit,
            offset=offset,
        )
    return [schemas.LeadRead.model_validate(lead) for lead in leads]


@router.get("/{lead_id}", response_model=schemas.LeadRead)
async def read_lead(
    lead_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadRead:
    """Return one owned lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.read",
    )
    lead = await service.get_lead(
        session,
        lead_id,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadRead.model_validate(lead)


@router.post(
    "/{lead_id}/documents",
    response_model=schemas.LeadDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_lead_document(
    lead_id: int,
    title: Annotated[str, Form(min_length=1, max_length=255)],
    file: Annotated[UploadFile, File()],
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadDocumentRead:
    """Upload a general project document for one owned lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.documents.create",
    )
    document = await service.upload_document(
        session,
        lead_id,
        title=title,
        upload=file,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadDocumentRead.model_validate(document)


@router.get("/{lead_id}/documents", response_model=list[schemas.LeadDocumentRead])
async def list_lead_documents(
    lead_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.LeadDocumentRead]:
    """Return general documents uploaded for one owned lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.documents.read",
    )
    documents = await service.list_documents(
        session,
        lead_id,
        owner_id=_owner_id(current_user),
        limit=limit,
        offset=offset,
    )
    return [schemas.LeadDocumentRead.model_validate(document) for document in documents]


@router.get("/{lead_id}/documents/{document_id}", response_model=schemas.LeadDocumentRead)
async def read_lead_document(
    lead_id: int,
    document_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadDocumentRead:
    """Return metadata for one uploaded lead document."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.documents.read",
    )
    document = await service.get_document(
        session,
        lead_id,
        document_id,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadDocumentRead.model_validate(document)


@router.get("/{lead_id}/documents/{document_id}/download")
async def download_lead_document(
    lead_id: int,
    document_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FileResponse:
    """Download one uploaded lead document."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.documents.read",
    )
    document = await service.get_document(
        session,
        lead_id,
        document_id,
        owner_id=_owner_id(current_user),
    )
    return FileResponse(
        service.stored_file_path(document.stored_path),
        media_type=document.content_type or "application/octet-stream",
        filename=document.original_filename,
    )


@router.delete("/{lead_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead_document(
    lead_id: int,
    document_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Delete one uploaded lead document."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.documents.delete",
    )
    await service.delete_document(
        session,
        lead_id,
        document_id,
        owner_id=_owner_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{lead_id}/electricity-bills",
    response_model=schemas.LeadElectricityBillRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_lead_electricity_bill(
    lead_id: int,
    title: Annotated[str, Form(min_length=1, max_length=255)],
    file: Annotated[UploadFile, File()],
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadElectricityBillRead:
    """Upload an electricity bill for one owned lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.electricity_bills.create",
    )
    bill = await service.upload_electricity_bill(
        session,
        lead_id,
        title=title,
        upload=file,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadElectricityBillRead.model_validate(bill)


@router.get(
    "/{lead_id}/electricity-bills",
    response_model=list[schemas.LeadElectricityBillRead],
)
async def list_lead_electricity_bills(
    lead_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.LeadElectricityBillRead]:
    """Return electricity bills uploaded for one owned lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.electricity_bills.read",
    )
    bills = await service.list_electricity_bills(
        session,
        lead_id,
        owner_id=_owner_id(current_user),
        limit=limit,
        offset=offset,
    )
    return [schemas.LeadElectricityBillRead.model_validate(bill) for bill in bills]


@router.get(
    "/{lead_id}/electricity-bills/{bill_id}",
    response_model=schemas.LeadElectricityBillRead,
)
async def read_lead_electricity_bill(
    lead_id: int,
    bill_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadElectricityBillRead:
    """Return metadata for one uploaded electricity bill."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.electricity_bills.read",
    )
    bill = await service.get_electricity_bill(
        session,
        lead_id,
        bill_id,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadElectricityBillRead.model_validate(bill)


@router.get("/{lead_id}/electricity-bills/{bill_id}/download")
async def download_lead_electricity_bill(
    lead_id: int,
    bill_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> FileResponse:
    """Download one uploaded electricity bill."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.electricity_bills.read",
    )
    bill = await service.get_electricity_bill(
        session,
        lead_id,
        bill_id,
        owner_id=_owner_id(current_user),
    )
    return FileResponse(
        service.stored_file_path(bill.stored_path),
        media_type=bill.content_type or "application/octet-stream",
        filename=bill.original_filename,
    )


@router.delete(
    "/{lead_id}/electricity-bills/{bill_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lead_electricity_bill(
    lead_id: int,
    bill_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Delete one uploaded electricity bill."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.electricity_bills.delete",
    )
    await service.delete_electricity_bill(
        session,
        lead_id,
        bill_id,
        owner_id=_owner_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{lead_id}/interactions",
    response_model=schemas.LeadInteractionRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_lead_interaction(
    lead_id: int,
    payload: schemas.LeadInteractionCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadInteractionRead:
    """Document a sales interaction or negotiation for one owned lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.interactions.create",
    )
    interaction = await service.create_interaction(
        session,
        lead_id,
        payload,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadInteractionRead.model_validate(interaction)


@router.get(
    "/{lead_id}/interactions",
    response_model=list[schemas.LeadInteractionRead],
)
async def list_lead_interactions(
    lead_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.LeadInteractionRead]:
    """Return sales interactions documented for one owned lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.interactions.read",
    )
    interactions = await service.list_interactions(
        session,
        lead_id,
        owner_id=_owner_id(current_user),
        limit=limit,
        offset=offset,
    )
    return [schemas.LeadInteractionRead.model_validate(interaction) for interaction in interactions]


@router.get(
    "/{lead_id}/interactions/{interaction_id}",
    response_model=schemas.LeadInteractionRead,
)
async def read_lead_interaction(
    lead_id: int,
    interaction_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadInteractionRead:
    """Return one documented lead interaction."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.interactions.read",
    )
    interaction = await service.get_interaction(
        session,
        lead_id,
        interaction_id,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadInteractionRead.model_validate(interaction)


@router.patch(
    "/{lead_id}/interactions/{interaction_id}",
    response_model=schemas.LeadInteractionRead,
)
async def update_lead_interaction(
    lead_id: int,
    interaction_id: int,
    payload: schemas.LeadInteractionUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadInteractionRead:
    """Partially update one documented lead interaction."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.interactions.update",
    )
    interaction = await service.update_interaction(
        session,
        lead_id,
        interaction_id,
        payload,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadInteractionRead.model_validate(interaction)


@router.delete(
    "/{lead_id}/interactions/{interaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_lead_interaction(
    lead_id: int,
    interaction_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Delete one documented lead interaction."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.interactions.delete",
    )
    await service.delete_interaction(
        session,
        lead_id,
        interaction_id,
        owner_id=_owner_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{lead_id}", response_model=schemas.LeadRead)
async def update_lead(
    lead_id: int,
    payload: schemas.LeadUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadRead:
    """Partially update one owned open lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.update",
    )
    lead = await service.update_lead(
        session,
        lead_id,
        payload,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadRead.model_validate(lead)


@router.post("/{lead_id}/stage", response_model=schemas.LeadRead)
async def move_lead_stage(
    lead_id: int,
    payload: schemas.LeadStageChange,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadRead:
    """Move one owned lead through an open-stage transition."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.stage.update",
    )
    lead = await service.move_to_stage(
        session,
        lead_id,
        stage=payload.stage,
        owner_id=_owner_id(current_user),
    )
    return schemas.LeadRead.model_validate(lead)


@router.post("/{lead_id}/close", response_model=schemas.LeadRead)
async def close_lead(
    lead_id: int,
    payload: schemas.LeadClose,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.LeadRead:
    """Close one owned lead as manually abandoned or lost."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.close",
    )
    lead = await service.close(
        session,
        lead_id,
        outcome=payload.outcome,
        by=_owner_id(current_user),
        notes=payload.notes,
    )
    return schemas.LeadRead.model_validate(lead)


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(
    lead_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Delete one owned open lead."""

    await permissions_service.require_permission(
        session,
        _owner_id(current_user),
        "crm.leads.delete",
    )
    await service.delete_lead(
        session,
        lead_id,
        owner_id=_owner_id(current_user),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
