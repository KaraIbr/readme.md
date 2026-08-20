export const PROPOSAL_STAGES = ['DRAFT', 'SENT', 'NEGOTIATION', 'WON', 'LOST', 'SUPERSEDED'] as const
export type ProposalStage = (typeof PROPOSAL_STAGES)[number]

export const NON_TERMINAL_PROPOSAL_STAGES = ['DRAFT', 'SENT', 'NEGOTIATION'] as const
export const TERMINAL_PROPOSAL_STAGES = ['WON', 'LOST', 'SUPERSEDED'] as const

export const PROPOSAL_SYSTEM_TYPES = ['PV', 'BESS', 'HIBRID'] as const
export type ProposalSystemType = (typeof PROPOSAL_SYSTEM_TYPES)[number]

export const PROPOSAL_DOCUMENT_CLASSIFICATIONS = ['Costs', 'Technical', 'Other'] as const
export type ProposalDocumentClassification = (typeof PROPOSAL_DOCUMENT_CLASSIFICATIONS)[number]

export interface ProposalInstallationAddress {
  address_line?: string | null
  city?: string | null
  state?: string | null
  postal_code?: string | null
}

export interface ProposalPVSystemPayload {
  panel_count?: number | null
  panel_model?: string | null
  panel_power?: number | null
  inverter_model?: string | null
  inverter_count?: number | null
  inverter_power?: number | null
  type_of_surface?: string | null
  total_power_ac?: number | null
  system_size_kw?: number | null
  oversizing_kw?: number | null
  estimated_annual_kwh?: number | null
  estimated_savings_kw?: number | null
  connection_mode?: string | null
  cost_watt?: number | null
  price_watt?: number | null
}

export interface ProposalPVSystemRead {
  id: number
  proposal_id: number
  panel_count: number | null
  panel_model: string | null
  panel_power: number | null
  inverter_model: string | null
  inverter_count: number | null
  inverter_power: number | null
  type_of_surface: string | null
  total_power_ac: number | null
  system_size_kw: number | null
  oversizing_kw: number | null
  estimated_annual_kwh: number | null
  estimated_savings_kw: number | null
  connection_mode: string | null
  cost_watt: number | null
  price_watt: number | null
}

export interface ProposalBESSSystemPayload {
  battery_model?: string | null
  battery_count?: number | null
  battery_power_kw?: number | null
  battery_storage_kwh?: number | null
  bess_primary_use?: string | null
  technical_notes?: string | null
  cost_kwh?: number | null
  price_kwh?: number | null
}

export interface ProposalBESSSystemRead {
  id: number
  proposal_id: number
  battery_model: string | null
  battery_count: number | null
  battery_power_kw: number | null
  battery_storage_kwh: number | null
  bess_primary_use: string | null
  technical_notes: string | null
  cost_kwh: number | null
  price_kwh: number | null
}

export interface ProposalCreate {
  lead_id: number
  name: string
  version?: string | null
  installation_address?: ProposalInstallationAddress | null
  tariff?: string | null
  contracted_demand?: number | null
  system_type?: ProposalSystemType | null
  total_price?: number | null
  annual_savings?: number | null
  currency?: string | null
  estimated_cost?: number | null
  expected_profit?: number | null
  submitted_at?: string | null
  valid_until?: string | null
  pv_system?: ProposalPVSystemPayload | null
  bess_system?: ProposalBESSSystemPayload | null
}

export interface ProposalUpdate {
  name?: string
  version?: string | null
  installation_address?: ProposalInstallationAddress | null
  tariff?: string | null
  contracted_demand?: number | null
  system_type?: ProposalSystemType | null
  total_price?: number | null
  annual_savings?: number | null
  currency?: string | null
  estimated_cost?: number | null
  expected_profit?: number | null
  submitted_at?: string | null
  valid_until?: string | null
  pv_system?: ProposalPVSystemPayload | null
  bess_system?: ProposalBESSSystemPayload | null
}

export interface ProposalRead {
  id: number
  lead_id: number
  lead_name?: string | null
  lead_stage?: string | null
  name: string
  version: string | null
  installation_address: ProposalInstallationAddress
  tariff: string | null
  contracted_demand: number | null
  system_type: ProposalSystemType | null
  total_price: number | null
  annual_savings: number | null
  currency: string | null
  estimated_cost: number | null
  expected_profit: number | null
  submitted_at: string | null
  valid_until: string | null
  pv_system: ProposalPVSystemRead | null
  bess_system: ProposalBESSSystemRead | null
  is_complete: boolean
  missing_required_fields: string[]
  current_stage: ProposalStage
  loss_reason: string | null
  proposed_at: string | null
  created_by: number
  created_at: string
}

export interface ProposalStageChange {
  stage: ProposalStage
}

export interface ProposalLost {
  loss_reason: string
}

export interface ProposalFilters {
  lead_id?: number
  stage?: ProposalStage
  limit?: number
  offset?: number
}

export interface ProposalCommercialDocumentRead {
  id: number
  proposal_id: number
  title: string
  original_filename: string
  content_type: string | null
  size_bytes: number
  uploaded_by: number
  uploaded_at: string
}

export interface ProposalDocumentRead {
  id: number
  proposal_id: number
  title: string
  classification: ProposalDocumentClassification
  original_filename: string
  content_type: string | null
  size_bytes: number
  uploaded_by: number
  uploaded_at: string
}

export const STAGE_LABELS: Record<ProposalStage, string> = {
  DRAFT: 'Draft',
  SENT: 'Sent',
  NEGOTIATION: 'Negotiation',
  WON: 'Won',
  LOST: 'Lost',
  SUPERSEDED: 'Superseded',
}

export const STAGE_VARIANTS: Record<ProposalStage, 'default' | 'warning' | 'info' | 'success' | 'danger'> = {
  DRAFT: 'default',
  SENT: 'info',
  NEGOTIATION: 'warning',
  WON: 'success',
  LOST: 'danger',
  SUPERSEDED: 'default',
}

export const SYSTEM_TYPE_LABELS: Record<ProposalSystemType, string> = {
  PV: 'Photovoltaic',
  BESS: 'BESS',
  HIBRID: 'Hybrid',
}

export const CLASSIFICATION_LABELS: Record<ProposalDocumentClassification, string> = {
  Costs: 'Costs',
  Technical: 'Technical',
  Other: 'Other',
}
