"""LangGraph state for the runtime CRM assistant."""

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict, total=False):
    """State shared by graph nodes."""

    messages: Annotated[list[BaseMessage], add_messages]
    selected_skills: list[str]
    skill_instructions: str
