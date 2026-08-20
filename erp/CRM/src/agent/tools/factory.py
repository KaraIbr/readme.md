"""Create LangChain tools for one authenticated agent request."""

from collections.abc import Sequence
from typing import Any

from agent.tools.contacts import (
    GetContactInput,
    SearchContactsInput,
    make_contact_tool_functions,
)
from agent.tools.leads import (
    GetLeadInput,
    ListLeadsForContactInput,
    SearchLeadsInput,
    make_lead_tool_functions,
)
from agent.tools.pipeline import (
    ListStageTransitionsInput,
    PipelineSummaryInput,
    make_pipeline_tool_functions,
)
from agent.tools.proposals import (
    CompareProposalsInput,
    GetProposalInput,
    ListProposalsForLeadInput,
    SearchProposalsInput,
    make_proposal_tool_functions,
)
from langchain_core.tools import BaseTool, StructuredTool
from sqlmodel.ext.asyncio.session import AsyncSession


def _structured_tool(
    *,
    coroutine: Any,
    name: str,
    description: str,
    args_schema: type,
) -> BaseTool:
    return StructuredTool.from_function(
        coroutine=coroutine,
        name=name,
        description=description,
        args_schema=args_schema,
    )


def build_tools(session: AsyncSession, user_id: int) -> Sequence[BaseTool]:
    """Build CRM tools bound to the current database session and user."""

    search_contacts, get_contact = make_contact_tool_functions(session, user_id)
    search_leads, get_lead, list_leads_for_contact = make_lead_tool_functions(
        session,
        user_id,
    )
    (
        search_proposals,
        get_proposal,
        list_proposals_for_lead,
        calculate_proposal_metrics,
        compare_proposals,
    ) = make_proposal_tool_functions(session, user_id)
    get_pipeline_summary, list_stage_transitions = make_pipeline_tool_functions(
        session,
        user_id,
    )

    return [
        _structured_tool(
            coroutine=search_contacts,
            name="search_contacts",
            description="Search the authenticated user's CRM contacts.",
            args_schema=SearchContactsInput,
        ),
        _structured_tool(
            coroutine=get_contact,
            name="get_contact",
            description="Get one authenticated-user-owned CRM contact by ID.",
            args_schema=GetContactInput,
        ),
        _structured_tool(
            coroutine=search_leads,
            name="search_leads",
            description="Search the authenticated user's CRM leads.",
            args_schema=SearchLeadsInput,
        ),
        _structured_tool(
            coroutine=get_lead,
            name="get_lead",
            description="Get one authenticated-user-owned CRM lead by ID.",
            args_schema=GetLeadInput,
        ),
        _structured_tool(
            coroutine=list_leads_for_contact,
            name="list_leads_for_contact",
            description="List leads tied to one authenticated-user-owned contact.",
            args_schema=ListLeadsForContactInput,
        ),
        _structured_tool(
            coroutine=search_proposals,
            name="search_proposals",
            description="Search the authenticated user's CRM proposals.",
            args_schema=SearchProposalsInput,
        ),
        _structured_tool(
            coroutine=get_proposal,
            name="get_proposal",
            description="Get one proposal with lead and contact context by ID.",
            args_schema=GetProposalInput,
        ),
        _structured_tool(
            coroutine=list_proposals_for_lead,
            name="list_proposals_for_lead",
            description="List proposals tied to one authenticated-user-owned lead.",
            args_schema=ListProposalsForLeadInput,
        ),
        _structured_tool(
            coroutine=calculate_proposal_metrics,
            name="calculate_proposal_metrics",
            description="Calculate deterministic commercial metrics for a proposal.",
            args_schema=GetProposalInput,
        ),
        _structured_tool(
            coroutine=compare_proposals,
            name="compare_proposals",
            description="Compare deterministic metrics for multiple proposals.",
            args_schema=CompareProposalsInput,
        ),
        _structured_tool(
            coroutine=get_pipeline_summary,
            name="get_pipeline_summary",
            description="Get current stage and transition count for a lead/proposal.",
            args_schema=PipelineSummaryInput,
        ),
        _structured_tool(
            coroutine=list_stage_transitions,
            name="list_stage_transitions",
            description="List stage transitions for CRM leads/proposals.",
            args_schema=ListStageTransitionsInput,
        ),
    ]
