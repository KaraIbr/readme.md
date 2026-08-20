import type { PaginatedResponse } from '@shared/types'

export function wrapPaginated<T>(items: T[]): PaginatedResponse<T> {
  return {
    items,
    total: items.length,
    limit: items.length,
    offset: 0,
  }
}
