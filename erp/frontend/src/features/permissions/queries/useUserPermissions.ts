import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { getPermissionCatalog, getUserPermissions } from '../services/permissions.service'
import { useAuth } from '../../auth'

export function usePermissionCatalog() {
  return useQuery({
    queryKey: queryKeys.permissions.catalog,
    queryFn: getPermissionCatalog,
    staleTime: 10 * 60 * 1000,
  })
}

export function useUserPermissions() {
  const { user, isAuthenticated } = useAuth()

  return useQuery({
    queryKey: queryKeys.permissions.user(user?.id ?? 0),
    queryFn: () => getUserPermissions(user!.id),
    enabled: isAuthenticated && !!user?.id,
    staleTime: 5 * 60 * 1000,
    retry: 1,
  })
}

export function useEffectivePermissions() {
  const { data, isError, isLoading, error } = useUserPermissions()
  const perms = new Set(data?.effective_permissions ?? [])

  return {
    role: ((data?.role ?? null)?.toUpperCase() ?? null) as 'ADMIN' | 'MANAGER' | 'SALES' | 'TECH' | null,
    effectivePermissions: perms,
    can: (permission: string) => perms.has(permission),
    permissionsError: isError ? error : null,
    permissionsLoading: isLoading,
    hasCrmAccess: isError ? false : data != null,
  }
}
