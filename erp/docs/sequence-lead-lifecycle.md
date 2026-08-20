# Sequence Diagram: Lead Lifecycle

How a Lead progresses from creation through close.

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant Router as router.py
    participant Service as leads/service.py
    participant Pipeline as pipeline/service.py
    participant Repo as leads/repository.py
    participant DB as Database

    Note over User,DB: === Create Lead ===
    User->>FE: Fill lead form
    FE->>Router: POST /api/v1/leads/
    Router->>Service: create_lead(payload, owner_id)
    Service->>Repo: insert_lead(lead_data)
    Repo->>DB: INSERT INTO lead
    DB-->>Repo: Lead created
    Repo-->>Service: Lead
    Service-->>Router: Lead
    Router-->>FE: 201 Created
    FE-->>User: Lead created (stage: NEW)

    Note over User,DB: === Move Stage: NEW → QUALIFYING ===
    User->>FE: Click "Advance Stage"
    FE->>Router: POST /api/v1/leads/{id}/stage
    Router->>Service: move_stage(lead_id, "QUALIFYING")
    Service->>Service: validate_current_stage(NEW)
    Service->>Pipeline: transition("LEAD", id, "NEW", "QUALIFYING")
    Pipeline->>Repo: insert_stage_transition()
    Repo->>DB: INSERT INTO stage_transition
    Pipeline-->>Service: Transition recorded
    Service->>Repo: update_lead_stage("QUALIFYING")
    Repo->>DB: UPDATE lead SET current_stage = 'QUALIFYING'
    Service-->>Router: Updated Lead
    Router-->>FE: 200 OK

    Note over User,DB: === Move Stage: QUALIFYING → PROPOSAL_PHASE ===
    User->>FE: Click "Advance Stage"
    FE->>Router: POST /api/v1/leads/{id}/stage
    Router->>Service: move_stage(lead_id, "PROPOSAL_PHASE")
    Service->>Service: validate_current_stage(QUALIFYING)
    Service->>Pipeline: transition("LEAD", id, "QUALIFYING", "PROPOSAL_PHASE")
    Pipeline->>Repo: INSERT INTO stage_transition
    Service->>Repo: update_lead_stage("PROPOSAL_PHASE")
    Repo->>DB: UPDATE lead SET current_stage = 'PROPOSAL_PHASE'

    Note over User,DB: === Close Lead (manual LOST) ===
    User->>FE: Click "Close as Lost"
    FE->>Router: POST /api/v1/leads/{id}/close
    Router->>Service: close_lead(lead_id, "LOST", reason)
    Service->>Service: validate_not_already_closed()
    Service->>Pipeline: transition("LEAD", id, "PROPOSAL_PHASE", "CLOSED_LOST")
    Pipeline->>Repo: INSERT INTO stage_transition
    Service->>Repo: update_lead_close("CLOSED_LOST", "LOST")
    Repo->>DB: UPDATE lead SET current_stage='CLOSED_LOST', outcome='LOST'
    Service-->>Router: Closed Lead
    Router-->>FE: 200 OK
    FE-->>User: Lead closed (immutable)
```

## Stage Machine

```
NEW ──→ QUALIFYING ──→ PROPOSAL_PHASE ──→ CLOSED_WON  (via proposal won)
                                      └──→ CLOSED_LOST  (via all proposals lost, or manual close)
```

- Stages move forward only, no backward transitions
- Manual close is LOST-only (WON is reserved for proposal outcome)
- Closed leads are immutable (no update, no delete, no stage change)
