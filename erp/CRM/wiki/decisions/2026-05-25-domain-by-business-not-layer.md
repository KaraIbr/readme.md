# ADR: Domain by Business, Not Layer

**Date:** 2026-05-25
**Status:** Accepted

## Context
The backend covers several business domains with consistent internal layers. The project needs a structure that keeps business concepts cohesive.

## Alternatives considered
- **Organize globally by technical layer:** Rejected because folders like `models/`, `services/`, and `routers/` would scatter each business concept across the codebase.
- **Organize by business domain:** Accepted because each domain can keep its model, schemas, repository, service, and router together.

## Decision
Use a `src/` layout organized by business domain: users, contacts, leads, proposals, pipeline, plus agent, core, and API aggregation.

## Consequences
- Domain ownership is clearer.
- Each domain follows the same 5-file pattern.
- Cross-domain calls should happen through services, not repositories.

## Affected components
[[users]], [[contacts]], [[leads]], [[proposals]], [[pipeline]], [[agent]], [[api-v1]], [[domain-structure]]
