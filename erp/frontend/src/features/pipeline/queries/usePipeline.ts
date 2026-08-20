import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { getTransitions, getPipelineSummary } from '../services/pipeline.service'
import type { PipelineFilters } from '../types'

export function useTransitions(filters?: PipelineFilters) {
  return useQuery({
    queryKey: queryKeys.pipeline.transitions(filters as Record<string, unknown>),
    queryFn: () => getTransitions(filters),
  })
}

export function usePipelineSummary(entityType: 'lead' | 'proposal', entityId: number) {
  return useQuery({
    queryKey: queryKeys.pipeline.summary(entityType, entityId),
    queryFn: () => getPipelineSummary(entityType, entityId),
    enabled: !!entityId,
  })
}
