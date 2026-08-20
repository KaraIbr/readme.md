# Domain: Permissions

**Path:** `src/domains/permissions/`
**Responsibility:** Owns CRM authorization records, CRM-specific permission catalog, role templates, user permission overrides, and resource authorization checks; it does not own IAM user identity, IAM permissions, IAM service access grants, or CRM business lifecycle rules.
**Status:** In development; role templates, user overrides, assignments, and route/service checks implemented

## Purpose
Permissions make CRM authorization explicit. Roles provide default permission sets, but individual users can receive explicit permission grants or denials. The domain also defines resource scope rules so `sales` and `tech` users only access assigned CRM records.

The sibling IAM service owns users, authentication, account status, IAM permissions, and service access grants. CRM-specific authorization lives in this domain and applies only after IAM has created the user and granted service access for `crm`.

## Data model
Implemented CRM authorization entities:
- `CRMUserAccess` - CRM role (`admin`, `manager`, `sales`, `tech`) and active CRM authorization state for an IAM user.
- `CRMUserPermissionOverride` - user-specific `grant` or `deny` for one permission key, including actor and timestamp metadata.
- `LeadAssignment` - active sales assignment for a Lead, with assignment history. At most one active sales follow-up owner exists per Lead.
- `ProposalAssignment` - assignment of a Proposal to one or more technical users.

Existing entities used by authorization:
- `TechnicalVisitAssignee.user_id` grants `tech` scope over assigned technical visits.
- `ProposalTechnicalVisit` links visit scope to proposal evidence where needed.
- `Lead.owner_id` is updated when active sales follow-up is assigned or transferred. Contact access for sales is derived from active Lead ownership; a Contact with no Leads remains visible to its creator.

Not implemented yet:
- Seeded database tables for permission catalog and role membership; role templates and permission catalog are currently code-defined in `service.py`.
- Proposal assignment removal endpoint.

## Public interface (service.py)
Implemented service functions:
- `role_permissions(role) -> set[str]` - returns default permission keys for `admin`, `manager`, `sales`, and `tech`.
- `get_crm_user_access(session, user_id) -> CRMUserAccess | None` - returns active CRM authorization for one IAM user after IAM service access is valid.
- `effective_permissions(session, user_id) -> set[str]` - combines role permissions, grants, and denials.
- `require_permission(session, user_id, permission) -> None` - rejects users without an effective permission.
- `can_manage_user(session, actor_id, target_user_id, requested_permissions=None) -> tuple[User, User]` - enforces manager/admin guardrails before permission or role changes.
- `set_user_permission_overrides(...)` - grants, denies, or clears user-specific CRM permissions.
- `assign_role(...)` - applies a CRM role template with guardrails.
- `assign_lead(...)` - transfers active sales follow-up and updates `Lead.owner_id`.
- `assign_proposal(...)` - assigns Proposal work to a `tech` user.
- `user_can_access_contact/lead/proposal/technical_visit(...)` - central resource-scope helpers used by REST services, pipeline, and agent-backed reads.

## Router endpoints
Implemented CRM administration endpoints:

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/permissions` | List CRM permission catalog |
| GET | `/api/v1/permissions/users/{user_id}` | Read one user's CRM role, overrides, and effective permissions |
| PATCH | `/api/v1/permissions/users/{user_id}` | Grant or deny individual CRM permissions |
| POST | `/api/v1/permissions/users/{user_id}/role` | Assign a CRM role template |
| POST | `/api/v1/leads/{lead_id}/assignment` | Assign or transfer sales follow-up for a Lead |
| POST | `/api/v1/proposals/{proposal_id}/assignments` | Assign a technical user to a Proposal |

IAM user creation is not a CRM endpoint. CRM may reference users only after IAM has created them, granted active service access for `crm`, and CRM access has been assigned through this domain.

## Request / Response schemas (schemas.py)
Implemented DTOs:
- `PermissionRead` - catalog entry.
- `UserPermissionsRead` - CRM role, role permissions, explicit grants/denials, and effective permission keys.
- `UserPermissionPatch` - grants, denials, and clears to apply.
- `RoleAssignment` - target CRM role.
- `LeadAssignmentCreate` - assigned sales user.
- `ProposalAssignmentCreate` - assigned technical user.
- `LeadAssignmentRead` and `ProposalAssignmentRead` - active assignment responses.

## Dependencies
- **Internal:** [[users]], [[contacts]], [[leads]], [[proposals]], [[technical-visits]], [[agent]]
- **Core:** [[core]], [[api-v1]]
- **External IAM:** central users, IAM permissions, and service access grants

## Business rules / invariants
- Roles are permission templates, not hard-coded authorization shortcuts.
- An IAM user has no CRM authority until IAM service access for `crm` is active and `CRMUserAccess` exists and is active.
- User-specific denies override role permissions and user-specific grants.
- An effective permission does not bypass resource scope.
- `admin` has every CRM permission with global scope.
- `manager` has every CRM permission, but cannot create IAM users, cannot modify admin accounts, cannot modify its own permissions or role, and cannot grant a permission it does not effectively have.
- `sales` users operate only on assigned Leads and derived Contacts, Proposals, TechnicalVisits, documents, and agent context.
- `tech` users operate only on assigned Proposals and TechnicalVisits, with derived read access to related Contacts, Leads, and Lead documents, but no Lead interactions.
- Proposal price fields require separate price permissions from general Proposal update permission.
- The agent must use the same permission and resource-scope checks as REST endpoints.

## Related decisions
[[2026-06-01-verp-identity-crm-permissions]], [[2026-05-25-domain-by-business-not-layer]]

## Known technical debt
- IAM service access is read from IAM-owned service grants; CRM still owns CRM roles and effective CRM permissions.
- Permission catalog and role templates are code-defined rather than seeded tables.
- Proposal assignment removal is not exposed yet.
- Proposal `price_watt` and `price_kwh` still need later calculated-and-rounded behavior.

## Maintainer notes
Keep permission checks centralized. Do not spread role conditionals through routers or individual domain services.
