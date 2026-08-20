import { describe, it, expect } from 'vitest'
import { profileUpdateSchema } from '../schemas/settings.schema'
import { api } from '../../../test/mocks/api-client'
import { updateProfile } from '../services/settings.service'

describe('settings', () => {
  describe('schema validation', () => {
    it('accepts a valid profile', () => {
      const result = profileUpdateSchema.safeParse({ full_name: 'New Name', email: 'new@example.com' })
      expect(result.success).toBe(true)
    })

    it('rejects invalid email', () => {
      const result = profileUpdateSchema.safeParse({ email: 'not-an-email' })
      expect(result.success).toBe(false)
    })

    it('accepts an empty object', () => {
      const result = profileUpdateSchema.safeParse({})
      expect(result.success).toBe(true)
    })
  })

  describe('api service', () => {
    it('sends only provided fields', async () => {
      api.patch.mockResolvedValue({ data: null })

      await updateProfile(7, { full_name: 'New Name', email: 'new@example.com' })

      expect(api.patch).toHaveBeenCalledWith('/identity/users/7', {
        full_name: 'New Name',
        email: 'new@example.com',
      })
    })

    it('omits undefined full_name', async () => {
      api.patch.mockResolvedValue({ data: null })

      await updateProfile(7, { email: 'new@example.com' })

      expect(api.patch).toHaveBeenCalledWith('/identity/users/7', { email: 'new@example.com' })
    })
  })
})
