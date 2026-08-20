"""API v1 router aggregation."""

from agent.router import router as agent_router
from domains.activities.router import router as activities_router
from domains.companies.router import router as companies_router
from domains.contacts.router import router as contacts_router
from domains.dashboard.router import router as dashboard_router
from domains.leads.router import router as leads_router
from domains.opportunities.router import router as opportunities_router
from domains.permissions.router import (
    lead_router as permissions_lead_router,
)
from domains.permissions.router import (
    proposal_router as permissions_proposal_router,
)
from domains.permissions.router import (
    router as permissions_router,
)
from domains.pipeline.router import router as pipeline_router
from domains.proposals.router import router as proposals_router
from domains.tasks.router import router as tasks_router
from domains.technical_visits.router import (
    lead_router as technical_visits_lead_router,
)
from domains.technical_visits.router import (
    proposal_router as technical_visits_proposal_router,
)
from domains.technical_visits.router import (
    router as technical_visits_router,
)
from fastapi import APIRouter

api_v1 = APIRouter(prefix="/api/v1")
api_v1.include_router(activities_router, prefix="/activities", tags=["activities"])
api_v1.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_v1.include_router(tasks_router, prefix="/tasks", tags=["tasks"])
api_v1.include_router(companies_router, prefix="/companies", tags=["companies"])
api_v1.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
api_v1.include_router(opportunities_router, prefix="/opportunities", tags=["opportunities"])
api_v1.include_router(leads_router, prefix="/leads", tags=["leads"])
api_v1.include_router(proposals_router, prefix="/proposals", tags=["proposals"])
api_v1.include_router(
    permissions_lead_router,
    prefix="/leads",
    tags=["permissions"],
)
api_v1.include_router(
    permissions_proposal_router,
    prefix="/proposals",
    tags=["permissions"],
)
api_v1.include_router(
    technical_visits_lead_router,
    prefix="/leads",
    tags=["technical-visits"],
)
api_v1.include_router(
    technical_visits_proposal_router,
    prefix="/proposals",
    tags=["technical-visits"],
)
api_v1.include_router(
    technical_visits_router,
    prefix="/technical-visits",
    tags=["technical-visits"],
)
api_v1.include_router(pipeline_router, prefix="/pipeline", tags=["pipeline"])
api_v1.include_router(permissions_router, prefix="/permissions", tags=["permissions"])
api_v1.include_router(agent_router, prefix="/agent", tags=["agent"])
