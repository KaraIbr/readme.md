# ADR: Outcome Lives in Proposal

**Date:** 2026-05-25
**Status:** Accepted

## Context
A Lead can have multiple Proposal variants. The business needs to know which exact variant won or lost, including technical differences and price differences.

## Alternatives considered
- **Store terminal outcome only on Lead:** Rejected because it loses the detail of which proposal variant was accepted or rejected.
- **Decide outcome at Proposal level and reflect it on Lead:** Accepted because it preserves proposal-level outcome detail while keeping Lead status useful.

## Decision
WON or LOST is decided at the Proposal level. Lead outcome reflects the aggregate result of its Proposals and is not the primary source of the terminal decision, except explicit manual abandonment.

## Consequences
- Winning one Proposal closes the Lead as `CLOSED_WON`.
- Active sibling Proposals are moved to `SUPERSEDED` when one Proposal wins.
- Losing all Proposals closes the Lead as `CLOSED_LOST`.

## Affected components
[[leads]], [[proposals]], [[pipeline]], [[pipeline-invariants]]
