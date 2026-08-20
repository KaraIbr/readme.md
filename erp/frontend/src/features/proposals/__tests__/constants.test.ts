import { describe, it, expect } from 'vitest'
import {
  PROPOSAL_STAGES,
  NON_TERMINAL_PROPOSAL_STAGES,
  TERMINAL_PROPOSAL_STAGES,
  PROPOSAL_SYSTEM_TYPES,
  PROPOSAL_DOCUMENT_CLASSIFICATIONS,
  STAGE_LABELS,
  STAGE_VARIANTS,
  SYSTEM_TYPE_LABELS,
  CLASSIFICATION_LABELS,
} from '../types'

describe('proposal type constants', () => {
  it('defines the full stage list', () => {
    expect(PROPOSAL_STAGES).toEqual(['DRAFT', 'SENT', 'NEGOTIATION', 'WON', 'LOST', 'SUPERSEDED'])
    expect(NON_TERMINAL_PROPOSAL_STAGES).toEqual(['DRAFT', 'SENT', 'NEGOTIATION'])
    expect(TERMINAL_PROPOSAL_STAGES).toEqual(['WON', 'LOST', 'SUPERSEDED'])
  })

  it('defines system types and document classifications', () => {
    expect(PROPOSAL_SYSTEM_TYPES).toEqual(['PV', 'BESS', 'HIBRID'])
    expect(PROPOSAL_DOCUMENT_CLASSIFICATIONS).toEqual(['Costs', 'Technical', 'Other'])
  })

  it('maps stages to labels and variants', () => {
    expect(STAGE_LABELS.DRAFT).toBe('Draft')
    expect(STAGE_LABELS.SUPERSEDED).toBe('Superseded')
    expect(STAGE_VARIANTS.WON).toBe('success')
    expect(STAGE_VARIANTS.LOST).toBe('danger')
    expect(STAGE_VARIANTS.SUPERSEDED).toBe('default')
  })

  it('maps system types and classifications to labels', () => {
    expect(SYSTEM_TYPE_LABELS.PV).toBe('Photovoltaic')
    expect(SYSTEM_TYPE_LABELS.HIBRID).toBe('Hybrid')
    expect(CLASSIFICATION_LABELS.Technical).toBe('Technical')
  })
})
