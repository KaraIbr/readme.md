import { describe, it, expect } from 'vitest'
import { adminUserCreateSchema } from '../schemas/admin.schema'
import { api } from '../../../test/mocks/api-client'
import { getUsers, getUser, createUser, updateUser, deleteUser } from '../services/admin.service'

describe('admin users', () => {
  describe('schema validation', () => {
    it('accepts a valid user', () => {
      const result = adminUserCreateSchema.safeParse({
        email: 'admin@example.com',
        password: 'strong-password',
        full_name: 'Admin',
        role: 'MANAGER',
      })
      expect(result.success).toBe(true)
    })

    it('rejects invalid email', () => {
      const result = adminUserCreateSchema.safeParse({
        email: 'not-an-email',
        password: 'strong-password',
        role: 'SALES',
      })
      expect(result.success).toBe(false)
    })

    it('rejects password shorter than 8 characters', () => {
      const result = adminUserCreateSchema.safeParse({
        email: 'admin@example.com',
        password: 'short',
        role: 'SALES',
      })
      expect(result.success).toBe(false)
    })

    it('rejects an unknown role', () => {
      const result = adminUserCreateSchema.safeParse({
        email: 'admin@example.com',
        password: 'strong-password',
        role: 'CUSTOM',
      })
      expect(result.success).toBe(false)
    })
  })

  describe('api service', () => {
    it('lists users', async () => {
      const users = [{ id: 1, email: 'a@example.com' }]
      api.get.mockResolvedValue({ data: users })

      const result = await getUsers()

      expect(api.get).toHaveBeenCalledWith('/identity/users/')
      expect(result).toEqual(users)
    })

    it('fetches a single user', async () => {
      const user = { id: 1, email: 'a@example.com' }
      api.get.mockResolvedValue({ data: user })

      const result = await getUser(1)

      expect(api.get).toHaveBeenCalledWith('/identity/users/1')
      expect(result).toEqual(user)
    })

    it('creates a user', async () => {
      const body = { email: 'a@example.com', password: 'strong-password', role: 'SALES' }
      const created = { id: 2, ...body }
      api.post.mockResolvedValue({ data: created })

      const result = await createUser(body)

      expect(api.post).toHaveBeenCalledWith('/identity/users/', body)
      expect(result).toEqual(created)
    })

    it('updates a user', async () => {
      const body = { full_name: 'Updated' }
      const updated = { id: 1, ...body }
      api.patch.mockResolvedValue({ data: updated })

      const result = await updateUser(1, body)

      expect(api.patch).toHaveBeenCalledWith('/identity/users/1', body)
      expect(result).toEqual(updated)
    })

    it('deletes a user', async () => {
      api.delete.mockResolvedValue({ data: null })

      await deleteUser(3)

      expect(api.delete).toHaveBeenCalledWith('/identity/users/3')
    })
  })
})
