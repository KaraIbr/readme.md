import { describe, it, expect } from 'vitest'
import {
  VISIT_STATUSES,
  ACTIVE_VISIT_STATUSES,
  ATTACHMENT_KINDS,
  STATUS_LABELS,
  STATUS_VARIANTS,
  ATTACHMENT_KIND_LABELS,
} from '../types'

describe('technical visit type constants', () => {
  it('defines statuses, active statuses and attachment kinds', () => {
    expect(VISIT_STATUSES).toEqual(['REQUESTED', 'SCHEDULED', 'COMPLETED', 'CANCELLED'])
    expect(ACTIVE_VISIT_STATUSES).toEqual(['REQUESTED', 'SCHEDULED'])
    expect(ATTACHMENT_KINDS).toEqual(['DOCUMENT', 'PHOTO', 'OTHER'])
  })

  it('maps statuses to labels and variants', () => {
    expect(STATUS_LABELS.REQUESTED).toBe('Requested')
    expect(STATUS_LABELS.COMPLETED).toBe('Completed')
    expect(STATUS_VARIANTS.SCHEDULED).toBe('info')
    expect(STATUS_VARIANTS.COMPLETED).toBe('success')
    expect(STATUS_VARIANTS.CANCELLED).toBe('danger')
  })

  it('maps attachment kinds to labels', () => {
    expect(ATTACHMENT_KIND_LABELS.DOCUMENT).toBe('Document')
    expect(ATTACHMENT_KIND_LABELS.PHOTO).toBe('Photo')
    expect(ATTACHMENT_KIND_LABELS.OTHER).toBe('Other')
  })
})
