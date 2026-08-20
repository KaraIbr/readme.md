import { z } from 'zod'

export const activityCreateSchema = z.object({
  activity_type: z.enum(['CALL', 'EMAIL', 'MEETING', 'NOTE']),
  title: z.string().min(1, 'Title is required').max(255),
  description: z.string().max(4000).optional().nullable(),
  contact_id: z.preprocess(
    value => value === '' || value === undefined ? undefined : Number(value),
    z.number().optional().nullable(),
  ),
  lead_id: z.preprocess(
    value => value === '' || value === undefined ? undefined : Number(value),
    z.number().optional().nullable(),
  ),
  assigned_to: z.preprocess(
    value => value === '' || value === undefined ? undefined : Number(value),
    z.number().optional().nullable(),
  ),
  scheduled_at: z.string().optional().nullable(),
})

export type ActivityCreateFormData = z.infer<typeof activityCreateSchema>
