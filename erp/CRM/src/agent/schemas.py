"""Runtime agent API schemas."""

from enum import StrEnum

from pydantic import BaseModel, Field


class AgentMessageRole(StrEnum):
    """Supported chat history roles."""

    USER = "user"
    ASSISTANT = "assistant"


class AgentMessage(BaseModel):
    """One prior chat message supplied by the client."""

    role: AgentMessageRole
    content: str = Field(min_length=1, max_length=8000)


class AgentChatRequest(BaseModel):
    """Request body for the CRM runtime assistant."""

    message: str = Field(min_length=1, max_length=8000)
    history: list[AgentMessage] = Field(default_factory=list, max_length=20)


class AgentEvidence(BaseModel):
    """Compact reference to CRM data used by the assistant."""

    source: str
    record_type: str | None = None
    record_id: int | None = None
    display_name: str | None = None


class AgentChatResponse(BaseModel):
    """Response returned by the CRM runtime assistant."""

    answer: str
    selected_skills: list[str] = Field(default_factory=list)
    tool_calls: list[str] = Field(default_factory=list)
    evidence: list[AgentEvidence] = Field(default_factory=list)
    needs_confirmation: bool = False
