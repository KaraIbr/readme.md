"""Proposal tools for the runtime CRM assistant."""

from agent.tools.formatters import proposal_metrics, proposal_record
from agent.tools.serialization import to_json
from domains.contacts import service as contacts_service
from domains.leads import service as leads_service
from domains.proposals import service as proposals_service
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession


class SearchProposalsInput(BaseModel):
    """Input for searching CRM proposals."""

    query: str = Field(
        min_length=1,
        description="Proposal name, address, system type, inverter, or term",
    )
    limit: int = Field(default=10, ge=1, le=25)


class GetProposalInput(BaseModel):
    """Input for retrieving one proposal."""

    proposal_id: int = Field(gt=0)


class ListProposalsForLeadInput(BaseModel):
    """Input for listing proposals tied to one lead."""

    lead_id: int = Field(gt=0)
    limit: int = Field(default=10, ge=1, le=25)


class CompareProposalsInput(BaseModel):
    """Input for comparing proposal metrics."""

    proposal_ids: list[int] = Field(min_length=2, max_length=10)


async def _proposal_with_context(
    session: AsyncSession,
    proposal,
    user_id: int,
) -> dict:
    lead = await leads_service.get_lead(
        session,
        proposal.lead_id,
        owner_id=user_id,
    )
    contact = await contacts_service.get_contact(
        session,
        lead.contact_id,
        owner_id=user_id,
    )
    return proposal_record(proposal, lead=lead, contact=contact)


def make_proposal_tool_functions(session: AsyncSession, user_id: int):
    """Create async proposal tool callables bound to request context."""

    async def search_proposals(query: str, limit: int = 10) -> str:
        """Search proposals owned by the authenticated user."""

        proposals = await proposals_service.search_proposals(
            session,
            user_id=user_id,
            query=query,
            limit=limit,
        )
        records = [
            await _proposal_with_context(session, proposal, user_id) for proposal in proposals
        ]
        return to_json(
            {
                "tool": "search_proposals",
                "query": query,
                "count": len(records),
                "records": records,
            }
        )

    async def get_proposal(proposal_id: int) -> str:
        """Get one proposal with its lead and contact context."""

        proposal = await proposals_service.get_proposal(
            session,
            proposal_id,
            user_id=user_id,
        )
        return to_json(
            {
                "tool": "get_proposal",
                "record": await _proposal_with_context(session, proposal, user_id),
            }
        )

    async def list_proposals_for_lead(lead_id: int, limit: int = 10) -> str:
        """List proposals owned by the user for a specific lead."""

        proposals = await proposals_service.list_proposals(
            session,
            user_id=user_id,
            lead_id=lead_id,
            limit=limit,
        )
        records = [
            await _proposal_with_context(session, proposal, user_id) for proposal in proposals
        ]
        return to_json(
            {
                "tool": "list_proposals_for_lead",
                "lead_id": lead_id,
                "count": len(records),
                "records": records,
            }
        )

    async def calculate_proposal_metrics(proposal_id: int) -> str:
        """Calculate deterministic commercial metrics for one proposal."""

        proposal = await proposals_service.get_proposal(
            session,
            proposal_id,
            user_id=user_id,
        )
        return to_json(
            {
                "tool": "calculate_proposal_metrics",
                "metrics": proposal_metrics(proposal),
            }
        )

    async def compare_proposals(proposal_ids: list[int]) -> str:
        """Compare deterministic commercial metrics for multiple proposals."""

        metrics = []
        for proposal_id in proposal_ids:
            proposal = await proposals_service.get_proposal(
                session,
                proposal_id,
                user_id=user_id,
            )
            metrics.append(proposal_metrics(proposal))
        return to_json(
            {
                "tool": "compare_proposals",
                "count": len(metrics),
                "metrics": metrics,
            }
        )

    return (
        search_proposals,
        get_proposal,
        list_proposals_for_lead,
        calculate_proposal_metrics,
        compare_proposals,
    )
