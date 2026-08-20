import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useTransitions, usePipelineSummary } from '../queries/usePipeline'
import { getTransitions, getPipelineSummary } from '../services/pipeline.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/pipeline.service', () => ({
  getTransitions: vi.fn(),
  getPipelineSummary: vi.fn(),
}))

const mockedGetTransitions = vi.mocked(getTransitions)
const mockedGetPipelineSummary = vi.mocked(getPipelineSummary)

describe('pipeline query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads transitions', async () => {
    const transitions = [{ id: 1, to_stage: 'NEW' }]
    mockedGetTransitions.mockResolvedValue(transitions as never)

    const { result } = renderHook(() => useTransitions({ entity_type: 'lead', entity_id: 1 }), {
      wrapper: createQueryWrapper(),
    })

    await waitFor(() => expect(result.current.data).toEqual(transitions))
    expect(mockedGetTransitions).toHaveBeenCalledWith({ entity_type: 'lead', entity_id: 1 })
  })

  it('loads a pipeline summary', async () => {
    const summary = { current_stage: 'NEW', transitions: [] }
    mockedGetPipelineSummary.mockResolvedValue(summary as never)

    const { result } = renderHook(() => usePipelineSummary('lead', 1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(summary))
    expect(mockedGetPipelineSummary).toHaveBeenCalledWith('lead', 1)
  })
})
