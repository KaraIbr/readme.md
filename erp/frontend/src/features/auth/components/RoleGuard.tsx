import type { ReactNode } from 'react'
import { useEffectivePermissions } from '@features/permissions/queries/useUserPermissions'
import type { CRMRole } from '@shared/permissions'

interface RoleGuardProps {
  roles: CRMRole[]
  children: ReactNode
  fallback?: ReactNode
}

export function RoleGuard({ roles, children, fallback = null }: RoleGuardProps) {
  const { role } = useEffectivePermissions()

  if (!role || !roles.includes(role as CRMRole)) {
    return <>{fallback}</>
  }

  return <>{children}</>
}
