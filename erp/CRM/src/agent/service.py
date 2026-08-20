"""Runtime agent service boundary."""

import json
from typing import Any

from agent.graph import build_agent_graph
from agent.providers.base import LLMProvider
from agent.providers.factory import get_llm_provider
from agent.schemas import (
    AgentChatRequest,
    AgentChatResponse,
    AgentEvidence,
    AgentMessageRole,
)
from agent.tools.factory import build_tools
from domains.users.models import User
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from sqlmodel.ext.asyncio.session import AsyncSession


def _history_to_messages(request: AgentChatRequest) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for item in request.history:
        if item.role == AgentMessageRole.USER:
            messages.append(HumanMessage(content=item.content))
        else:
            messages.append(AIMessage(content=item.content))
    messages.append(HumanMessage(content=request.message))
    return messages


def _message_text(message: BaseMessage) -> str:
    content = message.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                text_parts.append(part)
            elif isinstance(part, dict) and isinstance(part.get("text"), str):
                text_parts.append(part["text"])
        if text_parts:
            return "\n".join(text_parts)
    return json.dumps(content, ensure_ascii=False)


def _last_answer(messages: list[BaseMessage]) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage) and not message.tool_calls:
            return _message_text(message)
    return "No pude generar una respuesta final con la información disponible."


def _tool_calls(messages: list[BaseMessage]) -> list[str]:
    calls: list[str] = []
    for message in messages:
        if isinstance(message, AIMessage):
            calls.extend(call["name"] for call in message.tool_calls)
    return calls


def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    records: list[dict[str, Any]] = []
    record = payload.get("record")
    if isinstance(record, dict):
        records.append(record)
    for key in ("records", "metrics"):
        value = payload.get(key)
        if isinstance(value, list):
            records.extend(item for item in value if isinstance(item, dict))
        elif isinstance(value, dict):
            records.append(value)
    metrics = payload.get("metrics")
    if isinstance(metrics, dict):
        records.append(metrics)
    return records


def _evidence_from_tools(messages: list[BaseMessage]) -> list[AgentEvidence]:
    evidence: list[AgentEvidence] = []
    seen: set[tuple[str, str | None, int | None, str | None]] = set()
    for message in messages:
        if not isinstance(message, ToolMessage):
            continue
        try:
            payload = json.loads(_message_text(message))
        except json.JSONDecodeError:
            continue
        for record in _extract_records(payload):
            record_type = record.get("record_type")
            record_id = record.get("id") or record.get("proposal_id")
            display_name = record.get("display_name") or record.get("proposal_name")
            item = AgentEvidence(
                source=payload.get("tool") or message.name or "tool",
                record_type=record_type if isinstance(record_type, str) else None,
                record_id=record_id if isinstance(record_id, int) else None,
                display_name=display_name if isinstance(display_name, str) else None,
            )
            key = (item.source, item.record_type, item.record_id, item.display_name)
            if key not in seen:
                evidence.append(item)
                seen.add(key)
    return evidence


async def chat(
    session: AsyncSession,
    request: AgentChatRequest,
    *,
    current_user: User,
    provider: LLMProvider | None = None,
) -> AgentChatResponse:
    """Run one CRM assistant chat turn."""

    user_id = current_user.id
    assert user_id is not None

    llm_provider = provider or get_llm_provider()
    tools = build_tools(session, user_id)
    graph = build_agent_graph(model=llm_provider.chat_model(), tools=tools)
    result = await graph.ainvoke(
        {"messages": _history_to_messages(request)},
        config={"recursion_limit": 12},
    )
    messages = result.get("messages", [])
    return AgentChatResponse(
        answer=_last_answer(messages),
        selected_skills=list(result.get("selected_skills", [])),
        tool_calls=_tool_calls(messages),
        evidence=_evidence_from_tools(messages),
    )
