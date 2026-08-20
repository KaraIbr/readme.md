"""HTTP router for the runtime CRM assistant."""

from typing import Annotated

from agent import schemas, service
from agent.providers.base import LLMProvider
from agent.providers.factory import get_llm_provider
from api.dependencies import CurrentUser, get_db_session
from domains.permissions import service as permissions_service
from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.post("/chat", response_model=schemas.AgentChatResponse)
async def chat(
    payload: schemas.AgentChatRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    provider: Annotated[LLMProvider, Depends(get_llm_provider)],
) -> schemas.AgentChatResponse:
    """Run one authenticated CRM assistant chat turn."""

    user_id = current_user.id
    assert user_id is not None
    await permissions_service.require_permission(session, user_id, "crm.agent.chat")
    return await service.chat(
        session,
        payload,
        current_user=current_user,
        provider=provider,
    )
