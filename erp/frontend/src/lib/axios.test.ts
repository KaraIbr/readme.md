import { describe, it, expect } from 'vitest'
import { createAxiosInstance } from './axios'

describe('createAxiosInstance', () => {
  it('creates an axios instance with the given base url', () => {
    const instance = createAxiosInstance('/api/v1')

    expect(instance.defaults.baseURL).toBe('/api/v1')
    expect(instance.defaults.timeout).toBe(30_000)
    expect(instance.defaults.headers['Content-Type']).toBe('application/json')
  })
})
