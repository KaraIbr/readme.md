export interface PaginatedResponse<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface ApiError {
  status: number
  code: string
  message: string
  details?: Record<string, string[]>
}

export interface SelectOption<T = string> {
  label: string
  value: T
}

export type SortDirection = 'asc' | 'desc'

export interface SortConfig {
  field: string
  direction: SortDirection
}

export interface FilterConfig {
  field: string
  value: unknown
  operator?: 'eq' | 'neq' | 'contains' | 'gt' | 'gte' | 'lt' | 'lte' | 'in'
}
