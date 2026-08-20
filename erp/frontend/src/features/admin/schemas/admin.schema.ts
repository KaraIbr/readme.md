import { z } from 'zod/v4'
import { ADMIN_ROLES } from '../types'

export const adminUserCreateSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  full_name: z.string().optional(),
  role: z.enum(ADMIN_ROLES),
})

export type AdminUserCreateFormData = z.infer<typeof adminUserCreateSchema>
