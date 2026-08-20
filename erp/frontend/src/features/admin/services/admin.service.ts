import { api } from '@services/api-client'
import type { AdminUser, AdminUserCreate, AdminUserUpdate } from '../types'

export async function getUsers(): Promise<AdminUser[]> {
  const { data } = await api.get('/identity/users/')
  return data
}

export async function getUser(id: number): Promise<AdminUser> {
  const { data } = await api.get(`/identity/users/${id}`)
  return data
}

export async function createUser(body: AdminUserCreate): Promise<AdminUser> {
  const { data } = await api.post('/identity/users/', body)
  return data
}

export async function updateUser(id: number, body: AdminUserUpdate): Promise<AdminUser> {
  const { data } = await api.patch(`/identity/users/${id}`, body)
  return data
}

export async function deleteUser(id: number): Promise<void> {
  await api.delete(`/identity/users/${id}`)
}
