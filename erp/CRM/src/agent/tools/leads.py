"""Lead tools for the runtime CRM assistant."""

from agent.tools.formatters import lead_record
from agent.tools.serialization import to_json
from domains.contacts import service as contacts_service
from domains.leads import service as leads_service
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession


class SearchLeadsInput(BaseModel):
    """Input for searching CRM leads."""

    query: str = Field(min_length=1, description="Lead title, interest, or term")
    limit: int = Field(default=10, ge=1, le=25)


class GetLeadInput(BaseModel):
    """Input for retrieving one lead."""

    lead_id: int = Field(gt=0)


class ListLeadsForContactInput(BaseModel):
    """Input for listing leads tied to one contact."""

    contact_id: int = Field(gt=0)
    limit: int = Field(default=10, ge=1, le=25)


async def _lead_with_contact(session: AsyncSession, lead, user_id: int) -> dict:
    contact = await contacts_service.get_contact(
        session,
        lead.contact_id,
        owner_id=user_id,
    )
    return lead_record(lead, contact=contact)


def make_lead_tool_functions(session: AsyncSession, user_id: int):
    """Create async lead tool callables bound to request context."""

    async def search_leads(query: str, limit: int = 10) -> str:
        """Search leads owned by the authenticated user."""

        leads = await leads_service.search_leads(
            session,
            owner_id=user_id,
            query=query,
            limit=limit,
        )
        records = [await _lead_with_contact(session, lead, user_id) for lead in leads]
        return to_json(
            {
                "tool": "search_leads",
                "query": query,
                "count": len(records),
                "records": records,
            }
        )

    async def get_lead(lead_id: int) -> str:
        """Get one lead owned by the authenticated user."""

        lead = await leads_service.get_lead(session, lead_id, owner_id=user_id)
        return to_json(
            {
                "tool": "get_lead",
                "record": await _lead_with_contact(session, lead, user_id),
            }
        )

    async def list_leads_for_contact(contact_id: int, limit: int = 10) -> str:
        """List leads owned by the user for a specific contact."""

        leads = await leads_service.list_leads(
            session,
            owner_id=user_id,
            contact_id=contact_id,
            limit=limit,
        )
        records = [await _lead_with_contact(session, lead, user_id) for lead in leads]
        return to_json(
            {
                "tool": "list_leads_for_contact",
                "contact_id": contact_id,
                "count": len(records),
                "records": records,
            }
        )

    return search_leads, get_lead, list_leads_for_contact
