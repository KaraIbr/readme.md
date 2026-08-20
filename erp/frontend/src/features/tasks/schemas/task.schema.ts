import { z } from 'zod'

export const taskCreateSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  description: z.string().max(4000).optional().nullable(),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'URGENT'] as const).optional(),
  due_date: z.string().optional().nullable(),
  contact_id: z.number().positive().optional().nullable(),
  lead_id: z.number().positive().optional().nullable(),
  assigned_to: z.number().positive().optional().nullable(),
})

export const taskUpdateSchema = z.object({
  title: z.string().min(1).max(255).optional(),
  description: z.string().max(4000).optional().nullable(),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'URGENT'] as const).optional(),
  due_date: z.string().optional().nullable(),
  assigned_to: z.number().positive().optional().nullable(),
})

export const taskStatusChangeSchema = z.object({
  status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'CANCELLED'] as const),
})

export type TaskCreateFormData = z.infer<typeof taskCreateSchema>
export type TaskUpdateFormData = z.infer<typeof taskUpdateSchema>
export type TaskStatusChangeFormData = z.infer<typeof taskStatusChangeSchema>
