import { describe, it, expect } from 'vitest'
import { ADMIN_ROLES } from '../types'

describe('admin type constants', () => {
  it('defines the allowed admin roles', () => {
    expect(ADMIN_ROLES).toEqual(['ADMIN', 'MANAGER', 'SALES', 'TECH'])
  })
})
