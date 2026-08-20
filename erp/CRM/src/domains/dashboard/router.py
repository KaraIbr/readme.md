from typing import Annotated

from api.dependencies import CurrentUser, get_db_session
from domains.dashboard import service
from domains.permissions import service as permissions_service
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict:
    owner_id = current_user.id
    assert owner_id is not None
    await permissions_service.require_permission(
        session,
        owner_id,
        "crm.dashboard.read",
    )
    role = await permissions_service.get_user_crm_role(session, owner_id)
    return await service.get_stats(session, owner_id, role=role)
