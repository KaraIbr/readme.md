# VERP Frontend (Vite) â€” Development Log

## 2026-06-22 â€” Admin functions complete (users CRUD, roles, permissions)
- **Users CRUD:** Full CRUD via `features/admin/` â€” `AdminUsersPage` with DataTable, inline row editing, create form modal, delete with confirmation. Backed by `services/admin.service.ts` (IAM `/identity/users/`), TanStack Query hooks (`useUsers`, `useUser`, `useCreateUser`, `useUpdateUser`, `useDeleteUser`), and Zod schema validation.
- **Roles:** Three CRM roles â€” `ADMIN`, `MANAGER`, `SALES`. Color-coded Badge display in table, inline role switcher in UserActions, role select in UserForm. Role assignment via `PATCH /identity/users/{id}`.
- **Permissions page built out:** `AdminPermissionsPage` now renders permission catalog from `GET /permissions/`, shows effective permissions per role with grouped display, role template selection, and user-level override grant/deny/clear UI. Connects to CRM permissions backend.
- **Admin navigation:** Admin dashboard (`/admin`) with cards linking to Users, Permissions, Contacts. `/admin/users`, `/admin/permissions`, `/admin/audit`, `/admin/settings`, `/admin/contacts/*` all wired in routes.
- **Pipeline split into LeadBoard + ProposalBoard:** Pipeline page refactored; extracted `LeadBoard` and `ProposalBoard` as reusable components under `features/pipeline/components/`. Each board manages its own stages, transitions, and kanban columns. PipelinePage maintains tab toggle.
- **Missing Required Fields improved:** `ProposalInfoCard` now renders grouped missing fields (Installation Address, PV System, General) with human-readable labels, categorized sections with headings, and icon indicators â€” replaces raw field-name bullet list.

## 2026-06-24 — Auth system fixes (branch: fix/auth-system)
- **Fixed useAuth imports:** AuthGuard.tsx, RoleGuard.tsx, LoginForm.tsx ahora importan useAuth desde hooks/useAuth (no desde providers/AuthProvider). Resuelve: "does not provide an export named 'useAuth'"
- **Fixed can() en useEffectivePermissions:** Reemplazado \can: () => true\ con \can: (permission: string) => perms.has(permission)\ — ahora verifica permisos reales
- **Removed placeholderData:** Eliminado \placeholderData: mockPermissions()\ — ya no se muestra role ADMIN por defecto durante carga/error
- **Fixed RoleGuard:** Ahora usa \useEffectivePermissions().role\ en vez de castear \user.role\ (que siempre era undefined)
- **Fixed role assignment:** AdminUsersPage ahora usa \ssignUserRole(user.id, role)\ ? POST /permissions/users/{id}/role (CRM) en vez de PATCH /identity/users/{id} (IAM)
- **Fixed user creation:** handleCreate ahora asigna el role CRM despues de crear el usuario via \ssignUserRole(newUser.id, data.role)\
- **Added TECH to ADMIN_ROLES:** Agregado TECH a la lista de roles en admin/types, roleVariants, e inline role picker
- **Added AuthGuard to DashboardLayout:** Outlet protegido con AuthGuard — redirige a /login si no autenticado
- **TypeScript:** \	sc --noEmit\ pasa sin errores
