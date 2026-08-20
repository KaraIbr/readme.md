from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from core.exceptions import InvalidOperationError
from domains.contacts import schemas, service
from domains.contacts.models import ContactType
from domains.permissions import service as permissions_service
from fastapi import APIRouter, Depends, Query, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.post("/", response_model=schemas.ContactRead, status_code=status.HTTP_201_CREATED)
async def create_company(
    payload: schemas.CompanyCreate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ContactRead:
    """Create a company contact owned by the authenticated user."""

    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.contacts.create",
    )
    contact = await service.create_contact(
        session,
        payload,
        owner_id=owner_id,
    )
    return schemas.ContactRead.model_validate(contact)


@router.get("/", response_model=list[schemas.ContactRead])
async def list_companies(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    q: Annotated[str | None, Query(max_length=200)] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[schemas.ContactRead]:
    """Return company contacts owned by the authenticated user."""

    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.contacts.read",
    )
    if q:
        contacts = await service.search_contacts(
            session,
            owner_id=owner_id,
            query=q,
            contact_type=ContactType.COMPANY,
            limit=limit,
        )
    else:
        contacts = await service.list_contacts(
            session,
            owner_id=owner_id,
            contact_type=ContactType.COMPANY,
            limit=limit,
            offset=offset,
        )
    return [schemas.ContactRead.model_validate(contact) for contact in contacts]


@router.get("/{contact_id}", response_model=schemas.ContactRead)
async def read_company(
    contact_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ContactRead:
    """Return one owned company contact."""

    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.contacts.read",
    )
    contact = await service.get_contact(
        session,
        contact_id,
        owner_id=owner_id,
    )
    if contact.type != ContactType.COMPANY:
        raise InvalidOperationError("Contact is not a company")
    return schemas.ContactRead.model_validate(contact)


@router.patch("/{contact_id}", response_model=schemas.ContactRead)
async def update_company(
    contact_id: int,
    payload: schemas.ContactUpdate,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.ContactRead:
    """Partially update one owned company contact."""

    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.contacts.update",
    )
    contact = await service.update_contact(
        session,
        contact_id,
        payload,
        owner_id=owner_id,
    )
    return schemas.ContactRead.model_validate(contact)


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    contact_id: int,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    """Delete one owned company contact."""

    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.contacts.delete",
    )
    await service.delete_contact(
        session,
        contact_id,
        owner_id=owner_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
