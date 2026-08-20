import { api } from '@services/api-client'
import type { UserPermissions } from '../../auth/types'

export interface PermissionCatalogEntry {
  key: string
  description: string
}

export interface UserPermissionOverride {
  grant: string[]
  deny: string[]
  clear: string[]
}

export async function getPermissionCatalog(): Promise<PermissionCatalogEntry[]> {
  const { data } = await api.get<PermissionCatalogEntry[]>('/permissions/')
  return data
}

export async function getUserPermissions(userId: number): Promise<UserPermissions> {
  const { data } = await api.get<UserPermissions>(`/permissions/users/${userId}`)
  return data
}

export async function assignUserRole(userId: number, role: string): Promise<UserPermissions> {
  const { data } = await api.post<UserPermissions>(`/permissions/users/${userId}/role`, { role })
  return data
}

export async function grantCrmAccess(userId: number, role: string): Promise<UserPermissions> {
  const { data } = await api.post<UserPermissions>(`/permissions/users/${userId}/grant`, { role })
  return data
}

export async function updateUserPermissionOverrides(
  userId: number,
  body: UserPermissionOverride,
): Promise<UserPermissions> {
  const { data } = await api.patch<UserPermissions>(`/permissions/users/${userId}`, body)
  return data
}
