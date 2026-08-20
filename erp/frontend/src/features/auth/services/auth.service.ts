import { api } from '@services/api-client'
import type { LoginRequest, CurrentUser } from '../types'

export async function login(body: LoginRequest): Promise<void> {
  const formData = new URLSearchParams()
  formData.append('username', body.username)
  formData.append('password', body.password)
  await api.post('/identity/auth/login', formData.toString(), {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
}

export async function getCurrentUser(): Promise<CurrentUser> {
  const { data } = await api.get<CurrentUser>('/identity/users/me')
  return data
}

export async function logout(): Promise<void> {
  await api.post('/identity/auth/logout')
}
