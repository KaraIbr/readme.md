import { z } from 'zod/v4'

export const profileUpdateSchema = z.object({
  full_name: z.string().optional(),
  email: z.string().email('Invalid email').optional(),
})

export type ProfileUpdateFormData = z.infer<typeof profileUpdateSchema>
