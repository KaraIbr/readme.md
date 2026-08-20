# Guide: CRM Permissions

## Purpose
CRM authorization uses role templates, user-level overrides, and resource scope. A user must have the required permission and must be allowed to access the target resource.

IAM owns users, authentication, account status, IAM permissions, and service access grants such as `crm`. CRM owns CRM-specific roles, permission overrides, and resource scopes.

## Vocabulary
| Term | Meaning |
|---|---|
| IAM user | Central user account shared by CRM and future services |
| IAM service access | IAM-owned grant that lets a user enter a VERP service such as `crm` |
| CRM access | CRM role and active CRM authorization state for one IAM user |
| IAM permission | Central action key such as `iam.users.create` |
| Role | Template set of CRM permissions |
| Permission | One action key such as `crm.leads.read` |
| Override | User-specific grant or deny for one permission |
| Scope | Resource boundary such as `all`, `assigned_sales`, or `assigned_tech` |
| Effective permissions | Role permissions plus grants minus denials |

## Effective Permission Rule
```text
effective_permissions = role_permissions + user_grants - user_denies
```

Authorization must then check resource scope. For example, `crm.proposals.read` allows reading proposals only if the user also has scope over that proposal.

## Role Templates
| Role | Default permissions | Scope |
|---|---|---|
| `admin` | All CRM permissions | `all` |
| `manager` | All CRM permissions | `all`, with guardrails |
| `sales` | Contacts, Leads, Lead documents, Lead interactions, Agent; read-only Proposals and TechnicalVisits derived from assigned Leads | `assigned_sales` |
| `tech` | Proposals, TechnicalVisits, Agent; read-only Contacts, Leads, Lead documents, and Lead electricity bills derived from assigned Proposal or Visit scope; no Lead interactions and no price changes | `assigned_tech` |

Managers can manage CRM permissions for other non-admin users, but only within their own effective permission set. They cannot modify their own permissions or role, cannot modify admin users, and cannot grant permissions they do not have.

## Permission Catalog
Use stable permission keys in code, seed data, tests, and documentation.

| Permission | Meaning |
|---|---|
| `crm.permissions.read` | Read CRM permission catalog and effective permissions |
| `crm.permissions.manage` | Grant or deny CRM permissions within manager/admin guardrails |
| `crm.roles.assign` | Assign CRM role templates within manager/admin guardrails |
| `crm.contacts.create` | Create Contacts and contact subrecords |
| `crm.contacts.read` | Read Contacts, promoters, profiles, and company people |
| `crm.contacts.update` | Update Contacts, promoters, profiles, and company people |
| `crm.contacts.delete` | Delete Contacts, promoters, or company people when business rules allow |
| `crm.leads.create` | Create Leads |
| `crm.leads.read` | Read Leads |
| `crm.leads.update` | Update open Leads |
| `crm.leads.delete` | Delete open Leads |
| `crm.leads.assign` | Assign or transfer sales follow-up for a Lead |
| `crm.leads.stage.update` | Move non-terminal Lead stage |
| `crm.leads.close` | Manually close a Lead when business rules allow |
| `crm.leads.documents.create` | Upload general Lead documents |
| `crm.leads.documents.read` | Read or download general Lead documents |
| `crm.leads.documents.delete` | Delete general Lead documents |
| `crm.leads.electricity_bills.create` | Upload Lead electricity bills |
| `crm.leads.electricity_bills.read` | Read or download Lead electricity bills |
| `crm.leads.electricity_bills.delete` | Delete Lead electricity bills |
| `crm.leads.interactions.create` | Create Lead interactions |
| `crm.leads.interactions.read` | Read Lead interactions |
| `crm.leads.interactions.update` | Update Lead interactions |
| `crm.leads.interactions.delete` | Delete Lead interactions |
| `crm.proposals.create` | Create Proposals |
| `crm.proposals.read` | Read Proposals |
| `crm.proposals.update` | Update non-terminal Proposal fields except protected price fields |
| `crm.proposals.delete` | Delete non-terminal Proposals |
| `crm.proposals.assign_tech` | Assign technical users to Proposals |
| `crm.proposals.stage.update` | Move non-terminal Proposal stage |
| `crm.proposals.mark_won` | Mark Proposal as won |
| `crm.proposals.mark_lost` | Mark Proposal as lost |
| `crm.proposals.price.set` | Set an empty protected Proposal price field |
| `crm.proposals.price.update` | Change an already established protected Proposal price field |
| `crm.proposals.commercial_documents.create` | Upload commercial proposal PDFs |
| `crm.proposals.commercial_documents.read` | Read or download commercial proposal PDFs |
| `crm.proposals.commercial_documents.delete` | Delete commercial proposal PDFs |
| `crm.proposals.documents.create` | Upload classified Proposal documents |
| `crm.proposals.documents.read` | Read or download classified Proposal documents |
| `crm.proposals.documents.delete` | Delete classified Proposal documents |
| `crm.proposals.technical_visits.link` | Link Proposal evidence to TechnicalVisits |
| `crm.proposals.technical_visits.read` | Read Proposal-to-TechnicalVisit links |
| `crm.proposals.technical_visits.unlink` | Remove Proposal-to-TechnicalVisit links |
| `crm.technical_visits.create` | Create TechnicalVisits |
| `crm.technical_visits.read` | Read TechnicalVisits |
| `crm.technical_visits.update` | Update requested or scheduled TechnicalVisits |
| `crm.technical_visits.assign` | Assign technical visit users |
| `crm.technical_visits.complete` | Complete TechnicalVisits |
| `crm.technical_visits.cancel` | Cancel TechnicalVisits |
| `crm.technical_visits.attachments.create` | Upload TechnicalVisit attachments |
| `crm.technical_visits.attachments.read` | Read or download TechnicalVisit attachments |
| `crm.technical_visits.attachments.delete` | Delete TechnicalVisit attachments |
| `crm.pipeline.read` | Read pipeline transitions and summaries |
| `crm.agent.chat` | Use the CRM agent inside the user's allowed scope |

Central user creation is an IAM concern, not a CRM permission. CRM `manager` never creates IAM users.

Current IAM permissions live in the IAM service:

| Permission | Meaning |
|---|---|
| `iam.users.create` | Create central VERP users |
| `iam.permissions.read` | Read IAM user permissions |
| `iam.permissions.manage` | Grant or deny IAM permissions within guardrails |
| `iam.services.manage` | Grant access to services such as `crm` |

## Sales Scope
Sales users work through active Lead assignment:
- A sales user may have one or more assigned Leads.
- A Lead should have one active sales follow-up owner at a time.
- Assigning a Lead to another sales user removes the previous sales user's Lead scope.
- Sales users can create Contacts and Leads, but if they create a Lead assigned to another sales user, the creator does not keep access by virtue of creation.
- Contact access for sales is derived from assigned Leads. If a Contact has no active Lead, use the Contact's current assigned owner until a Lead assignment exists.
- Sales users can read Proposals, Proposal documents, TechnicalVisits, and TechnicalVisit attachments only when they are associated with an assigned Lead.
- Sales users do not mutate Proposals or TechnicalVisits.

Current implementation updates `Lead.owner_id` when sales follow-up is assigned or transferred, and also records the assignment history in `LeadAssignment`. Contact access for sales is derived from active Lead ownership; if a Contact has no Leads, the creator can still access it.

## Tech Scope
Tech users work through technical assignment:
- Proposal scope comes from `ProposalAssignment`.
- TechnicalVisit scope comes from `TechnicalVisitAssignee.user_id`.
- Lead and Contact read scope is derived from assigned Proposals or assigned TechnicalVisits.
- Tech users can read Lead documents and electricity bills related to their assigned work.
- Tech users cannot read Lead interactions.
- Tech users can update Proposals and TechnicalVisits inside their assignment scope, except protected price fields.
- Tech users can use the agent only within the same assigned technical scope.

## Proposal Price Rules
Protected price fields:
- `Proposal.total_price`
- `ProposalPVSystem.price_watt`
- `ProposalBESSSystem.price_kwh`

General Proposal update permission does not authorize changing protected price fields.

Rules:
- Setting an empty protected price field requires `crm.proposals.price.set`.
- Changing a non-empty protected price field requires `crm.proposals.price.update`.
- Default `admin` and `manager` role templates include both price permissions.
- Default `tech` role template does not include price permissions.
- Default `sales` role template cannot mutate Proposals.

Do not add a separate price table for the first implementation. Add `ProposalPricingRevision` only if CRM needs formal pricing history, approvals, or commercial revision audit.

Later proposal work: `price_watt` and `price_kwh` must be calculated from proposal values and rounded to 4 decimal places. They should not remain freely edited unit fields once calculation rules are implemented.

## Agent Rules
The agent has no independent authority.
- It must call the same authorization service used by REST.
- It must filter searches by the user's effective resource scope.
- It must not expose Lead interactions to `tech` users.
- It must not mutate without explicit confirmation and the required permission.
- It must not change protected price fields without price permission.

## Current Implementation Status
Implemented:
- CRM read-only reference to IAM users via `iam_user.id`.
- IAM service access check for the `crm` service key.
- CRM role storage through `CRMUserAccess`.
- CRM `tech` role in CRM access.
- Code-defined permission catalog and role templates in [[permissions]].
- User-specific permission overrides through `CRMUserPermissionOverride`.
- `LeadAssignment` and `ProposalAssignment` tables.
- `TechnicalVisitAssignee.user_id` as technical visit scope.
- Centralized resource-scope helpers for Contacts, Leads, Proposals, and TechnicalVisits.
- REST permission checks for Contacts, Leads, Proposals, TechnicalVisits, Pipeline, and Agent chat.
- Proposal protected price checks for `total_price`, `price_watt`, and `price_kwh`.
- Agent reads/searches inherit service-level scope filtering.
- Integration coverage for sales transfer, tech scope, Lead interaction blocking, and protected price blocking.

Remaining:
- Persist permission catalog and role-template membership as seed data if runtime administration of templates is needed.
- Add Proposal assignment removal if operationally required.
- Implement calculated `price_watt` and `price_kwh` rounded to four decimals.

## Related Pages
[[permissions]], [[users]], [[contacts]], [[leads]], [[proposals]], [[technical-visits]], [[agent]], [[2026-06-01-verp-identity-crm-permissions]]
