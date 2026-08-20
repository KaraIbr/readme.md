# Sequence Diagram: Proposal Win (Atomic Flow)

How marking a Proposal as WON triggers sibling superseding and Lead closure in a single transaction.

```mermaid
sequenceDiagram
    actor User
    participant FE as Frontend
    participant Router as proposals/router.py
    participant PropService as proposals/service.py
    participant LeadService as leads/service.py
    participant Pipeline as pipeline/service.py
    participant Repo as proposals/repository.py
    participant DB as Database

    Note over User,DB: === Mark Proposal as WON ===
    User->>FE: Click "Mark Won" on Proposal #1
    FE->>Router: POST /api/v1/proposals/1/won
    Router->>PropService: mark_won(proposal_id=1, user_id)

    Note over PropService,DB: Begin transaction
    PropService->>Repo: get_proposal_with_lead(1)
    Repo->>DB: SELECT proposal JOIN lead
    DB-->>Repo: Proposal + Lead

    PropService->>PropService: validate_stage(DRAFT or SENT+)
    PropService->>PropService: validate_one_won_per_lead()

    PropService->>Repo: mark_won(1, "WON")
    Repo->>DB: UPDATE proposal SET current_stage = 'WON'
    Repo->>DB: UPDATE lead SET current_stage = 'CLOSED_WON', outcome = 'WON'

    Note over PropService,DB: Supersede active siblings
    PropService->>Repo: supersede_active_siblings(lead_id=5, exclude_id=1)
    Repo->>DB: UPDATE proposal SET current_stage = 'SUPERSEDED'<br/>WHERE lead_id = 5 AND id != 1<br/>AND current_stage NOT IN ('WON','LOST','SUPERSEDED')

    PropService->>Pipeline: transition("PROPOSAL", 1, "SENT", "WON")
    Pipeline->>DB: INSERT INTO stage_transition

    Note over PropService,DB: End transaction
    PropService-->>Router: Updated Proposal
    Router-->>FE: 200 OK
    FE-->>User: Proposal WON, siblings SUPERSEDED, Lead CLOSED_WON
```

## Invariants Enforced

1. **One WON per Lead** — only one Proposal can be WON at a time
2. **Atomic win** — winning one Proposal auto-supersedes all active siblings in the same transaction
3. **Lead closes automatically** — the Lead transitions to CLOSED_WON when any Proposal wins
4. **SUPERSEDED is automatic** — never user-initiated, applied to all non-terminal siblings
5. **Loss reason mandatory** — when marking LOST, `loss_reason` is required

## Proposal Stage Machine

```
DRAFT ──→ SENT ──→ NEGOTIATION ──→ WON
                               └──→ LOST
                               └──→ SUPERSEDED (auto when sibling wins)
```
