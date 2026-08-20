# Subsystem: API v1

**Path:** `src/api/v1/`
**Responsibility:** Owns versioned REST router aggregation; it does not implement domain business logic.
**Status:** Stable

## Purpose
API v1 mounts all domain routers under a stable `/api/v1` prefix and centralizes shared HTTP dependencies.

## Data model
API v1 does not own persisted data models.

## Public interface (service.py)
No service layer is specified for API v1. The main interface is `api_v1` in `src/api/v1/router.py`.

## Router endpoints
The technical specification mounts routers as:

| Router | Prefix | Tags |
|---|---|---|
| contacts | `/api/v1/contacts` | `contacts` |
| leads | `/api/v1/leads` | `leads` |
| proposals | `/api/v1/proposals` | `proposals` |
| technical visits | `/api/v1/technical-visits` | `technical-visits` |
| pipeline | `/api/v1/pipeline` | `pipeline` |
| agent | `/api/v1/agent` | `agent` |
| permissions | `/api/v1/permissions` | `permissions` |

Contacts subroutes from [[2026-05-28-contact-promoters-and-company-people]]:

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/contacts/promoters` | Create an owned promoter catalog entry |
| GET | `/api/v1/contacts/promoters` | List owned promoters |
| GET | `/api/v1/contacts/promoters/{promoter_id}` | Return one owned promoter |
| PATCH | `/api/v1/contacts/promoters/{promoter_id}` | Update one owned promoter |
| DELETE | `/api/v1/contacts/promoters/{promoter_id}` | Delete one unused promoter |
| POST | `/api/v1/contacts/{company_id}/people` | Add a person inside an owned company |
| GET | `/api/v1/contacts/{company_id}/people` | List people inside an owned company |
| GET | `/api/v1/contacts/{company_id}/people/{person_id}` | Return one company person |
| PATCH | `/api/v1/contacts/{company_id}/people/{person_id}` | Update one company person |
| DELETE | `/api/v1/contacts/{company_id}/people/{person_id}` | Delete one company person without leaving the company empty |

Lead subroutes for project documents, electricity bills, and interactions:

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/leads/{lead_id}/documents` | Upload a general project document |
| GET | `/api/v1/leads/{lead_id}/documents` | List general project document metadata |
| GET | `/api/v1/leads/{lead_id}/documents/{document_id}` | Read one general project document metadata row |
| GET | `/api/v1/leads/{lead_id}/documents/{document_id}/download` | Download one general project document |
| DELETE | `/api/v1/leads/{lead_id}/documents/{document_id}` | Delete one general project document |
| POST | `/api/v1/leads/{lead_id}/electricity-bills` | Upload an electricity bill |
| GET | `/api/v1/leads/{lead_id}/electricity-bills` | List electricity bill metadata |
| GET | `/api/v1/leads/{lead_id}/electricity-bills/{bill_id}` | Read one electricity bill metadata row |
| GET | `/api/v1/leads/{lead_id}/electricity-bills/{bill_id}/download` | Download one electricity bill |
| DELETE | `/api/v1/leads/{lead_id}/electricity-bills/{bill_id}` | Delete one electricity bill |
| POST | `/api/v1/leads/{lead_id}/interactions` | Document a sales interaction or negotiation |
| GET | `/api/v1/leads/{lead_id}/interactions` | List lead interactions |
| GET | `/api/v1/leads/{lead_id}/interactions/{interaction_id}` | Read one lead interaction |
| PATCH | `/api/v1/leads/{lead_id}/interactions/{interaction_id}` | Update one lead interaction |
| DELETE | `/api/v1/leads/{lead_id}/interactions/{interaction_id}` | Delete one lead interaction |

Proposal subroutes for customer-facing commercial PDFs and classified internal documents:

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/proposals/{proposal_id}/commercial-pdf` | Upload the commercial proposal PDF sent or intended for the customer |
| GET | `/api/v1/proposals/{proposal_id}/commercial-pdf` | List commercial proposal PDF metadata |
| GET | `/api/v1/proposals/{proposal_id}/commercial-pdf/{document_id}` | Read one commercial PDF metadata row |
| GET | `/api/v1/proposals/{proposal_id}/commercial-pdf/{document_id}/download` | Download one commercial proposal PDF |
| DELETE | `/api/v1/proposals/{proposal_id}/commercial-pdf/{document_id}` | Delete one commercial proposal PDF |
| POST | `/api/v1/proposals/{proposal_id}/documents` | Upload a classified proposal document (`Costs`, `Technical`, or `Other`) |
| GET | `/api/v1/proposals/{proposal_id}/documents` | List classified proposal document metadata |
| GET | `/api/v1/proposals/{proposal_id}/documents/{document_id}` | Read one classified proposal document metadata row |
| GET | `/api/v1/proposals/{proposal_id}/documents/{document_id}/download` | Download one classified proposal document |
| DELETE | `/api/v1/proposals/{proposal_id}/documents/{document_id}` | Delete one classified proposal document |

Technical visit subroutes from [[2026-05-29-technical-visits-as-lead-subprocess]]:

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/leads/{lead_id}/technical-visit-requirement` | Set a Lead's technical visit requirement decision |
| POST | `/api/v1/leads/{lead_id}/technical-visits` | Create a technical visit for a Lead |
| GET | `/api/v1/leads/{lead_id}/technical-visits` | List technical visits for a Lead |
| GET | `/api/v1/technical-visits` | List owned technical visits across Leads |
| GET | `/api/v1/technical-visits/{visit_id}` | Return one technical visit |
| PATCH | `/api/v1/technical-visits/{visit_id}` | Update a requested or scheduled visit |
| POST | `/api/v1/technical-visits/{visit_id}/complete` | Mark a visit completed |
| POST | `/api/v1/technical-visits/{visit_id}/cancel` | Cancel a visit |
| POST | `/api/v1/technical-visits/{visit_id}/attachments` | Upload visit evidence |
| GET | `/api/v1/technical-visits/{visit_id}/attachments` | List visit attachment metadata |
| GET | `/api/v1/technical-visits/{visit_id}/attachments/{attachment_id}` | Read visit attachment metadata |
| GET | `/api/v1/technical-visits/{visit_id}/attachments/{attachment_id}/download` | Download visit evidence |
| DELETE | `/api/v1/technical-visits/{visit_id}/attachments/{attachment_id}` | Delete visit evidence |
| POST | `/api/v1/proposals/{proposal_id}/technical-visits` | Link a Proposal to technical visit evidence |
| GET | `/api/v1/proposals/{proposal_id}/technical-visits` | List Proposal-to-visit evidence links |
| DELETE | `/api/v1/proposals/{proposal_id}/technical-visits/{technical_visit_id}` | Remove a Proposal-to-visit evidence link |

Permission subroutes from [[permissions]]:

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/permissions` | List CRM permission catalog |
| GET | `/api/v1/permissions/users/{user_id}` | Read one user's CRM role, overrides, and effective permissions |
| PATCH | `/api/v1/permissions/users/{user_id}` | Grant, deny, or clear individual CRM permission overrides |
| POST | `/api/v1/permissions/users/{user_id}/role` | Assign a CRM role template |
| POST | `/api/v1/leads/{lead_id}/assignment` | Assign or transfer sales follow-up for a Lead |
| POST | `/api/v1/proposals/{proposal_id}/assignments` | Assign a technical user to a Proposal |

## Request / Response schemas (schemas.py)
API v1 does not define domain DTOs in the technical specification.

## Dependencies
- **Internal:** [[users]], [[contacts]], [[leads]], [[proposals]], [[technical-visits]], [[pipeline]], [[agent]], [[permissions]]
- **Core:** [[core]]

## Business rules / invariants
- Domain routers are aggregated under `/api/v1`.
- `api/dependencies.py` provides shared dependencies such as database session and current user.
- Routers only know services and schemas, not repositories.
- CRM authorization is centralized through [[permissions]] instead of per-router role shortcuts.
- Every authenticated endpoint must check both action permission and resource scope when the operation is not purely public authentication.

## Related decisions
[[2026-05-25-domain-by-business-not-layer]], [[2026-05-28-contact-promoters-and-company-people]], [[2026-05-29-technical-visits-as-lead-subprocess]], [[2026-06-01-verp-identity-crm-permissions]]

## Known technical debt
None documented.

## Maintainer notes
Keep HTTP aggregation separate from business orchestration.
The current implementation mounts only CRM routers. IAM users, login, IAM permissions, and service-access grants are served by the sibling IAM service.
Static contacts subroutes such as `/contacts/promoters` must be registered before parameterized contact routes such as `/contacts/{contact_id}`.
