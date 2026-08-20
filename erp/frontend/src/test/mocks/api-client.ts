import { vi } from 'vitest'

export const api = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
}

vi.mock('@services/api-client', () => ({ api }))
