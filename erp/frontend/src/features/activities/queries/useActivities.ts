import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { getActivities, getActivity } from '../services/activity.service'

export function useActivities(params?: { activity_type?: string }) {
  return useQuery({
    queryKey: queryKeys.activities.list(params as Record<string, unknown> | undefined),
    queryFn: () => getActivities(params),
  })
}

export function useActivity(id: number) {
  return useQuery({
    queryKey: queryKeys.activities.detail(id),
    queryFn: () => getActivity(id),
    enabled: !!id,
  })
}
