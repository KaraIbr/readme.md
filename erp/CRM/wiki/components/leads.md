# Domain: Leads

**Path:** `src/domains/leads/`
**Responsibility:** Owns sales opportunities, the bounded "what to sell"; it also owns lead-scoped project documents, electricity bills, sales interactions, and the explicit technical visit requirement decision, but does not own permanent contact identity, technical visit execution, or technical proposal variants.
**Status:** In development

## Purpose
Leads represent qualified commercial interest before a definitive technical scope has been established.

## Data model
The implemented `Lead` SQLModel table is named `lead`.

Implemented fields:
- `id`
- `contact_id` — foreign key to `contact.id`
- `title`
- `interest_type`: `Photovoltaic`, `BESS`, or `Hibrid`
- `qualification_score`
- `current_stage`: `NEW`, `QUALIFYING`, `PROPOSAL_PHASE`, `CLOSED_WON`, `CLOSED_LOST`
- `outcome`: null until closed, then `WON` or `LOST`
- `owner_id` — foreign key to `iam_user.id`; currently stores active sales follow-up owner and is updated when [[permissions]] assigns or transfers a Lead
- `notes`
- `technical_visit_requirement`: `UNDETERMINED`, `NOT_REQUIRED`, or `REQUIRED`
- `created_at`, `closed_at`

Additional implemented lead-scoped tables:
- `LeadDocument` (`lead_document`) — general project documents such as plans, requirements, or customer-provided specifications; includes `title`, original filename, content type, stored path, size, uploader, and upload timestamp
- `LeadElectricityBill` (`lead_electricity_bill`) — electricity bills kept separate from general documents because they feed an independent review process; includes the same upload metadata fields
- `LeadInteraction` (`lead_interaction`) — sales interactions and negotiations documented against the lead; includes `interaction_type`, `title`, `notes`, `interaction_date`, creator, and timestamps

## Public interface (service.py)
- `create_lead(session, lead_create, owner_id) -> Lead` — creates a lead for a contact owned by the same user
- `get_lead(session, lead_id, owner_id) -> Lead` — loads an owned lead or raises `NotFoundError` / `AuthorizationError`
- `list_leads(session, owner_id, contact_id=None, stage=None, limit=100, offset=0) -> list[Lead]` — lists Leads visible to the user, optionally filtered by contact or stage
- `update_lead(session, lead_id, lead_update, owner_id) -> Lead` — partially updates an open owned lead
- `move_to_stage(session, lead_id, stage, owner_id) -> Lead` — moves an open lead through pre-close stages
- `close(session, lead_id, outcome, by, notes=None) -> Lead` — closes a lead as `CLOSED_WON` or `CLOSED_LOST`; this is the interface proposals will call
- `delete_lead(session, lead_id, owner_id) -> None` — deletes an open owned lead
- `upload_document(...) -> LeadDocument`, `list_documents(...)`, `get_document(...)`, `delete_document(...)` — manages general project documents for an owned lead
- `upload_electricity_bill(...) -> LeadElectricityBill`, `list_electricity_bills(...)`, `get_electricity_bill(...)`, `delete_electricity_bill(...)` — manages electricity bills separately from other lead documents
- `create_interaction(...) -> LeadInteraction`, `list_interactions(...)`, `get_interaction(...)`, `update_interaction(...)`, `delete_interaction(...)` — documents sales interactions and negotiations for an owned lead

## Router endpoints
The leads router is mounted under `/api/v1/leads`.

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/leads/` | Create a lead for an owned contact |
| GET | `/api/v1/leads/` | List leads owned by the authenticated user |
| GET | `/api/v1/leads/{lead_id}` | Return one owned lead |
| PATCH | `/api/v1/leads/{lead_id}` | Partially update one owned open lead |
| POST | `/api/v1/leads/{lead_id}/stage` | Move an open lead through `NEW → QUALIFYING → PROPOSAL_PHASE` |
| POST | `/api/v1/leads/{lead_id}/close` | Manually close a lead as `LOST` |
| DELETE | `/api/v1/leads/{lead_id}` | Delete one owned open lead |
| POST | `/api/v1/leads/{lead_id}/documents` | Upload a general project document with a title |
| GET | `/api/v1/leads/{lead_id}/documents` | List general project document metadata |
| GET | `/api/v1/leads/{lead_id}/documents/{document_id}` | Read one general project document metadata row |
| GET | `/api/v1/leads/{lead_id}/documents/{document_id}/download` | Download one general project document file |
| DELETE | `/api/v1/leads/{lead_id}/documents/{document_id}` | Delete one general project document |
| POST | `/api/v1/leads/{lead_id}/electricity-bills` | Upload an electricity bill with a title |
| GET | `/api/v1/leads/{lead_id}/electricity-bills` | List electricity bill metadata |
| GET | `/api/v1/leads/{lead_id}/electricity-bills/{bill_id}` | Read one electricity bill metadata row |
| GET | `/api/v1/leads/{lead_id}/electricity-bills/{bill_id}/download` | Download one electricity bill file |
| DELETE | `/api/v1/leads/{lead_id}/electricity-bills/{bill_id}` | Delete one electricity bill |
| POST | `/api/v1/leads/{lead_id}/interactions` | Document a sales interaction or negotiation |
| GET | `/api/v1/leads/{lead_id}/interactions` | List documented sales interactions |
| GET | `/api/v1/leads/{lead_id}/interactions/{interaction_id}` | Read one documented sales interaction |
| PATCH | `/api/v1/leads/{lead_id}/interactions/{interaction_id}` | Update one documented sales interaction |
| DELETE | `/api/v1/leads/{lead_id}/interactions/{interaction_id}` | Delete one documented sales interaction |

## Request / Response schemas (schemas.py)
- `LeadCreate` — request body for creating a lead; `owner_id`, `current_stage`, `outcome`, and `closed_at` are service-controlled
- `LeadUpdate` — partial update body for open leads
- `LeadStageChange` — request body for non-terminal stage movement
- `LeadClose` — request body for manual `LOST` outcome; `WON` is reserved for proposal workflows calling `service.close(...)`
- `LeadRead` — public lead response including owner, stage, outcome, technical visit requirement, and timestamps
- `LeadDocumentRead` — public metadata for general lead documents; upload itself is multipart form data with `title` plus `file`
- `LeadElectricityBillRead` — public metadata for lead electricity bills; upload itself is multipart form data with `title` plus `file`
- `LeadInteractionCreate`, `LeadInteractionUpdate`, `LeadInteractionRead` — DTOs for documenting sales interactions and negotiations

## Dependencies
- **Internal:** [[contacts]], [[users]], [[pipeline]], [[proposals]], [[technical-visits]]
- **Core:** [[core]], [[api-v1]]

## Business rules / invariants
- Lead answers "what we want to sell them."
- Lead lifetime is bounded: it opens, then closes.
- Lead does not carry budget or capacity estimates at lead creation; those belong later once scope/proposals are defined.
- Lead interest type is constrained to `Photovoltaic`, `BESS`, or `Hibrid`.
- One Lead references one primary Contact.
- A Lead can have multiple Proposals.
- General project documents and electricity bills are separate lead-scoped entities.
- Every uploaded document or bill requires a human title in addition to the original filename.
- Electricity bills must not be mixed into the general document collection because they are processed independently.
- Sales interactions and negotiations are documented at the lead level.
- The technical visit requirement decision is documented at the lead level; visit scheduling, completion, and evidence belong to [[technical-visits]].
- Creating a technical visit for an `UNDETERMINED` Lead marks the Lead as `REQUIRED`; creating one for a `NOT_REQUIRED` Lead is rejected.
- Every interaction must include `interaction_date`; the date can be past, present, or future for planned interactions.
- Lead outcome reflects proposal outcomes rather than independently determining them, except explicit manual abandonment.
- `owner_id` is never accepted from the request body; it comes from `current_user`.
- `contact_id` must reference a contact owned by the authenticated user.
- Authorization: active sales Lead assignment is the source of `sales` access. Assigning a Lead to another sales user removes the previous sales user's scope over that Lead, its Contact, and its derived Proposal/TechnicalVisit read access.
- Authorization: `tech` users can read Lead data, Lead documents, and electricity bills only when derived from assigned Proposals or TechnicalVisits; they cannot read Lead interactions.
- Open-stage transitions are constrained to `NEW → QUALIFYING → PROPOSAL_PHASE`.
- Terminal stages are reached through `close(...)`, which sets `outcome` and `closed_at`; direct HTTP close is manual `LOST` only.
- Closed leads cannot be updated, moved, closed again, or deleted.
- Stage changes are applied through [[pipeline]] so `stage_transition` receives append-only audit rows.

## Related decisions
[[2026-05-25-contact-vs-lead-separation]], [[2026-05-25-outcome-lives-in-proposal]], [[2026-05-25-domain-by-business-not-layer]], [[2026-05-29-technical-visits-as-lead-subprocess]], [[2026-06-01-verp-identity-crm-permissions]]

## Known technical debt
None documented.

## Maintainer notes
Do not collapse Contacts and Leads. Closing a lost Lead must not destroy the Contact.
The implementation lives under `CRM/src/domains/leads/`, is mounted in `CRM/src/api/v1/router.py`, and is covered by unit tests in `CRM/tests/unit/domains/leads/` plus integration tests in `CRM/tests/integration/api/`.
The project now includes an initial Alembic schema migration. Development SQLite databases created before that baseline should be recreated from Alembic or explicitly stamped only after confirming their schema matches the baseline.
