import { z } from 'zod'

export const leadCreateSchema = z.object({
  contact_id: z.number({ message: 'Contact is required' }).positive('Contact is required'),
  title: z.string().min(1, 'Title is required').max(255),
  interest_type: z.enum(['Photovoltaic', 'BESS', 'Hibrid'] as const),
  qualification_score: z.number().min(0).max(100).optional().nullable(),
  notes: z.string().max(4000).optional().nullable(),
})

export const leadUpdateSchema = z.object({
  contact_id: z.number().positive().optional(),
  title: z.string().min(1).max(255).optional(),
  interest_type: z.enum(['Photovoltaic', 'BESS', 'Hibrid'] as const).optional(),
  qualification_score: z.number().min(0).max(100).optional().nullable(),
  notes: z.string().max(4000).optional().nullable(),
})

export const leadCloseSchema = z.object({
  outcome: z.enum(['WON', 'LOST'] as const),
  notes: z.string().max(4000).optional().nullable(),
})

export const leadStageChangeSchema = z.object({
  stage: z.enum(['NEW', 'QUALIFYING', 'PROPOSAL_PHASE'] as const),
})

export const leadInteractionCreateSchema = z.object({
  interaction_type: z.enum(['CALL', 'EMAIL', 'MEETING', 'MESSAGE', 'NEGOTIATION', 'NOTE'] as const),
  title: z.string().min(1).max(255),
  notes: z.string().min(1).max(4000),
  interaction_date: z.string().min(1, 'Date is required'),
})

export const leadInteractionUpdateSchema = z.object({
  interaction_type: z.enum(['CALL', 'EMAIL', 'MEETING', 'MESSAGE', 'NEGOTIATION', 'NOTE'] as const).optional(),
  title: z.string().min(1).max(255).optional(),
  notes: z.string().min(1).max(4000).optional(),
  interaction_date: z.string().optional(),
})

export type LeadCreateFormData = z.infer<typeof leadCreateSchema>
export type LeadUpdateFormData = z.infer<typeof leadUpdateSchema>
export type LeadCloseFormData = z.infer<typeof leadCloseSchema>
export type LeadStageChangeFormData = z.infer<typeof leadStageChangeSchema>
export type LeadInteractionCreateFormData = z.infer<typeof leadInteractionCreateSchema>
export type LeadInteractionUpdateFormData = z.infer<typeof leadInteractionUpdateSchema>
