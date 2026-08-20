import { describe, it, expect } from 'vitest'
import { api } from '../../../test/mocks/api-client'
import {
  getPermissionCatalog,
  getUserPermissions,
  assignUserRole,
  grantCrmAccess,
  updateUserPermissionOverrides,
} from '../services/permissions.service'

describe('permissions api service', () => {
  it('fetches the permission catalog', async () => {
    const catalog = [{ key: 'crm.leads.read', description: 'Read leads' }]
    api.get.mockResolvedValue({ data: catalog })

    const result = await getPermissionCatalog()

    expect(api.get).toHaveBeenCalledWith('/permissions/')
    expect(result).toEqual(catalog)
  })

  it('fetches permissions for a user', async () => {
    const permissions = {
      role: 'SALES',
      permissions: [],
      grants: [],
      denials: [],
      effective_permissions: ['crm.leads.read'],
    }
    api.get.mockResolvedValue({ data: permissions })

    const result = await getUserPermissions(5)

    expect(api.get).toHaveBeenCalledWith('/permissions/users/5')
    expect(result).toEqual(permissions)
  })

  it('assigns a role to a user', async () => {
    const permissions = { role: 'SALES', permissions: [], grants: [], denials: [], effective_permissions: [] }
    api.post.mockResolvedValue({ data: permissions })

    const result = await assignUserRole(5, 'SALES')

    expect(api.post).toHaveBeenCalledWith('/permissions/users/5/role', { role: 'SALES' })
    expect(result).toEqual(permissions)
  })

  it('grants CRM access to a user', async () => {
    const permissions = { role: 'SALES', permissions: [], grants: [], denials: [], effective_permissions: [] }
    api.post.mockResolvedValue({ data: permissions })

    const result = await grantCrmAccess(5, 'SALES')

    expect(api.post).toHaveBeenCalledWith('/permissions/users/5/grant', { role: 'SALES' })
    expect(result).toEqual(permissions)
  })

  it('updates permission overrides', async () => {
    const permissions = { role: null, permissions: [], grants: [], denials: [], effective_permissions: [] }
    const body = { grant: ['crm.leads.read'], deny: [], clear: [] }
    api.patch.mockResolvedValue({ data: permissions })

    const result = await updateUserPermissionOverrides(5, body)

    expect(api.patch).toHaveBeenCalledWith('/permissions/users/5', body)
    expect(result).toEqual(permissions)
  })
})
