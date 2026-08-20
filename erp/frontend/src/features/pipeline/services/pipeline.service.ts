import { api } from '@services/api-client'
import type { StageTransitionRead, PipelineSummary, PipelineFilters } from '../types'

export async function getTransitions(params?: PipelineFilters): Promise<StageTransitionRead[]> {
  const { data } = await api.get('/pipeline/transitions', { params })
  return data
}

export async function getPipelineSummary(
  entityType: 'lead' | 'proposal',
  entityId: number,
): Promise<PipelineSummary> {
  const { data } = await api.get(`/pipeline/summary/${entityType}/${entityId}`)
  return data
}
