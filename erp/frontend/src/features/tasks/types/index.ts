export const TASK_STATUSES = ['TODO', 'IN_PROGRESS', 'DONE', 'CANCELLED'] as const
export type TaskStatus = (typeof TASK_STATUSES)[number]

export const TASK_PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'URGENT'] as const
export type TaskPriority = (typeof TASK_PRIORITIES)[number]

export interface TaskRead {
  id: number
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  due_date: string | null
  completed_at: string | null
  contact_id: number | null
  lead_id: number | null
  assigned_to: number | null
  created_by: number
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string | null
  status?: TaskStatus
  priority?: TaskPriority
  due_date?: string | null
  contact_id?: number | null
  lead_id?: number | null
  assigned_to?: number | null
}

export interface TaskUpdate {
  title?: string
  description?: string | null
  priority?: TaskPriority
  due_date?: string | null
  assigned_to?: number | null
}

export interface TaskFilters {
  status?: TaskStatus
  priority?: TaskPriority
  limit?: number
  offset?: number
}

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  TODO: 'To Do',
  IN_PROGRESS: 'In Progress',
  DONE: 'Done',
  CANCELLED: 'Cancelled',
}

export const TASK_STATUS_VARIANTS: Record<TaskStatus, 'default' | 'info' | 'success' | 'warning' | 'danger'> = {
  TODO: 'default',
  IN_PROGRESS: 'info',
  DONE: 'success',
  CANCELLED: 'danger',
}

export const TASK_PRIORITY_LABELS: Record<TaskPriority, string> = {
  LOW: 'Low',
  MEDIUM: 'Medium',
  HIGH: 'High',
  URGENT: 'Urgent',
}

export const TASK_PRIORITY_VARIANTS: Record<TaskPriority, 'default' | 'info' | 'warning' | 'danger'> = {
  LOW: 'default',
  MEDIUM: 'info',
  HIGH: 'warning',
  URGENT: 'danger',
}
