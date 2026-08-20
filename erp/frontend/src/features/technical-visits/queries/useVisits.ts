import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import {
  getVisits,
  getVisit,
  getVisitAttachments,
} from '../services/visit.service'
import type { VisitFilters } from '../types'

export function useVisitList(filters?: VisitFilters) {
  return useQuery({
    queryKey: queryKeys.technicalVisits.list(filters as Record<string, unknown>),
    queryFn: () => getVisits(filters),
  })
}

export function useVisit(id: number) {
  return useQuery({
    queryKey: queryKeys.technicalVisits.detail(id),
    queryFn: () => getVisit(id),
    enabled: !!id,
  })
}

export function useVisitAttachments(visitId: number) {
  return useQuery({
    queryKey: queryKeys.technicalVisits.attachments(visitId),
    queryFn: () => getVisitAttachments(visitId),
    enabled: !!visitId,
  })
}
