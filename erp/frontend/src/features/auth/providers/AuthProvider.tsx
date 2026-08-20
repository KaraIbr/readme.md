import { createContext, useState, useCallback, useEffect, type ReactNode } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import * as authService from '../services/auth.service'
import type { AuthContextValue, CurrentUser, LoginRequest } from '../types'

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [user, setUser] = useState<CurrentUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    authService.getCurrentUser()
      .then((u) => { if (!cancelled) setUser(u) })
      .catch(() => { if (!cancelled) setUser(null) })
      .finally(() => { if (!cancelled) setIsLoading(false) })
    return () => { cancelled = true }
  }, [])

  const login = useCallback(async (credentials: LoginRequest) => {
    await authService.login(credentials)
    const currentUser = await authService.getCurrentUser()
    setUser(currentUser)
  }, [])

  const logout = useCallback(() => {
    authService.logout().catch(() => {})
    setUser(null)
    queryClient.clear()
    window.location.href = '/login'
  }, [queryClient])

  const value: AuthContextValue = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export { AuthContext, type AuthContextValue }
