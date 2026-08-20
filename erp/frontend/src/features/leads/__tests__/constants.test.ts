import { describe, it, expect } from 'vitest'
import {
  LEAD_STAGES,
  NON_TERMINAL_STAGES,
  LEAD_OUTCOMES,
  LEAD_INTEREST_TYPES,
  TECHNICAL_VISIT_REQUIREMENTS,
  LEAD_INTERACTION_TYPES,
  STAGE_LABELS,
  STAGE_VARIANTS,
  INTEREST_LABELS,
  INTERACTION_LABELS,
} from '../types'

describe('lead type constants', () => {
  it('defines the full stage list', () => {
    expect(LEAD_STAGES).toEqual(['NEW', 'QUALIFYING', 'PROPOSAL_PHASE', 'CLOSED_WON', 'CLOSED_LOST'])
    expect(NON_TERMINAL_STAGES).toEqual(['NEW', 'QUALIFYING', 'PROPOSAL_PHASE'])
  })

  it('defines outcomes, interest types and requirements', () => {
    expect(LEAD_OUTCOMES).toEqual(['WON', 'LOST'])
    expect(LEAD_INTEREST_TYPES).toEqual(['Photovoltaic', 'BESS', 'Hibrid'])
    expect(TECHNICAL_VISIT_REQUIREMENTS).toEqual(['UNDETERMINED', 'NOT_REQUIRED', 'REQUIRED'])
    expect(LEAD_INTERACTION_TYPES).toEqual(['CALL', 'EMAIL', 'MEETING', 'MESSAGE', 'NEGOTIATION', 'NOTE'])
  })

  it('maps stages to labels and variants', () => {
    expect(STAGE_LABELS.NEW).toBe('New')
    expect(STAGE_LABELS.CLOSED_WON).toBe('Closed Won')
    expect(STAGE_VARIANTS.NEW).toBe('default')
    expect(STAGE_VARIANTS.CLOSED_WON).toBe('success')
    expect(STAGE_VARIANTS.CLOSED_LOST).toBe('danger')
  })

  it('maps interest and interaction types to labels', () => {
    expect(INTEREST_LABELS.Hibrid).toBe('Hybrid')
    expect(INTERACTION_LABELS.CALL).toBe('Call')
    expect(INTERACTION_LABELS.NEGOTIATION).toBe('Negotiation')
  })
})
