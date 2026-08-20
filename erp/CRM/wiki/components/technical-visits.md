# Domain: Technical Visits

**Path:** `src/domains/technical_visits/`
**Responsibility:** Owns optional on-site technical visit subprocesses for Leads, including scheduling, assignees, completion, attachments, and Proposal evidence links.
**Status:** In development

## Purpose
Technical visits capture qualified engineering inspections at a customer's installation site. They help determine whether a Lead needs an on-site review, schedule the visit, record who performs and receives it, and store the documents or photos produced by the inspection.

## Data model
Implemented entities:
- `TechnicalVisit` (`technical_visit`) — Lead-scoped visit header with `lead_id`, `status`, `scheduled_at`, customer receiver contact fields, notes, creator, timestamps, and completion timestamp.
- `TechnicalVisitAssignee` (`technical_visit_assignee`) — one row per engineer or visitor assigned to the visit; can optionally reference an internal user when applicable.
- `TechnicalVisitAttachment` (`technical_visit_attachment`) — visit documents and photos with human title, file kind, original filename, content type, stored path, size, uploader, and upload timestamp.
- `ProposalTechnicalVisit` (`proposal_technical_visit`) — many-to-many relationship between Proposals and TechnicalVisits, with `relationship_type` such as `BASED_ON` or `VALIDATED_BY` and optional notes.

`TechnicalVisit.status` supports:
- `REQUESTED`
- `SCHEDULED`
- `COMPLETED`
- `CANCELLED`

Lead stores an implemented `technical_visit_requirement` decision:
- `UNDETERMINED`
- `NOT_REQUIRED`
- `REQUIRED`

## Public interface (service.py)
Implemented service functions:
- `set_lead_requirement(...) -> Lead` — records whether a Lead requires a technical visit.
- `create_visit(...) -> TechnicalVisit` — creates a visit for an owned open Lead.
- `list_visits(...) -> list[TechnicalVisit]` — lists owned visits, optionally filtered by Lead or status.
- `get_visit(...) -> TechnicalVisit` — returns one owned visit.
- `update_visit(...) -> TechnicalVisit` — updates scheduling and visit metadata before completion.
- `complete_visit(...) -> TechnicalVisit` — marks the visit completed after evidence has been uploaded.
- `cancel_visit(...) -> TechnicalVisit` — cancels a visit that is no longer needed.
- `upload_attachment(...) -> TechnicalVisitAttachment` — uploads a document, photo, or other evidence file to a visit.
- `list_attachments(...) -> list[TechnicalVisitAttachment]`, `get_attachment(...)`, `delete_attachment(...)` — manages visit evidence metadata and stored files.
- `link_proposal_visit(...) -> ProposalTechnicalVisit` — records that a Proposal is based on or validated by a visit.
- `list_proposal_visit_links(...) -> list[ProposalTechnicalVisit]` — lists Proposal-to-visit evidence links.
- `unlink_proposal_visit(...) -> None` — removes a non-essential Proposal-to-visit relationship.

## Router endpoints
Implemented router endpoints:

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/leads/{lead_id}/technical-visit-requirement` | Set the Lead's technical visit requirement decision |
| POST | `/api/v1/leads/{lead_id}/technical-visits` | Create a technical visit for a Lead |
| GET | `/api/v1/leads/{lead_id}/technical-visits` | List technical visits for a Lead |
| GET | `/api/v1/technical-visits` | List owned technical visits across Leads |
| GET | `/api/v1/technical-visits/{visit_id}` | Return one technical visit |
| PATCH | `/api/v1/technical-visits/{visit_id}` | Update schedule, receiver, notes, or assignees |
| POST | `/api/v1/technical-visits/{visit_id}/complete` | Mark a visit completed |
| POST | `/api/v1/technical-visits/{visit_id}/cancel` | Cancel a visit |
| POST | `/api/v1/technical-visits/{visit_id}/attachments` | Upload a visit document or photo |
| GET | `/api/v1/technical-visits/{visit_id}/attachments` | List visit attachment metadata |
| GET | `/api/v1/technical-visits/{visit_id}/attachments/{attachment_id}` | Read one visit attachment metadata row |
| GET | `/api/v1/technical-visits/{visit_id}/attachments/{attachment_id}/download` | Download one visit attachment |
| DELETE | `/api/v1/technical-visits/{visit_id}/attachments/{attachment_id}` | Delete one visit attachment |
| POST | `/api/v1/proposals/{proposal_id}/technical-visits` | Link a Proposal to a TechnicalVisit |
| GET | `/api/v1/proposals/{proposal_id}/technical-visits` | List visits linked to a Proposal |
| DELETE | `/api/v1/proposals/{proposal_id}/technical-visits/{technical_visit_id}` | Remove a Proposal-to-visit link |

## Request / Response schemas (schemas.py)
Implemented DTOs:
- `TechnicalVisitRequirementUpdate` — request body for the Lead-level requirement decision.
- `TechnicalVisitCreate`, `TechnicalVisitUpdate`, `TechnicalVisitRead` — scheduling and visit header DTOs.
- `TechnicalVisitAssigneePayload`, `TechnicalVisitAssigneeRead` — assignee DTOs.
- `TechnicalVisitCancel` — optional cancellation reason DTO; completing a visit has no request body.
- `TechnicalVisitAttachmentRead` — uploaded evidence metadata; upload itself is multipart form data with `title`, `file_kind`, and `file`.
- `ProposalTechnicalVisitCreate`, `ProposalTechnicalVisitRead` — Proposal evidence link DTOs.

## Dependencies
- **Internal:** [[leads]], [[proposals]], [[users]]
- **Core:** [[core]], [[api-v1]]

## Business rules / invariants
- Technical visits are optional per Lead.
- Lead visit requirement must be explicit: `UNDETERMINED`, `NOT_REQUIRED`, or `REQUIRED`.
- A visit must belong to one owned Lead.
- Creating a visit for an `UNDETERMINED` Lead automatically marks the Lead `REQUIRED`; creating a visit for a `NOT_REQUIRED` Lead is rejected.
- A visit may exist before any Proposal exists.
- A visit can start as `REQUESTED` without schedule data, or as `SCHEDULED` when `scheduled_at`, receiver name, receiver phone, and at least one assignee are provided together.
- Scheduled visits require at least one assignee.
- Authorization: `TechnicalVisitAssignee.user_id` grants `tech` scope over assigned visits.
- Authorization: `sales` users can read TechnicalVisits and attachments only when the visit belongs to an assigned Lead.
- Authorization: `tech` users can manage assigned TechnicalVisits and attachments, and can read related Lead and Contact context without Lead interactions.
- Completing a visit requires a complete schedule and at least one uploaded attachment.
- Completing a visit sets `completed_at`; no special field checklist is required.
- Completed and cancelled visits cannot be modified.
- Attachments can be uploaded before or after completion, but not after cancellation.
- Visit evidence is uploaded as attachments, not as structured completion fields.
- A Proposal can be linked to many TechnicalVisits through `ProposalTechnicalVisit`.
- A TechnicalVisit can be linked to many Proposals through `ProposalTechnicalVisit`.
- Proposal-to-visit links must stay within the same Lead.
- Duplicate Proposal-to-visit links are rejected.
- Sent or negotiated Proposals should not be silently edited when a later visit changes assumptions; create a new Proposal version and link it to the visit evidence.

## Related decisions
[[2026-05-29-technical-visits-as-lead-subprocess]], [[2026-05-25-outcome-lives-in-proposal]], [[2026-05-25-domain-by-business-not-layer]], [[2026-06-01-verp-identity-crm-permissions]]

## Known technical debt
None documented.

## Maintainer notes
Technical visits are business subprocesses, not pipeline stages. They do not change Lead or Proposal outcomes by themselves.
The implementation lives under `CRM/src/domains/technical_visits/`, is mounted in `CRM/src/api/v1/router.py` through lead, proposal, and technical-visit route groups, and is covered by unit tests in `CRM/tests/unit/domains/technical_visits/` plus integration tests in `CRM/tests/integration/api/test_technical_visits_router.py`.
The project now includes an initial Alembic schema migration. Development SQLite databases created before that baseline should be recreated from Alembic or explicitly stamped only after confirming their schema matches the baseline.
