import { z } from 'zod'

const companyFields = {
  name: z.string().min(1, 'Name is required').max(255),
  promoter_id: z.preprocess(
    value => value === '' || value === undefined ? undefined : Number(value),
    z.number().optional(),
  ),
  address_line: z.string().max(255).optional().nullable(),
  city: z.string().max(120).optional().nullable(),
  state: z.string().max(120).optional().nullable(),
  postal_code: z.string().max(30).optional().nullable(),
  industry: z.string().max(120).optional().nullable(),
}

const peopleSchema = z
  .array(
    z.object({
      name: z.string().min(1, 'Person name is required').max(255),
      phone: z.string().min(1, 'Phone is required').max(50),
      email: z.string().email().max(255).optional().nullable().or(z.literal('')),
      position: z.string().min(1, 'Position is required').max(120),
    }),
  )
  .min(1, 'At least one contact person is required')

export const companyCreateSchema = z.object({
  ...companyFields,
  people: peopleSchema,
})

export const companyDetailSchema = z.object(companyFields)

export type CompanyCreateFormData = z.infer<typeof companyCreateSchema>
export type CompanyDetailFormData = z.infer<typeof companyDetailSchema>
