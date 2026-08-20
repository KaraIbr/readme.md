"""Contact tools for the runtime CRM assistant."""

from agent.tools.formatters import contact_record
from agent.tools.serialization import to_json
from domains.contacts import service as contacts_service
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession


class SearchContactsInput(BaseModel):
    """Input for searching CRM contacts."""

    query: str = Field(min_length=1, description="Name, email, phone, city, or term")
    limit: int = Field(default=10, ge=1, le=25)


class GetContactInput(BaseModel):
    """Input for retrieving one contact."""

    contact_id: int = Field(gt=0)


def make_contact_tool_functions(session: AsyncSession, user_id: int):
    """Create async contact tool callables bound to request context."""

    async def search_contacts(query: str, limit: int = 10) -> str:
        """Search contacts owned by the authenticated user."""

        contacts = await contacts_service.search_contacts(
            session,
            owner_id=user_id,
            query=query,
            limit=limit,
        )
        return to_json(
            {
                "tool": "search_contacts",
                "query": query,
                "count": len(contacts),
                "records": [contact_record(contact) for contact in contacts],
            }
        )

    async def get_contact(contact_id: int) -> str:
        """Get one contact owned by the authenticated user."""

        contact = await contacts_service.get_contact(
            session,
            contact_id,
            owner_id=user_id,
        )
        return to_json(
            {
                "tool": "get_contact",
                "record": contact_record(contact),
            }
        )

    return search_contacts, get_contact
