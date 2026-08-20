export interface LoginRequest {
  username: string
  password: string
}

export interface CurrentUser {
  id: number
  email: string
  full_name: string | null
  is_active: boolean
}

export interface UserPermissions {
  role: string | null
  permissions: string[]
  grants: string[]
  denials: string[]
  effective_permissions: string[]
}

export interface AuthState {
  user: CurrentUser | null
  isAuthenticated: boolean
  isLoading: boolean
}

export interface AuthContextValue extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
}
