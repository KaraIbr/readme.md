import type { BadgeVariant } from '@atoms/Badge/Badge'

export type OpportunityStage = 'PROSPECTING' | 'QUALIFIED' | 'PROPOSAL' | 'NEGOTIATION' | 'CLOSED_WON' | 'CLOSED_LOST'

export interface OpportunityRead {
  id: number
  name: string
  contact_id: number
  lead_id: number | null
  value: number | null
  currency: string | null
  current_stage: OpportunityStage
  outcome: string | null
  expected_close_date: string | null
  owner_id: number
  notes: string | null
  created_at: string
  updated_at: string
  closed_at: string | null
}

export interface OpportunityCreate {
  name: string
  contact_id: number
  lead_id?: number | null
  value?: number | null
  currency?: string | null
  expected_close_date?: string | null
  notes?: string | null
}

export interface OpportunityUpdate {
  name?: string
  value?: number | null
  currency?: string | null
  expected_close_date?: string | null
  notes?: string | null
}

export interface OpportunityStageChange {
  stage: OpportunityStage
}

export interface OpportunityClose {
  outcome: 'WON' | 'LOST'
  notes?: string | null
}

export const OPPORTUNITY_STAGES: OpportunityStage[] = [
  'PROSPECTING', 'QUALIFIED', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST',
]

export const STAGE_LABELS: Record<OpportunityStage, string> = {
  PROSPECTING: 'Prospecting',
  QUALIFIED: 'Qualified',
  PROPOSAL: 'Proposal',
  NEGOTIATION: 'Negotiation',
  CLOSED_WON: 'Won',
  CLOSED_LOST: 'Lost',
}

export const STAGE_VARIANTS: Record<OpportunityStage, BadgeVariant> = {
  PROSPECTING: 'default',
  QUALIFIED: 'info',
  PROPOSAL: 'info',
  NEGOTIATION: 'warning',
  CLOSED_WON: 'success',
  CLOSED_LOST: 'danger',
}

export const FORWARD_STAGES: Record<OpportunityStage, OpportunityStage[]> = {
  PROSPECTING: ['QUALIFIED'],
  QUALIFIED: ['PROPOSAL'],
  PROPOSAL: ['NEGOTIATION'],
  NEGOTIATION: ['CLOSED_WON', 'CLOSED_LOST'],
  CLOSED_WON: [],
  CLOSED_LOST: [],
}
