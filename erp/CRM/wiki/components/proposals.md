# Domain: Proposals

**Path:** `src/domains/proposals/`
**Responsibility:** Owns concrete technical offer variants for a Lead; it does not own permanent contact identity, technical visit execution, or generic stage history.
**Status:** In development

## Purpose
Proposals represent technical variants offered to a customer to close a Lead. They are explicitly classified as `PV`, `BESS`, or `HIBRID` (`PV + BESS`). When one proposal is won, that proposal becomes the project to execute.

## Data model
The implemented `Proposal` SQLModel table is named `proposal` and now stores only the common commercial header.

Common `Proposal` fields:
- `id`
- `lead_id` — foreign key to `lead.id`
- `name`
- `version`
- `installation_address_line`
- `installation_city`
- `installation_state`
- `installation_postal_code`
- `tariff`
- `contracted_demand`
- `system_type`: `PV`, `BESS`, or `HIBRID`
- `total_price`
- `annual_savings`
- `currency`
- `estimated_cost`
- `expected_profit`
- `submitted_at`
- `valid_until`
- `current_stage`: `DRAFT`, `SENT`, `NEGOTIATION`, `WON`, `LOST`, `SUPERSEDED`
- `loss_reason`
- `proposed_at`
- `created_by` — foreign key to `iam_user.id`
- `created_at`

`ProposalPVSystem` is an implemented one-to-one detail table named `proposal_pv_system`; it is present for `PV` and `HIBRID` proposals and owns: `panel_count`, `panel_model`, `panel_power`, `inverter_model`, `inverter_count`, `inverter_power`, `type_of_surface`, `total_power_ac`, `system_size_kw`, `oversizing_kw`, `estimated_annual_kwh`, `estimated_savings_kw`, `connection_mode`, `cost_watt`, and `price_watt`.

`ProposalBESSSystem` is an implemented one-to-one detail table named `proposal_bess_system`; it is present for `BESS` and `HIBRID` proposals and owns: `battery_model`, `battery_count`, `battery_power_kw`, `battery_storage_kwh`, `bess_primary_use`, `technical_notes`, `cost_kwh`, and `price_kwh`.

`ProposalCommercialDocument` stores the customer-facing commercial proposal PDF separately from other documents. `ProposalDocument` stores proposal cost, technical, or other internal documents with `title` and `classification` (`Costs`, `Technical`, or `Other`).

Technical visit evidence is linked through [[technical-visits]] using `ProposalTechnicalVisit`; the Proposal header does not store a direct technical visit foreign key.

Authorization treats `total_price`, `ProposalPVSystem.price_watt`, and `ProposalBESSSystem.price_kwh` as protected price fields with permissions separate from general Proposal updates.

## Public interface (service.py)
- `create_proposal(session, proposal_create, created_by) -> Proposal` — creates a `DRAFT` proposal for an owned open lead
- `get_proposal(session, proposal_id, user_id) -> Proposal` — loads an owned proposal or raises `NotFoundError` / `AuthorizationError`
- `list_proposals(session, user_id, lead_id=None, stage=None, limit=100, offset=0) -> list[Proposal]` — lists proposals created by the user
- `update_proposal(session, proposal_id, proposal_update, user_id) -> Proposal` — partially updates a non-terminal proposal
- `move_to_stage(session, proposal_id, stage, user_id) -> Proposal` — moves through non-terminal stages (`DRAFT → SENT → NEGOTIATION`)
- `mark_won(proposal_id, user_id, session) -> Proposal` — marks one sent proposal `WON`, supersedes active siblings, and closes the Lead as `WON`
- `mark_lost(session, proposal_id, user_id, loss_reason) -> Proposal` — marks one sent proposal `LOST`; if no active proposals remain, closes the Lead as `LOST`
- `delete_proposal(session, proposal_id, user_id) -> None` — deletes a non-terminal proposal
- `upload_commercial_document(session, proposal_id, title, upload, user_id) -> ProposalCommercialDocument` — stores the commercial proposal PDF
- `list_commercial_documents(session, proposal_id, user_id) -> list[ProposalCommercialDocument]` — lists commercial PDFs for an owned proposal
- `upload_document(session, proposal_id, title, classification, upload, user_id) -> ProposalDocument` — stores a classified proposal document
- `list_documents(session, proposal_id, user_id, classification=None) -> list[ProposalDocument]` — lists classified proposal documents

Proposal-to-technical-visit evidence links are owned by [[technical-visits]], not by `proposals/service.py`.

## Router endpoints
The proposals router is mounted under `/api/v1/proposals`.

| Method | Path | Description |
|---|---|---|
| POST | `/api/v1/proposals/` | Create a proposal for an owned lead |
| GET | `/api/v1/proposals/` | List proposals created by the authenticated user |
| GET | `/api/v1/proposals/{proposal_id}` | Return one owned proposal |
| PATCH | `/api/v1/proposals/{proposal_id}` | Partially update one owned non-terminal proposal |
| POST | `/api/v1/proposals/{proposal_id}/stage` | Move through non-terminal stages |
| POST | `/api/v1/proposals/{proposal_id}/won` | Mark one sent proposal as won |
| POST | `/api/v1/proposals/{proposal_id}/lost` | Mark one sent proposal as lost with `loss_reason` |
| DELETE | `/api/v1/proposals/{proposal_id}` | Delete one owned non-terminal proposal |
| POST | `/api/v1/proposals/{proposal_id}/commercial-pdf` | Upload the customer-facing commercial proposal PDF |
| GET | `/api/v1/proposals/{proposal_id}/commercial-pdf` | List commercial PDF metadata |
| GET | `/api/v1/proposals/{proposal_id}/commercial-pdf/{document_id}` | Read commercial PDF metadata |
| GET | `/api/v1/proposals/{proposal_id}/commercial-pdf/{document_id}/download` | Download a commercial proposal PDF |
| DELETE | `/api/v1/proposals/{proposal_id}/commercial-pdf/{document_id}` | Delete a commercial proposal PDF |
| POST | `/api/v1/proposals/{proposal_id}/documents` | Upload a classified proposal document |
| GET | `/api/v1/proposals/{proposal_id}/documents` | List classified proposal documents |
| GET | `/api/v1/proposals/{proposal_id}/documents/{document_id}` | Read classified document metadata |
| GET | `/api/v1/proposals/{proposal_id}/documents/{document_id}/download` | Download a classified proposal document |
| DELETE | `/api/v1/proposals/{proposal_id}/documents/{document_id}` | Delete a classified proposal document |

## Request / Response schemas (schemas.py)
- `ProposalCreate` — request body for creating a technical offer variant; only `lead_id` and `name` are required at creation; `created_by`, `current_stage`, `loss_reason`, `proposed_at`, and `created_at` are service-controlled
- `ProposalUpdate` — partial update body for non-terminal proposals; PV details are nested under `pv_system`, and BESS details are nested under `bess_system`
- `ProposalPVSystemPayload`, `ProposalBESSSystemPayload` — nested request DTOs for one-to-one subtype detail rows
- `ProposalStageChange` — request body for non-terminal stage movement
- `ProposalLost` — request body for terminal lost outcome; `loss_reason` is required
- `ProposalRead` — public proposal response including structured `installation_address`, nested `pv_system` / `bess_system`, `is_complete`, `missing_required_fields`, stage, terminal fields, creator, and timestamps
- `ProposalCommercialDocumentRead` — public metadata for the commercial proposal PDF
- `ProposalDocumentRead` — public metadata for cost, technical, or other classified proposal documents

## Dependencies
- **Internal:** [[leads]], [[pipeline]], [[users]], [[technical-visits]]
- **Core:** [[core]], [[api-v1]]

## Business rules / invariants
- One Lead can have multiple Proposals.
- Only one Proposal per Lead can be `WON`.
- When a Proposal moves to `WON`, active siblings automatically move to `SUPERSEDED` in the same transaction.
- `loss_reason` is required when a Proposal moves to `LOST`.
- Proposal state determines Lead outcome.
- Proposals can reference technical visit evidence through `ProposalTechnicalVisit`, but visits remain Lead-scoped.
- Proposals can only be created for leads owned by the authenticated user.
- Proposals cannot be created for closed leads.
- `lead_id` and `name` are the only fields required to create a `DRAFT`.
- All common fields are required before a proposal can move beyond `DRAFT`: `version`, full installation address, `tariff`, `contracted_demand`, `system_type`, `total_price`, `annual_savings`, `currency`, `estimated_cost`, `expected_profit`, `submitted_at`, and `valid_until`.
- `PV` proposals require the PV field group before leaving `DRAFT`: panels, inverters, surface type, AC power, system size, oversizing, annual kWh, estimated savings, connection mode, `cost_watt`, and `price_watt`.
- `BESS` proposals require the BESS field group before leaving `DRAFT`: battery model/count/power/storage, primary use, technical notes, `cost_kwh`, and `price_kwh`.
- `HIBRID` proposals require both the PV and BESS field groups before leaving `DRAFT`, including all four unit economics fields.
- Protected price fields require price-specific permissions: setting an empty price field requires `crm.proposals.price.set`; changing an established price field requires `crm.proposals.price.update`.
- Default `tech` users can update assigned Proposals but cannot set or change protected price fields.
- Later proposal work: `price_watt` and `price_kwh` must be calculated and rounded to 4 decimal places instead of being freely edited unit fields.
- `PV` details live only in `proposal_pv_system`; `BESS` details live only in `proposal_bess_system`.
- `PV` proposals cannot carry BESS detail rows, and `BESS` proposals cannot carry PV detail rows.
- Proposal terminal actions require a proposal that has reached at least `SENT`.
- `SENT` assigns `proposed_at` the first time the proposal is sent.
- Terminal proposals (`WON`, `LOST`, `SUPERSEDED`) cannot be updated, moved, deleted, or terminally acted on again.
- If the last active proposal for a lead becomes `LOST`, the lead closes as `CLOSED_LOST`.
- Stage changes are applied through [[pipeline]] so `stage_transition` receives append-only audit rows.
- The commercial proposal PDF is kept in a dedicated document collection; cost and technical documents use `ProposalDocument.classification`.
- If a technical visit changes assumptions after a Proposal has moved beyond `DRAFT`, create a new Proposal version and link that version to the visit instead of silently changing the already-sent Proposal.
- Authorization: `sales` users have read-only access to Proposals and Proposal documents associated with assigned Leads.
- Authorization: `tech` users have full non-price Proposal access only for assigned Proposals.

## Related decisions
[[2026-05-25-outcome-lives-in-proposal]], [[2026-05-25-domain-by-business-not-layer]], [[2026-05-25-sqlmodel-vs-pydantic-strategy]], [[2026-05-29-technical-visits-as-lead-subprocess]], [[2026-06-01-verp-identity-crm-permissions]]

## Known technical debt
None documented.

## Maintainer notes
These records were previously called "projects"; the specification uses "proposals" because there is no strict project until a proposal is won.
The implementation lives under `CRM/src/domains/proposals/`, is mounted in `CRM/src/api/v1/router.py`, and is covered by unit tests in `CRM/tests/unit/domains/proposals/` plus integration tests in `CRM/tests/integration/api/`.
The project now includes an initial Alembic schema migration. Development SQLite databases created before that baseline should be recreated from Alembic or explicitly stamped only after confirming their schema matches the baseline.
