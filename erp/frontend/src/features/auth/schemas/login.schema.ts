import { z } from 'zod'

export const loginSchema = z.object({
  username: z
    .string()
    .min(1, 'Email is required')
    .email('Invalid email format'),
  password: z
    .string()
    .min(1, 'Password is required')
    .min(3, 'Password must be at least 3 characters'),
})

export type LoginFormData = z.infer<typeof loginSchema>
