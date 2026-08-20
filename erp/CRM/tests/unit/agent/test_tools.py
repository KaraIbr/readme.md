import json

from agent.tools.factory import build_tools

from unit.agent.helpers import create_crm_fixture, create_owner


def _tool_by_name(tools, name: str):  # noqa: ANN001, ANN201
    return next(tool for tool in tools if tool.name == name)


async def test_search_tools_return_owner_scoped_structured_records(session) -> None:
    owner = await create_owner(session)
    other = await create_owner(session, "other@example.com")
    assert owner.id is not None
    assert other.id is not None
    _, _, proposal = await create_crm_fixture(session, owner.id)
    await create_crm_fixture(session, other.id)

    tools = build_tools(session, owner.id)
    search_contacts = _tool_by_name(tools, "search_contacts")
    search_proposals = _tool_by_name(tools, "search_proposals")

    contacts_payload = json.loads(await search_contacts.ainvoke({"query": "Acme", "limit": 10}))
    proposals_payload = json.loads(await search_proposals.ainvoke({"query": "Acme", "limit": 10}))

    assert contacts_payload["count"] == 1
    assert contacts_payload["records"][0]["display_name"] == "Acme Manufacturing"
    assert proposals_payload["count"] == 1
    assert proposals_payload["records"][0]["id"] == proposal.id
    assert proposals_payload["records"][0]["pv_system"]["inverter_model"] == "INV-8K"
    assert proposals_payload["records"][0]["pv_system"]["cost_watt"] == "21.1765"
    assert proposals_payload["records"][0]["pv_system"]["price_watt"] == "29.4118"


async def test_calculate_proposal_metrics_uses_python_arithmetic(session) -> None:
    owner = await create_owner(session)
    assert owner.id is not None
    _, _, proposal = await create_crm_fixture(session, owner.id)

    calculate_metrics = _tool_by_name(
        build_tools(session, owner.id),
        "calculate_proposal_metrics",
    )
    payload = json.loads(await calculate_metrics.ainvoke({"proposal_id": proposal.id}))

    assert payload["metrics"]["proposal_id"] == proposal.id
    assert payload["metrics"]["cost_watt"] == "21.1765"
    assert payload["metrics"]["price_watt"] == "29.4118"
    assert payload["metrics"]["price_per_kw_formula"] == "250000.00 / 8.5 kW"
    assert payload["metrics"]["price_per_kw"] == "29411.76"
    assert payload["metrics"]["gross_margin"] == "70000.00"
    assert payload["metrics"]["gross_margin_percent"] == "28.0000"
