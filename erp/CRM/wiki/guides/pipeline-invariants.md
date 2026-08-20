# Guide: Pipeline Invariants

## Business Rules
1. Only one Proposal can be in `WON` state per Lead.
2. When a Proposal goes to `WON`, all active siblings auto-transition to `SUPERSEDED` in the same transaction.
3. `loss_reason` is mandatory when a Proposal goes to `LOST`.
4. A Lead is only closed as a consequence of its Proposals' outcomes, never directly, except explicit abandonment.
5. Every stage transition is recorded in `stage_transition`; history is immutable and append-only.

## Lead Stages
```text
NEW -> QUALIFYING -> PROPOSAL_PHASE -> CLOSED_WON | CLOSED_LOST
```

## Proposal Stages
```text
DRAFT -> SENT -> NEGOTIATION -> WON | LOST | SUPERSEDED
```

## Atomic Proposal Win Flow
When a proposal wins:
1. The winning Proposal transitions to `WON`.
2. Active sibling Proposals transition to `SUPERSEDED`.
3. The Lead closes as `CLOSED_WON`.

All three steps happen in the same transaction.

## Related Decisions
[[2026-05-25-outcome-lives-in-proposal]]

## Related Components
[[leads]], [[proposals]], [[pipeline]]
