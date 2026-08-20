import { z } from 'zod'

const installationAddressSchema = z.object({
  address_line: z.string().min(1).max(500).optional().nullable(),
  city: z.string().min(1).max(120).optional().nullable(),
  state: z.string().min(1).max(120).optional().nullable(),
  postal_code: z.string().min(1).max(30).optional().nullable(),
})

const pvSystemSchema = z.object({
  panel_count: z.number().min(0).optional().nullable(),
  panel_model: z.string().min(1).max(255).optional().nullable(),
  panel_power: z.number().positive().optional().nullable(),
  inverter_model: z.string().min(1).max(255).optional().nullable(),
  inverter_count: z.number().min(0).optional().nullable(),
  inverter_power: z.number().positive().optional().nullable(),
  type_of_surface: z.string().min(1).max(120).optional().nullable(),
  total_power_ac: z.number().positive().optional().nullable(),
  system_size_kw: z.number().positive().optional().nullable(),
  oversizing_kw: z.number().min(0).optional().nullable(),
  estimated_annual_kwh: z.number().positive().optional().nullable(),
  estimated_savings_kw: z.number().min(0).optional().nullable(),
  connection_mode: z.string().min(1).max(120).optional().nullable(),
  cost_watt: z.number().min(0).optional().nullable(),
  price_watt: z.number().positive().optional().nullable(),
})

const bessSystemSchema = z.object({
  battery_model: z.string().min(1).max(255).optional().nullable(),
  battery_count: z.number().min(0).optional().nullable(),
  battery_power_kw: z.number().positive().optional().nullable(),
  battery_storage_kwh: z.number().positive().optional().nullable(),
  bess_primary_use: z.string().min(1).max(120).optional().nullable(),
  technical_notes: z.string().min(1).max(4000).optional().nullable(),
  cost_kwh: z.number().min(0).optional().nullable(),
  price_kwh: z.number().positive().optional().nullable(),
})

export const proposalCreateSchema = z.object({
  lead_id: z.number({ message: 'Lead is required' }).positive('Lead is required'),
  name: z.string().min(1, 'Name is required').max(255),
  version: z.string().min(1).max(50).optional().nullable(),
  installation_address: installationAddressSchema.optional().nullable(),
  tariff: z.string().min(1).max(120).optional().nullable(),
  contracted_demand: z.number().positive().optional().nullable(),
  system_type: z.enum(['PV', 'BESS', 'HIBRID'] as const).optional().nullable(),
  total_price: z.number().min(0).optional().nullable(),
  annual_savings: z.number().min(0).optional().nullable(),
  currency: z.enum(['MXN', 'USD']).optional().nullable(),
  estimated_cost: z.number().min(0).optional().nullable(),
  expected_profit: z.number().min(0).optional().nullable(),
  submitted_at: z.string().optional().nullable(),
  valid_until: z.string().optional().nullable(),
  pv_system: pvSystemSchema.optional().nullable(),
  bess_system: bessSystemSchema.optional().nullable(),
})

export const proposalUpdateSchema = z.object({
  name: z.string().min(1).max(255).optional(),
  version: z.string().min(1).max(50).optional().nullable(),
  installation_address: installationAddressSchema.optional().nullable(),
  tariff: z.string().min(1).max(120).optional().nullable(),
  contracted_demand: z.number().positive().optional().nullable(),
  system_type: z.enum(['PV', 'BESS', 'HIBRID'] as const).optional().nullable(),
  total_price: z.number().min(0).optional().nullable(),
  annual_savings: z.number().min(0).optional().nullable(),
  currency: z.enum(['MXN', 'USD']).optional().nullable(),
  estimated_cost: z.number().min(0).optional().nullable(),
  expected_profit: z.number().min(0).optional().nullable(),
  submitted_at: z.string().optional().nullable(),
  valid_until: z.string().optional().nullable(),
  pv_system: pvSystemSchema.optional().nullable(),
  bess_system: bessSystemSchema.optional().nullable(),
})

export const proposalStageChangeSchema = z.object({
  stage: z.enum(['DRAFT', 'SENT', 'NEGOTIATION'] as const),
})

export const proposalLostSchema = z.object({
  loss_reason: z.string().min(1, 'Loss reason is required').max(500),
})

export type ProposalCreateFormData = z.infer<typeof proposalCreateSchema>
export type ProposalUpdateFormData = z.infer<typeof proposalUpdateSchema>
export type ProposalStageChangeFormData = z.infer<typeof proposalStageChangeSchema>
export type ProposalLostFormData = z.infer<typeof proposalLostSchema>
