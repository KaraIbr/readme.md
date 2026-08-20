import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { getTasks, getTask } from '../services/task.service'
import type { TaskFilters } from '../types'

export function useTasks(filters?: TaskFilters) {
  return useQuery({
    queryKey: queryKeys.tasks.list(filters as Record<string, unknown>),
    queryFn: () => getTasks(filters),
  })
}

export function useTask(id: number) {
  return useQuery({
    queryKey: queryKeys.tasks.detail(id),
    queryFn: () => getTask(id),
    enabled: !!id,
  })
}
