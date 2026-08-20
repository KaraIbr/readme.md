import type { ReactNode } from 'react'
import { useEffectivePermissions } from '../queries/useUserPermissions'

interface PermissionGuardProps {
  permission: string
  children: ReactNode
  fallback?: ReactNode
}

export function PermissionGuard({ permission, children, fallback = null }: PermissionGuardProps) {
  const { can } = useEffectivePermissions()

  if (can(permission)) {
    return <>{children}</>
  }

  return <>{fallback}</>
}
