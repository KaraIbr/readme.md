import { api } from '@services/api-client'
import type {
  TaskRead,
  TaskCreate,
  TaskUpdate,
  TaskFilters,
  TaskStatus,
} from '../types'

export async function getTasks(params?: TaskFilters): Promise<TaskRead[]> {
  const { data } = await api.get<TaskRead[]>('/tasks/', { params })
  return data
}

export async function getTask(id: number): Promise<TaskRead> {
  const { data } = await api.get<TaskRead>(`/tasks/${id}`)
  return data
}

export async function createTask(body: TaskCreate): Promise<TaskRead> {
  const { data } = await api.post<TaskRead>('/tasks/', body)
  return data
}

export async function updateTask(id: number, body: TaskUpdate): Promise<TaskRead> {
  const { data } = await api.patch<TaskRead>(`/tasks/${id}`, body)
  return data
}

export async function changeTaskStatus(id: number, body: { status: TaskStatus }): Promise<TaskRead> {
  const { data } = await api.post<TaskRead>(`/tasks/${id}/status`, body)
  return data
}

export async function deleteTask(id: number): Promise<void> {
  await api.delete(`/tasks/${id}`)
}
