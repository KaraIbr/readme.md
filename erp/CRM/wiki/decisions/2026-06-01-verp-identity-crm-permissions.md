# ADR: IAM Users and CRM Permissions

**Date:** 2026-06-01
**Status:** Accepted

## Context
VERP hosts CRM, IAM, and future services that must share the same human users. CRM also needs detailed domain permissions: roles should provide default permission sets, but individual users must be able to receive explicit permission grants or denials. Some permissions depend on assignment to a Lead, Proposal, or TechnicalVisit rather than on global role membership alone.

Central users, JWT authentication, IAM permissions, and service access grants belong to the sibling IAM service. CRM stores CRM access/roles under [[permissions]] and keeps a read-only IAM user reference under [[users]] so ownership, assignment, and audit fields can point to `iam_user.id`.

## Alternatives considered
- **Keep all users and permissions inside CRM:** Rejected because future VERP services would need to duplicate account lifecycle, authentication, and user administration.
- **Keep a `src/verp` identity module inside CRM:** Rejected because IAM is a sibling VERP service, not a CRM subpackage.
- **Use roles only:** Rejected because a user may need one extra permission or one removed permission without creating a new role for every exception.
- **Put every permission in JWT claims:** Rejected because permissions can be changed individually and should take effect without relying on long-lived tokens carrying stale authorization state.
- **Use global permissions without resource scopes:** Rejected because `sales` and `tech` users must only access assigned Leads, Proposals, TechnicalVisits, and derived records.

## Decision
IAM is the central source of users, authentication, account status, IAM permissions, and service access grants. CRM owns CRM-specific authorization: role templates, permission catalog, per-user CRM permission overrides, and resource assignment checks.

CRM permissions are evaluated as:

```text
effective_permissions = role_permissions + user_grants - user_denies
```

An effective permission is necessary but not always sufficient. The authorization layer must also verify resource scope:
- `admin` has all CRM permissions with global scope.
- `manager` has all CRM permissions and cannot grant permissions they do not have, modify their own permissions, or modify admin accounts. Creating IAM users is not a CRM action.
- `sales` works on assigned Leads and derived Contacts, Proposals, TechnicalVisits, documents, and agent context.
- `tech` works on assigned Proposals and TechnicalVisits, with derived read access to related Contacts, Leads, and lead documents, excluding Lead interactions.

Proposal price editing is a separate field-level permission concern. `total_price`, `price_watt`, and `price_kwh` are protected price fields. Setting an empty price and changing an established price should be checked separately through CRM permissions such as `crm.proposals.price.set` and `crm.proposals.price.update`. Initial implementation does not require a separate pricing table; add one later only if formal pricing history, approval workflow, or commercial revision audit is required.

The agent must use the same CRM authorization service and resource scopes as REST endpoints. It must not expose records outside the authenticated user's assigned scope.

## Consequences
- Expected benefits:
  - One IAM user identity can be reused by CRM and future services.
  - CRM keeps domain-specific permissions close to CRM business rules.
  - Roles remain useful templates without becoming rigid.
  - `sales` and `tech` visibility can be enforced through assignment rather than ad hoc filters.
  - Proposal price changes can be protected independently from other proposal edits.
- Trade-offs or risks accepted:
  - Authorization becomes a first-class domain with its own tables, migrations, tests, and administration endpoints.
  - Services must consistently call the authorization layer before reading or mutating resources.
  - Caching effective permissions must be short-lived or invalidated when overrides change.
  - CRM must validate IAM-created user ids and service access before applying CRM permissions.

## Affected components
[[users]], [[permissions]], [[contacts]], [[leads]], [[proposals]], [[technical-visits]], [[agent]], [[api-v1]], [[core]]
