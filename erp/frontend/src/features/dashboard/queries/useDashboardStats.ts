import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { getDashboardStats } from '../services/dashboard.service'

export function useDashboardStats() {
  return useQuery({
    queryKey: queryKeys.dashboard.stats,
    queryFn: getDashboardStats,
  })
}
