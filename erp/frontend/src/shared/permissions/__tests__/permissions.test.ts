import { describe, it, expect } from 'vitest'
import {
  CrmPermissions,
  IamPermissions,
  NavPermissionRequirements,
  Permissions,
  canAny,
  roleDefaultPath,
} from '../index'

describe('canAny', () => {
  it('returns true when no permission is required', () => {
    expect(canAny(new Set(), undefined)).toBe(true)
  })

  it('returns true when required list is empty', () => {
    expect(canAny(new Set(), [])).toBe(true)
  })

  it('returns true when a single required permission is present', () => {
    expect(canAny(new Set(['crm.leads.read']), 'crm.leads.read')).toBe(true)
  })

  it('returns false when a single required permission is absent', () => {
    expect(canAny(new Set(['crm.contacts.read']), 'crm.leads.read')).toBe(false)
  })

  it('returns true when any of the required permissions is present', () => {
    const perms = new Set(['crm.leads.read'])
    expect(canAny(perms, ['crm.leads.read', 'crm.proposals.read'])).toBe(true)
  })

  it('returns false when none of the required permissions is present', () => {
    const perms = new Set(['crm.contacts.read'])
    expect(canAny(perms, ['crm.leads.read', 'crm.proposals.read'])).toBe(false)
  })
})

describe('roleDefaultPath', () => {
  it('routes TECH to proposals', () => {
    expect(roleDefaultPath('TECH')).toBe('/proposals')
  })

  it('routes SALES to pipeline', () => {
    expect(roleDefaultPath('SALES')).toBe('/pipeline')
  })

  it('routes ADMIN and MANAGER to dashboard', () => {
    expect(roleDefaultPath('ADMIN')).toBe('/dashboard')
    expect(roleDefaultPath('MANAGER')).toBe('/dashboard')
  })

  it('falls back to dashboard for null', () => {
    expect(roleDefaultPath(null)).toBe('/dashboard')
  })
})

describe('permission keys', () => {
  it('exposes CRM permission keys aligned with backend', () => {
    expect(CrmPermissions.contacts.create).toBe('crm.contacts.create')
    expect(CrmPermissions.leads.stageUpdate).toBe('crm.leads.stage.update')
    expect(CrmPermissions.leads.documents.delete).toBe('crm.leads.documents.delete')
    expect(CrmPermissions.proposals.assignTech).toBe('crm.proposals.assign_tech')
    expect(CrmPermissions.proposals.technicalVisits.link).toBe('crm.proposals.technical_visits.link')
    expect(CrmPermissions.technicalVisits.complete).toBe('crm.technical_visits.complete')
    expect(CrmPermissions.pipeline.read).toBe('crm.pipeline.read')
    expect(CrmPermissions.permissions.assignRole).toBe('crm.roles.assign')
    expect(CrmPermissions.agent.chat).toBe('crm.agent.chat')
  })

  it('exposes IAM permission keys', () => {
    expect(IamPermissions.users.create).toBe('iam.users.create')
    expect(IamPermissions.permissions.manage).toBe('iam.permissions.manage')
    expect(IamPermissions.services.read).toBe('iam.services.read')
  })

  it('keeps the deprecated Permissions mapping in sync', () => {
    expect(Permissions.contacts.view).toBe(CrmPermissions.contacts.read)
    expect(Permissions.leads.edit).toBe(CrmPermissions.leads.update)
    expect(Permissions.admin.users.role).toBe('crm.roles.assign')
  })

  it('maps nav items to their minimum permissions', () => {
    expect(NavPermissionRequirements.dashboard).toEqual([])
    expect(NavPermissionRequirements.pipeline).toBe(CrmPermissions.pipeline.read)
    expect(NavPermissionRequirements.leads).toBe(CrmPermissions.leads.read)
    expect(NavPermissionRequirements['technical-visits']).toBe(CrmPermissions.technicalVisits.read)
    expect(NavPermissionRequirements.contacts).toBe(CrmPermissions.contacts.read)
    expect(NavPermissionRequirements.companies).toBe(CrmPermissions.contacts.read)
    expect(NavPermissionRequirements.agent).toBe(CrmPermissions.agent.chat)
  })
})
