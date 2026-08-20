# ADR: Technical Visits as Lead Subprocess

**Date:** 2026-05-29
**Status:** Accepted

## Context
Some renewable energy opportunities require an on-site technical visit before, during, or after the first commercial proposal. A qualified engineer inspects the customer's facilities, measures distances, reviews voltages, records installation constraints, and uploads documents or photos with the findings.

The visit can happen before any Proposal exists, or after an initial Proposal has already been sent. When a visit changes technical assumptions after a Proposal exists, the business needs to preserve which Proposal version was based on which visit evidence.

## Alternatives considered
- **Store visit fields directly on Lead:** Rejected because scheduling, assignees, completion, and attachments form a subprocess with identity and lifecycle.
- **Store visit fields directly on Proposal:** Rejected because visits can happen before a Proposal exists and can inform multiple Proposal versions.
- **Add a nullable `source_technical_visit_id` field to Proposal:** Rejected because it supports only one visit per proposal and puts cross-domain relationship metadata on the Proposal header.
- **Create a Lead-owned TechnicalVisit entity and a ProposalTechnicalVisit link table:** Accepted because the visit belongs to the sales opportunity, while proposals can explicitly reference the visit evidence they used.

## Decision
Technical visits are modeled as an optional Lead-scoped subprocess with their own persisted entity, schedule fields, assignees, status, and attachments.

Proposals do not store a direct visit foreign key. Instead, Proposal-to-visit usage is modeled through a `ProposalTechnicalVisit` relationship table with relationship metadata such as `BASED_ON` or `VALIDATED_BY`.

The Lead also stores an explicit visit requirement decision so the system can distinguish "not decided yet" from "visit is not required."

## Consequences
- A Lead can have zero, one, or many TechnicalVisits.
- A TechnicalVisit can be scheduled and completed without any Proposal.
- A Proposal can reference one or more TechnicalVisits without adding visit fields to the Proposal header.
- Multiple Proposal versions can reference the same TechnicalVisit.
- If a visit changes assumptions after a Proposal has moved beyond `DRAFT`, the business should create a new Proposal version rather than silently editing the already-sent offer.
- Visit documents and photos belong to the TechnicalVisit, not the generic Lead document collection.

## Affected components
[[leads]], [[proposals]], [[technical-visits]], [[api-v1]]
