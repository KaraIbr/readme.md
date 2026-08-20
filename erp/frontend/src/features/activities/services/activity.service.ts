import { api } from '@services/api-client'
import type { ActivityRead, ActivityCreate, ActivityUpdate } from '../types'

export async function getActivities(params?: { activity_type?: string }): Promise<ActivityRead[]> {
  const { data } = await api.get<ActivityRead[]>('/activities/', { params })
  return data
}

export async function getActivity(id: number): Promise<ActivityRead> {
  const { data } = await api.get(`/activities/${id}`)
  return data
}

export async function createActivity(body: ActivityCreate): Promise<ActivityRead> {
  const { data } = await api.post('/activities/', body)
  return data
}

export async function updateActivity(id: number, body: ActivityUpdate): Promise<ActivityRead> {
  const { data } = await api.patch(`/activities/${id}`, body)
  return data
}

export async function completeActivity(id: number): Promise<ActivityRead> {
  const { data } = await api.post(`/activities/${id}/complete`)
  return data
}

export async function deleteActivity(id: number): Promise<void> {
  await api.delete(`/activities/${id}`)
}
