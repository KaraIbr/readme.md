"""LangGraph runtime graph for the CRM assistant."""

from collections.abc import Sequence

from agent.prompts import build_system_prompt
from agent.skills.registry import select_skills
from agent.state import AgentState
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.runtime import Runtime


def _latest_user_text(state: AgentState) -> str:
    for message in reversed(state.get("messages", [])):
        if message.type == "human":
            content = message.content
            if isinstance(content, str):
                return content
            return str(content)
    return ""


def build_agent_graph(
    *,
    model: BaseChatModel,
    tools: Sequence[BaseTool],
):
    """Compile a LangGraph state machine for one agent request."""

    bound_model = model.bind_tools(list(tools))

    async def select_runtime_skills(state: AgentState) -> dict[str, object]:
        selected = select_skills(_latest_user_text(state))
        return {
            "selected_skills": [skill.name for skill in selected],
            "skill_instructions": build_system_prompt(selected),
        }

    async def call_model(
        state: AgentState,
        _: Runtime | None = None,
    ) -> dict[str, object]:
        prompt = state.get("skill_instructions") or build_system_prompt(())
        response = await bound_model.ainvoke(
            [SystemMessage(content=prompt), *state.get("messages", [])]
        )
        return {"messages": [response]}

    graph = StateGraph(AgentState)
    graph.add_node("select_skills", select_runtime_skills)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(list(tools)))

    graph.add_edge(START, "select_skills")
    graph.add_edge("select_skills", "agent")
    graph.add_conditional_edges(
        "agent",
        tools_condition,
        {"tools": "tools", END: END},
    )
    graph.add_edge("tools", "agent")

    return graph.compile()
