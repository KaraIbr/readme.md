# CRM Service Overview

## Purpose

CRM is the first functional business service in VERP. It manages the commercial lifecycle for renewable-energy opportunities from first contact through deal close. The current scope focuses on photovoltaic and battery energy storage opportunities, including contacts, leads, technical proposals, technical visits, documents, pipeline history, CRM authorization, and a read-oriented AI assistant.

CRM does not cover post-sale execution as an implemented service. Once a proposal is won, the proposal represents the project to execute, but execution itself is outside the current CRM boundary.

## Service Boundary

CRM owns:

- Commercial contacts and promoter catalog records.
- Leads as bounded sales opportunities.
- Lead documents, electricity bills, and sales interactions.
- Proposals as concrete technical and commercial offer variants.
- PV and BESS proposal detail records.
- Technical visits and visit evidence.
- Pipeline stage transitions and audit history.
- CRM-specific roles, permissions, overrides, and resource scopes.
- The CRM agent runtime and CRM-specific agent tools.

CRM does not own:

- Central user creation.
- Password authentication.
- Refresh tokens.
- IAM permission keys.
- IAM service-access grants.

Those identity and central access concerns belong to the sibling IAM service.

## Code Structure

```text
CRM/
|-- main.py
|-- docs/
|-- wiki/
|-- src/
|   |-- api/
|   |-- core/
|   |-- domains/
|   |   |-- users/
|   |   |-- contacts/
|   |   |-- leads/
|   |   |-- proposals/
|   |   |-- technical_visits/
|   |   |-- permissions/
|   |   `-- pipeline/
|   `-- agent/
`-- tests/
```

The service uses a domain-organized structure. Each business domain follows the same internal pattern:

| File | Responsibility |
|---|---|
| `models.py` | SQLModel persisted entities |
| `schemas.py` | Pydantic request and response DTOs |
| `repository.py` | Async SQLModel/SQLAlchemy data access |
| `service.py` | Business rules and orchestration |
| `router.py` | FastAPI HTTP routes |

Routers call services, services call repositories, and repositories own database queries. Cross-domain business calls should go through services rather than directly through another domain's repository.

## Runtime

CRM is a FastAPI service with versioned endpoints mounted under:

```text
/api/v1
```

Local startup from the VERP root:

```bash
uv run python CRM/main.py
```

The local quickstart documents the development app at:

```text
http://127.0.0.1:8000/docs
```

## Identity And Authorization

CRM uses IAM as the central source of users, authentication, account status, and service access. CRM keeps a read-only reference to the IAM-owned `iam_user` table so business records can point to stable user ids.

CRM authorization starts only after IAM has created the user and granted active service access for `crm`. CRM then applies its own role templates, permission overrides, and assignment-scoped resource checks.

Current CRM roles:

| Role | Meaning |
|---|---|
| `ADMIN` | All CRM permissions with global CRM scope |
| `MANAGER` | All CRM permissions with guardrails on user and permission administration |
| `SALES` | Commercial follow-up on assigned Leads and derived records |
| `TECH` | Technical work on assigned Proposals and TechnicalVisits |

Effective CRM permissions are computed as:

```text
effective_permissions = role_permissions + user_grants - user_denies
```

An effective permission is necessary but not always sufficient. CRM also checks resource scope, especially for `SALES` and `TECH` users. For example, a sales user can work on assigned Leads and derived Contacts, Proposals, TechnicalVisits, documents, and agent context. A tech user can work on assigned Proposals and TechnicalVisits, with derived read access to related Contacts, Leads, and Lead documents, but not Lead interactions.

## Domain Model

### Users Reference

`CRM/src/domains/users/` is a reference domain for IAM users. It does not create users or authenticate passwords. It resolves active IAM users and checks IAM service access for the `crm` service key.

### Contacts

Contacts answer "who they are." They are durable people or organizations that may generate zero or many Leads over time.

The contacts domain owns:

- `contact`: common contact identity, address, owner, and promoter reference.
- `individual_contact_profile`: individual-only email and phone.
- `company_contact_profile`: company-only industry.
- `company_contact_person`: one or more people inside a company contact.
- `promoter`: owner-scoped catalog of people who promote or refer contacts.

Important rules:

- A Contact can outlive a lost Lead and later generate another Lead.
- Every Contact references an owned Promoter.
- Company contacts must have at least one company person.
- Company representatives are not modeled as generic Contact rows.
- Deal-specific fields such as budget, capacity, roof details, and system scope belong in Leads or Proposals, not Contacts.

### Leads

Leads answer "what we want to sell them." A Lead is a bounded sales opportunity linked to one primary Contact.

The leads domain owns:

- `lead`: commercial opportunity header, interest type, stage, outcome, owner, and technical visit requirement.
- `lead_document`: general project documents such as plans, requirements, or specifications.
- `lead_electricity_bill`: electricity bills separated from general documents because they feed their own review process.
- `lead_interaction`: sales interactions, negotiations, notes, and planned or historical follow-ups.

Lead stages are:

```text
NEW -> QUALIFYING -> PROPOSAL_PHASE -> CLOSED_WON | CLOSED_LOST
```

Important rules:

- A Lead can have multiple Proposals.
- Lead outcome reflects Proposal outcomes except for explicit manual abandonment.
- Closed Leads cannot be updated, moved, closed again, or deleted.
- Stage changes are recorded through the pipeline domain.
- Sales assignment is the source of sales-user scope over Leads and derived records.

### Proposals

Proposals are concrete technical and commercial offer variants for a Lead. Until a proposal is won, there is no strict project in CRM's language.

The proposals domain owns:

- `proposal`: common commercial header.
- `proposal_pv_system`: one-to-one PV detail row for `PV` and `HIBRID` proposals.
- `proposal_bess_system`: one-to-one BESS detail row for `BESS` and `HIBRID` proposals.
- `proposal_commercial_document`: customer-facing commercial proposal PDFs.
- `proposal_document`: internal classified documents for costs, technical evidence, or other proposal material.

Proposal stages are:

```text
DRAFT -> SENT -> NEGOTIATION -> WON | LOST | SUPERSEDED
```

Important rules:

- `lead_id` and `name` are the only fields required to create a `DRAFT`.
- Common commercial fields and system-specific technical fields must be complete before a Proposal leaves `DRAFT`.
- Only one Proposal per Lead can be `WON`.
- When one Proposal wins, active sibling Proposals are moved to `SUPERSEDED` in the same transaction.
- If all active Proposals are lost, the Lead closes as `CLOSED_LOST`.
- `loss_reason` is mandatory when a Proposal is marked `LOST`.
- Protected price fields require dedicated price permissions:
  - `proposal.total_price`
  - `proposal_pv_system.price_watt`
  - `proposal_bess_system.price_kwh`

The implemented enum value for a combined PV and BESS proposal is `HIBRID`.

### Technical Visits

Technical visits are optional Lead-scoped subprocesses for on-site engineering inspections. A visit can happen before any Proposal exists or after a first Proposal has been sent.

The technical visits domain owns:

- `technical_visit`: visit header, schedule, receiver, status, creator, and timestamps.
- `technical_visit_assignee`: engineers or visitors assigned to the visit.
- `technical_visit_attachment`: visit documents, photos, and evidence.
- `proposal_technical_visit`: evidence links between Proposals and TechnicalVisits.

Technical visit statuses are:

```text
REQUESTED
SCHEDULED
COMPLETED
CANCELLED
```

Lead-level visit requirement values are:

```text
UNDETERMINED
NOT_REQUIRED
REQUIRED
```

Important rules:

- Creating a visit for an `UNDETERMINED` Lead automatically marks the Lead `REQUIRED`.
- Creating a visit for a `NOT_REQUIRED` Lead is rejected.
- Scheduled visits require schedule data and at least one assignee.
- Completing a visit requires complete schedule data and at least one uploaded attachment.
- Completed and cancelled visits cannot be modified.
- Proposal-to-visit links must stay within the same Lead.
- If a later visit changes assumptions after a Proposal has moved beyond `DRAFT`, create a new Proposal version and link it to the visit evidence.

### Pipeline

Pipeline is cross-cutting stage infrastructure. It tracks Lead and Proposal stage changes and records immutable transition history in `stage_transition`.

Pipeline does not own the business meaning of Leads or Proposals. It validates stage movement, records transitions, and provides summaries/history for authorized users.

Important rules:

- Transition history is append-only.
- Lead and Proposal services call pipeline operations when changing stages.
- Pipeline reads use CRM permissions and resource scope checks.

### Permissions

The permissions domain owns CRM-specific authorization records:

- `crm_user_access`: active CRM role and service authorization state for an IAM user.
- `crm_user_permission_override`: per-user CRM permission grant or denial.
- `lead_assignment`: active sales follow-up assignment with history.
- `proposal_assignment`: technical assignment for Proposal work.

Permission catalog and role templates are currently code-defined in `CRM/src/domains/permissions/service.py`.

Important guardrails:

- Managers cannot create IAM users.
- Managers cannot modify admin accounts.
- Managers cannot modify their own CRM role or permissions.
- Managers cannot grant permissions they do not effectively have.
- User-specific denials override role permissions and user-specific grants.
- Resource scope is checked after permission checks.

### Agent

The CRM agent is a read-oriented assistant implemented with LangGraph and a swappable LLM provider interface. It answers authenticated user questions using tools that call CRM domain services.

The agent does not duplicate business logic and does not bypass CRM permissions. Its tools must use the same authorization layer as REST endpoints.

Current capabilities include read tools for contacts, leads, proposals, pipeline summaries, transition history, and proposal metrics. Mutating operations are intentionally not exposed yet.

## API Groups

CRM aggregates these route groups under `/api/v1`:

| Group | Prefix | Purpose |
|---|---|---|
| Contacts | `/api/v1/contacts` | Contacts, promoters, company people |
| Leads | `/api/v1/leads` | Leads, documents, electricity bills, interactions |
| Proposals | `/api/v1/proposals` | Proposals and proposal documents |
| Technical visits | `/api/v1/technical-visits` plus Lead/Proposal subroutes | Visit lifecycle, attachments, proposal links |
| Pipeline | `/api/v1/pipeline` | Transition history and summaries |
| Permissions | `/api/v1/permissions` plus assignment subroutes | CRM roles, permissions, assignments |
| Agent | `/api/v1/agent` | CRM assistant chat |

IAM identity endpoints are not mounted by CRM.

## Database Ownership

CRM stores its data in the shared VERP database at `./ventura.db` for local development. CRM migrations are in the repository-level `alembic/` directory and use the default `alembic_version` table. Because CRM references IAM-owned `iam_user` rows, IAM migrations should be applied first on a fresh database.

Run migrations from the VERP root:

```bash
PYTHONPATH=IAM/src uv run python -m alembic -c IAM/alembic.ini upgrade head
PYTHONPATH=CRM/src uv run python -m alembic upgrade head
```

## Known Technical Debt

- The CRM permission catalog and role templates are code-defined rather than seeded database tables.
- Proposal assignment removal is not exposed yet.
- Proposal unit prices `price_watt` and `price_kwh` still need later calculated-and-rounded behavior rather than free editing.
- Agent write tools, confirmation checkpoints, stronger entity resolution, and production runtime hardening remain future work.
- Cross-service token validation currently depends on shared JWT configuration; a future architecture may use JWKS or IAM token introspection.

## Where To Go Deeper

Read the CRM service-local documentation:

| Path | Use |
|---|---|
| `CRM/docs/tech-spec.md` | Technical specification |
| `CRM/docs/local-rest-quickstart.md` | Local REST workflow |
| `CRM/docs/rest-json-bodies.md` | Request body examples |
| `CRM/wiki/` | Component pages, guides, decisions, and technical debt |
