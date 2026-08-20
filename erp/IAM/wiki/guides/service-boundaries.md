# Guide: Service Boundaries

## Purpose

This guide defines the boundary between IAM and other VERP services.

## VERP Workspace

VERP is a workspace containing services. It is not a single API server.

```text
VERP/
|-- IAM/
`-- CRM/
```

Each service owns its startup, endpoints, docs, wiki, tests, and domain structure.

This service separation does not imply a separate physical database. Local
development uses the shared workspace database `./ventura.db`; production should use
the shared VERP PostgreSQL database unless a later ADR says otherwise.

## IAM Owns

- Central user accounts
- Authentication
- Token issuance
- IAM permissions
- Service access grants
- IAM tables and IAM migration history inside the shared VERP database

## IAM Does Not Own

- CRM roles
- CRM permissions
- CRM resource scope
- CRM business lifecycle
- CRM proposal pricing rules
- A separate `IAM/iam.db` database file

## CRM Owns

- CRM role assignment over IAM users
- CRM permission overrides over IAM users
- CRM lead/proposal/technical-visit assignments
- CRM agent scope
- CRM business invariants

## Cross-Service Rule

IAM may say:

```text
User 12 exists and has access to crm.
```

CRM may then say:

```text
User 12 is a sales user and can read assigned Lead 44.
```

Neither service should pretend to own the other service's authorization model.
