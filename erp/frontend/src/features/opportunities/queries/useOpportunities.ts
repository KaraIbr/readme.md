import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { getOpportunities, getOpportunity } from '../services/opportunity.service'

export function useOpportunities(params?: { stage?: string }) {
  return useQuery({
    queryKey: queryKeys.opportunities.list(params as Record<string, unknown> | undefined),
    queryFn: () => getOpportunities(params),
  })
}

export function useOpportunity(id: number) {
  return useQuery({
    queryKey: queryKeys.opportunities.detail(id),
    queryFn: () => getOpportunity(id),
    enabled: !!id,
  })
}
