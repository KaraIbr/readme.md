# ADR: IAM as a VERP Service

**Date:** 2026-06-01
**Status:** Accepted

## Context

VERP is the workspace for multiple backend services. CRM is one service inside VERP and has its own startup, endpoints, docs, wiki, and business domains. Central users and access must be shared by CRM and future services, so they cannot live inside CRM.

## Alternatives Considered

- **Keep identity inside CRM:** Rejected because future services would depend on CRM internals and user creation would remain wrongly coupled to CRM endpoints.
- **Place loose `users/identity/iam` modules directly under VERP:** Rejected because VERP does not run as a single API. Each backend capability should be a service with its own startup and documentation.
- **Create an IAM service sibling to CRM:** Accepted because it gives users, authentication, IAM permissions, and service access their own bounded service.

## Decision

Create `VERP/IAM` as a standalone service sibling to `VERP/CRM`.

IAM owns:
- Central VERP users
- Authentication and token issuance
- IAM permission overrides
- Access grants to VERP services

CRM owns:
- CRM roles
- CRM permission catalog
- CRM permission overrides
- CRM resource scope rules
- CRM business workflows

## Consequences

- IAM can evolve independently from CRM.
- CRM no longer creates central users.
- CRM must reference central IAM users and verify service access before assigning CRM roles.
- Shared user ids must remain stable across services.
- A workspace-level script can later start IAM and CRM together, but each service remains independently runnable.

## Affected Components

[[users]], [[auth]], [[permissions]], [[services]], [[api-v1]], [[core]]
