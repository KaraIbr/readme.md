import { z } from 'zod'

export const visitAssigneeSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  user_id: z.number().positive().optional().nullable(),
})

export const visitCreateSchema = z.object({
  lead_id: z.number({ message: 'Lead is required' }).positive('Lead is required'),
  scheduled_at: z.string().optional().nullable(),
  receiver_name: z.string().max(255).optional().nullable(),
  receiver_phone: z.string().max(30).optional().nullable(),
  notes: z.string().max(4000).optional().nullable(),
  assignees: z.array(visitAssigneeSchema).optional().default([]),
})

export const visitUpdateSchema = z.object({
  scheduled_at: z.string().optional().nullable(),
  receiver_name: z.string().max(255).optional().nullable(),
  receiver_phone: z.string().max(30).optional().nullable(),
  notes: z.string().max(4000).optional().nullable(),
  assignees: z.array(visitAssigneeSchema).optional().nullable(),
})

export type VisitCreateFormData = z.infer<typeof visitCreateSchema>
export type VisitUpdateFormData = z.infer<typeof visitUpdateSchema>
