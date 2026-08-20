import { describe, it, expect } from 'vitest'
import {
  OPPORTUNITY_STAGES,
  STAGE_LABELS,
  STAGE_VARIANTS,
  FORWARD_STAGES,
} from '../types'

describe('opportunity type constants', () => {
  it('defines the full stage list', () => {
    expect(OPPORTUNITY_STAGES).toEqual([
      'PROSPECTING', 'QUALIFIED', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST',
    ])
  })

  it('maps stages to labels and variants', () => {
    expect(STAGE_LABELS.PROSPECTING).toBe('Prospecting')
    expect(STAGE_LABELS.CLOSED_WON).toBe('Won')
    expect(STAGE_VARIANTS.NEGOTIATION).toBe('warning')
    expect(STAGE_VARIANTS.CLOSED_WON).toBe('success')
    expect(STAGE_VARIANTS.CLOSED_LOST).toBe('danger')
  })

  it('defines forward stages for each stage', () => {
    expect(FORWARD_STAGES.PROSPECTING).toEqual(['QUALIFIED'])
    expect(FORWARD_STAGES.NEGOTIATION).toEqual(['CLOSED_WON', 'CLOSED_LOST'])
    expect(FORWARD_STAGES.CLOSED_WON).toEqual([])
  })
})
