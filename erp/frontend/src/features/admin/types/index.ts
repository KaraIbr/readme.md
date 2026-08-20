export interface AdminUser {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
  role: string | null
  last_login: string | null
  created_at: string
}

export interface AdminUserCreate {
  email: string
  password: string
  full_name?: string
  role: string
}

export interface AdminUserUpdate {
  email?: string
  full_name?: string
  role?: string
  is_active?: boolean
}

export const ADMIN_ROLES = ['ADMIN', 'MANAGER', 'SALES', 'TECH'] as const
export type AdminRole = typeof ADMIN_ROLES[number]
