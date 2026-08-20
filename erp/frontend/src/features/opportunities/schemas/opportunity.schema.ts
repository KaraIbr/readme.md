import { z } from 'zod'

export const opportunityCreateSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  contact_id: z.preprocess(
    value => value === '' || value === undefined ? undefined : Number(value),
    z.number({ message: 'Contact is required' }).gt(0),
  ),
  lead_id: z.preprocess(
    value => value === '' || value === undefined ? undefined : Number(value),
    z.number().optional().nullable(),
  ),
  value: z.preprocess(
    value => value === '' || value === undefined ? undefined : Number(value),
    z.number().optional().nullable(),
  ),
  currency: z.string().max(3).optional().nullable(),
  expected_close_date: z.string().optional().nullable(),
  notes: z.string().max(4000).optional().nullable(),
})

export type OpportunityCreateFormData = z.infer<typeof opportunityCreateSchema>
