export interface StageTransitionRead {
  id: number
  entity_type: 'lead' | 'proposal'
  entity_id: number
  from_stage: string | null
  to_stage: string
  transitioned_by: number
  transitioned_at: string
  reason: string | null
  notes: string | null
}

export interface PipelineSummary {
  entity_type: 'lead' | 'proposal'
  entity_id: number
  current_stage: string
  transition_count: number
  last_transition_at: string | null
}

export interface PipelineFilters {
  entity_type?: 'lead' | 'proposal'
  entity_id?: number
  limit?: number
  offset?: number
}

export interface PipelineTransitionPage {
  items: StageTransitionRead[]
  total: number
  limit: number
  offset: number
}
