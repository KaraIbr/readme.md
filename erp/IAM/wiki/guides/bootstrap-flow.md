# Guide: Bootstrap Flow

## Purpose

Bootstrap creates the first central IAM user and gives that user enough explicit permission to administer IAM.

## Rule

If no users exist, `POST /api/v1/users/` may create the first user without authentication.

That first user receives explicit grants:

```text
iam.users.create
iam.users.read
iam.users.update
iam.users.deactivate
iam.permissions.read
iam.permissions.manage
iam.services.read
iam.services.manage
```

After one user exists, `POST /api/v1/users/` requires `iam.users.create`.

## No Platform-Admin Boolean

Do not implement `is_platform_admin`.

Central authority must be represented as explicit IAM permission grants, so authority can be added or removed per user.

## CRM Onboarding After Bootstrap

Creating the first IAM user does not automatically create CRM authority.

Correct sequence:

1. IAM creates the first central user.
2. IAM grants that user access to service key `crm` through `/api/v1/services`.
3. CRM assigns that user a CRM role, usually `admin`, inside CRM.

This keeps IAM and CRM permissions separate.
