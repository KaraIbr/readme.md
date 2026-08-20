import { describe, it, expect } from 'vitest'
import { ACTIVITY_TYPES, ACTIVITY_LABELS, ACTIVITY_VARIANTS } from '../types'

describe('activity type constants', () => {
  it('defines the activity types', () => {
    expect(ACTIVITY_TYPES).toEqual(['CALL', 'EMAIL', 'MEETING', 'NOTE'])
  })

  it('maps activity types to labels and variants', () => {
    expect(ACTIVITY_LABELS.CALL).toBe('Call')
    expect(ACTIVITY_LABELS.MEETING).toBe('Meeting')
    expect(ACTIVITY_VARIANTS.CALL).toBe('warning')
    expect(ACTIVITY_VARIANTS.EMAIL).toBe('info')
    expect(ACTIVITY_VARIANTS.NOTE).toBe('default')
  })
})
