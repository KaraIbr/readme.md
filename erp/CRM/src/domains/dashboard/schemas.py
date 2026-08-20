from datetime import datetime

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_contacts: int
    total_leads: int
    active_leads: int
    won_leads: int
    pending_visits: int
    revenue_won: float
    leads_by_stage: dict[str, int]
    proposals_by_stage: dict[str, int]
    recent_transitions: list[dict]


class TransitionEntry(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    to_stage: str
    transitioned_at: datetime
