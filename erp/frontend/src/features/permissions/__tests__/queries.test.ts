import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { usePermissionCatalog, useUserPermissions, useEffectivePermissions } from '../queries/useUserPermissions'
import { getPermissionCatalog, getUserPermissions } from '../services/permissions.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/permissions.service', () => ({
  getPermissionCatalog: vi.fn(),
  getUserPermissions: vi.fn(),
}))

vi.mock('../../auth', () => ({
  useAuth: () => ({ user: { id: 5 }, isAuthenticated: true }),
}))

const mockedGetPermissionCatalog = vi.mocked(getPermissionCatalog)
const mockedGetUserPermissions = vi.mocked(getUserPermissions)

describe('permission query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the permission catalog', async () => {
    const catalog = [{ key: 'crm.leads.read', description: 'Read leads' }]
    mockedGetPermissionCatalog.mockResolvedValue(catalog)

    const { result } = renderHook(() => usePermissionCatalog(), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(catalog))
  })

  it('loads permissions for the current user', async () => {
    const permissions = {
      role: 'sales',
      permissions: [],
      grants: [],
      denials: [],
      effective_permissions: ['crm.leads.read'],
    }
    mockedGetUserPermissions.mockResolvedValue(permissions)

    const { result } = renderHook(() => useUserPermissions(), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(permissions))
    expect(mockedGetUserPermissions).toHaveBeenCalledWith(5)
  })

  it('derives effective permissions for the current user', async () => {
    mockedGetUserPermissions.mockResolvedValue({
      role: 'sales',
      permissions: [],
      grants: [],
      denials: [],
      effective_permissions: ['crm.leads.read'],
    })

    const { result } = renderHook(() => useEffectivePermissions(), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.hasCrmAccess).toBe(true))
    expect(result.current.role).toBe('SALES')
    expect(result.current.can('crm.leads.read')).toBe(true)
    expect(result.current.can('crm.proposals.read')).toBe(false)
    expect(result.current.permissionsLoading).toBe(false)
    expect(result.current.permissionsError).toBeNull()
  })
})
