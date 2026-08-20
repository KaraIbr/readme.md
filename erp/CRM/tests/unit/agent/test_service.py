from agent.schemas import AgentChatRequest
from agent.service import chat
from langchain_core.messages import AIMessage

from unit.agent.helpers import FakeProvider, create_crm_fixture, create_owner


async def test_chat_runs_graph_tools_and_returns_evidence(session) -> None:
    owner = await create_owner(session)
    assert owner.id is not None
    _, _, proposal = await create_crm_fixture(session, owner.id)
    provider = FakeProvider(
        [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "get_proposal",
                        "args": {"proposal_id": proposal.id},
                        "id": "call_get_proposal",
                    }
                ],
            ),
            AIMessage(
                content=(
                    "La propuesta Acme technical option incluye el inversor INV-8K "
                    "y una capacidad de 8.5 kW."
                )
            ),
        ]
    )

    response = await chat(
        session,
        AgentChatRequest(message="Qué inversor incluye la propuesta de Acme?"),
        current_user=owner,
        provider=provider,
    )

    assert "INV-8K" in response.answer
    assert response.selected_skills == [
        "crm-entity-resolution",
        "crm-proposal-qa",
    ]
    assert response.tool_calls == ["get_proposal"]
    assert any(item.record_id == proposal.id for item in response.evidence)


async def test_chat_flattens_responses_api_text_blocks(session) -> None:
    owner = await create_owner(session)
    assert owner.id is not None
    provider = FakeProvider(
        [
            AIMessage(
                content=[
                    {
                        "type": "text",
                        "text": "Respuesta limpia desde Responses API.",
                    }
                ]
            ),
        ]
    )

    response = await chat(
        session,
        AgentChatRequest(message="Hola"),
        current_user=owner,
        provider=provider,
    )

    assert response.answer == "Respuesta limpia desde Responses API."
