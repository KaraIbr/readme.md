import { api } from '@services/api-client'
import type { ProfileUpdate } from '../types'

export async function updateProfile(id: number, body: ProfileUpdate): Promise<void> {
  const payload: Record<string, unknown> = {}
  if (body.full_name !== undefined) payload.full_name = body.full_name
  if (body.email !== undefined) payload.email = body.email
  await api.patch(`/identity/users/${id}`, payload)
}
