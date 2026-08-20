# Domain: Pipeline

**Path:** `src/domains/pipeline/`
**Responsibility:** Owns stage transitions and immutable transition history for Leads and Proposals; it is not itself a business entity.
**Status:** In development

## Purpose
Pipeline tracks which stage each Lead and Proposal is in and records every transition as audit history.

## Data model
`PipelineEntityType` identifies the tracked entity family:
- `lead`
- `proposal`

Configured stage paths:
- Lead: `NEW -> QUALIFYING -> PROPOSAL_PHASE -> CLOSED_WON | CLOSED_LOST`
- Proposal: `DRAFT -> SENT -> NEGOTIATION -> WON | LOST | SUPERSEDED`

`StageTransition` is an implemented SQLModel table named `stage_transition`.

Critical fields:
- `id`
- `entity_type`: `lead` or `proposal`
- `entity_id`
- `from_stage`
- `to_stage`
- `transitioned_by`
- `transitioned_at`
- `reason`
- `notes`

## Public interface (service.py)
- `transition(session, entity_type, entity_id, to_stage, by, reason=None, notes=None, commit=True) -> StageTransition | None` — validates, applies, and audits a stage change; returns `None` for no-op transitions
- `record_initial_transition(session, entity_type, entity_id, to_stage, by, reason="created", notes=None, commit=True) -> StageTransition` — records `None -> initial_stage` when Leads or Proposals are created
- `list_transitions(session, user_id, entity_type=None, entity_id=None, limit=100, offset=0) -> list[StageTransition]` — lists authenticated user transition history
- `summarize_entity(session, user_id, entity_type, entity_id) -> PipelineSummary` — returns current stage, transition count, and latest transition timestamp for an owned entity

## Router endpoints
The pipeline router is mounted under `/api/v1/pipeline`.

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/pipeline/transitions` | List transition history for the authenticated user, optionally filtered by `entity_type` and `entity_id` |
| GET | `/api/v1/pipeline/summary/{entity_type}/{entity_id}` | Return a compact summary for one owned Lead or Proposal |

## Request / Response schemas (schemas.py)
- `StageTransitionRead` — public audit entry response
- `PipelineSummary` — compact current-stage and history summary

## Dependencies
- **Internal:** [[leads]], [[proposals]], [[users]]
- **Core:** [[core]], [[api-v1]]

## Business rules / invariants
- Every stage transition is recorded in `stage_transition`.
- `StageTransition` history is immutable and append-only.
- Transition validation belongs in the service layer.
- Lead open transitions are constrained to `NEW -> QUALIFYING -> PROPOSAL_PHASE`; terminal closure is allowed from any open lead stage to preserve manual abandonment and proposal-outcome flows.
- Proposal open transitions are constrained to `DRAFT -> SENT -> NEGOTIATION`; `WON` and `LOST` require service-level proposal workflows, while `SUPERSEDED` is used by the atomic win flow for active siblings.
- Pipeline summary and transition-history access use [[permissions]] so history is visible only when the user can access the underlying Lead or Proposal.
- Pipeline invariants are documented in [[pipeline-invariants]].

## Related decisions
[[2026-05-25-outcome-lives-in-proposal]], [[2026-05-25-domain-by-business-not-layer]], [[2026-06-01-verp-identity-crm-permissions]]

## Known technical debt
None documented.

## Maintainer notes
Pipeline is cross-cutting stage infrastructure. It should not absorb business ownership from [[leads]] or [[proposals]].
The current implementation lives under `CRM/src/domains/pipeline/`, is mounted in `CRM/src/api/v1/router.py`, and is covered by unit tests in `CRM/tests/unit/domains/pipeline/` plus integration tests in `CRM/tests/integration/api/`.
