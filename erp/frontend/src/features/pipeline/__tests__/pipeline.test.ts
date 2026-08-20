import { describe, it, expect } from 'vitest'
import { api } from '../../../test/mocks/api-client'
import { getTransitions, getPipelineSummary } from '../services/pipeline.service'

describe('pipeline api service', () => {
  it('lists transitions with optional filters', async () => {
    const transitions = [{ id: 1, to_stage: 'NEW' }]
    api.get.mockResolvedValue({ data: transitions })

    const result = await getTransitions({ entity_type: 'lead', entity_id: 1 })

    expect(api.get).toHaveBeenCalledWith('/pipeline/transitions', {
      params: { entity_type: 'lead', entity_id: 1 },
    })
    expect(result).toEqual(transitions)
  })

  it('fetches a pipeline summary for a lead', async () => {
    const summary = { current_stage: 'NEW', transitions: [] }
    api.get.mockResolvedValue({ data: summary })

    const result = await getPipelineSummary('lead', 1)

    expect(api.get).toHaveBeenCalledWith('/pipeline/summary/lead/1')
    expect(result).toEqual(summary)
  })

  it('fetches a pipeline summary for a proposal', async () => {
    const summary = { current_stage: 'DRAFT', transitions: [] }
    api.get.mockResolvedValue({ data: summary })

    const result = await getPipelineSummary('proposal', 2)

    expect(api.get).toHaveBeenCalledWith('/pipeline/summary/proposal/2')
    expect(result).toEqual(summary)
  })
})
