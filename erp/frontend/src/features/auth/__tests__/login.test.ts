import { describe, it, expect } from 'vitest'
import { loginSchema } from '../schemas/login.schema'
import { api } from '../../../test/mocks/api-client'
import { login, getCurrentUser, logout } from '../services/auth.service'

describe('auth login', () => {
  describe('schema validation', () => {
    it('accepts valid credentials', () => {
      const result = loginSchema.safeParse({
        username: 'user@example.com',
        password: 'secret',
      })
      expect(result.success).toBe(true)
    })

    it('rejects empty username', () => {
      const result = loginSchema.safeParse({ username: '', password: 'secret' })
      expect(result.success).toBe(false)
    })

    it('rejects non-email username', () => {
      const result = loginSchema.safeParse({ username: 'not-an-email', password: 'secret' })
      expect(result.success).toBe(false)
    })

    it('rejects empty password', () => {
      const result = loginSchema.safeParse({ username: 'user@example.com', password: '' })
      expect(result.success).toBe(false)
    })

    it('rejects password shorter than 3 characters', () => {
      const result = loginSchema.safeParse({ username: 'user@example.com', password: 'ab' })
      expect(result.success).toBe(false)
    })
  })

  describe('api service', () => {
    it('posts credentials as urlencoded form data', async () => {
      api.post.mockResolvedValue({ data: null })

      await login({ username: 'user@example.com', password: 'secret' })

      expect(api.post).toHaveBeenCalledWith(
        '/identity/auth/login',
        'username=user%40example.com&password=secret',
        { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } },
      )
    })

    it('fetches the current user', async () => {
      const user = { id: 1, email: 'user@example.com', full_name: null, is_active: true }
      api.get.mockResolvedValue({ data: user })

      const result = await getCurrentUser()

      expect(api.get).toHaveBeenCalledWith('/identity/users/me')
      expect(result).toEqual(user)
    })

    it('posts to the logout endpoint', async () => {
      api.post.mockResolvedValue({ data: null })

      await logout()

      expect(api.post).toHaveBeenCalledWith('/identity/auth/logout')
    })
  })
})
