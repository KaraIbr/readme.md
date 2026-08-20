export const LEAD_STAGES = ['NEW', 'QUALIFYING', 'PROPOSAL_PHASE', 'CLOSED_WON', 'CLOSED_LOST'] as const
export type LeadStage = (typeof LEAD_STAGES)[number]

export const NON_TERMINAL_STAGES = ['NEW', 'QUALIFYING', 'PROPOSAL_PHASE'] as const

export const LEAD_OUTCOMES = ['WON', 'LOST'] as const
export type LeadOutcome = (typeof LEAD_OUTCOMES)[number]

export const LEAD_INTEREST_TYPES = ['Photovoltaic', 'BESS', 'Hibrid'] as const
export type LeadInterestType = (typeof LEAD_INTEREST_TYPES)[number]

export const TECHNICAL_VISIT_REQUIREMENTS = ['UNDETERMINED', 'NOT_REQUIRED', 'REQUIRED'] as const
export type TechnicalVisitRequirement = (typeof TECHNICAL_VISIT_REQUIREMENTS)[number]

export const LEAD_INTERACTION_TYPES = ['CALL', 'EMAIL', 'MEETING', 'MESSAGE', 'NEGOTIATION', 'NOTE'] as const
export type LeadInteractionType = (typeof LEAD_INTERACTION_TYPES)[number]

export interface LeadRead {
  id: number
  contact_id: number
  title: string
  interest_type: LeadInterestType
  qualification_score: number | null
  current_stage: LeadStage
  outcome: LeadOutcome | null
  owner_id: number
  notes: string | null
  technical_visit_requirement: TechnicalVisitRequirement
  created_at: string
  closed_at: string | null
}

export interface LeadCreate {
  contact_id: number
  title: string
  interest_type: LeadInterestType
  qualification_score?: number | null
  notes?: string | null
}

export interface LeadUpdate {
  contact_id?: number
  title?: string
  interest_type?: LeadInterestType
  qualification_score?: number | null
  notes?: string | null
}

export interface LeadClose {
  outcome: LeadOutcome
  notes?: string | null
}

export interface LeadStageChange {
  stage: LeadStage
}

export interface LeadFilters {
  contact_id?: number
  stage?: LeadStage
  limit?: number
  offset?: number
}

export interface LeadDocumentRead {
  id: number
  lead_id: number
  title: string
  original_filename: string
  content_type: string | null
  size_bytes: number
  uploaded_by: number
  uploaded_at: string
}

export interface LeadElectricityBillRead {
  id: number
  lead_id: number
  title: string
  original_filename: string
  content_type: string | null
  size_bytes: number
  uploaded_by: number
  uploaded_at: string
}

export interface LeadInteractionCreate {
  interaction_type: LeadInteractionType
  title: string
  notes: string
  interaction_date: string
}

export interface LeadInteractionUpdate {
  interaction_type?: LeadInteractionType
  title?: string
  notes?: string
  interaction_date?: string
}

export interface LeadInteractionRead {
  id: number
  lead_id: number
  interaction_type: LeadInteractionType
  title: string
  notes: string
  interaction_date: string
  created_by: number
  created_at: string
  updated_at: string
}

export const STAGE_LABELS: Record<LeadStage, string> = {
  NEW: 'New',
  QUALIFYING: 'Qualifying',
  PROPOSAL_PHASE: 'Proposal Phase',
  CLOSED_WON: 'Closed Won',
  CLOSED_LOST: 'Closed Lost',
}

export const STAGE_VARIANTS: Record<LeadStage, 'default' | 'warning' | 'info' | 'success' | 'danger'> = {
  NEW: 'default',
  QUALIFYING: 'warning',
  PROPOSAL_PHASE: 'info',
  CLOSED_WON: 'success',
  CLOSED_LOST: 'danger',
}

export const INTEREST_LABELS: Record<LeadInterestType, string> = {
  Photovoltaic: 'Photovoltaic',
  BESS: 'BESS',
  Hibrid: 'Hybrid',
}

export const INTERACTION_LABELS: Record<LeadInteractionType, string> = {
  CALL: 'Call',
  EMAIL: 'Email',
  MEETING: 'Meeting',
  MESSAGE: 'Message',
  NEGOTIATION: 'Negotiation',
  NOTE: 'Note',
}
