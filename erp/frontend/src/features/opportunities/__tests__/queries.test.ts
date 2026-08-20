import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useOpportunities, useOpportunity } from '../queries/useOpportunities'
import { getOpportunities, getOpportunity } from '../services/opportunity.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/opportunity.service', () => ({
  getOpportunities: vi.fn(),
  getOpportunity: vi.fn(),
}))

const mockedGetOpportunities = vi.mocked(getOpportunities)
const mockedGetOpportunity = vi.mocked(getOpportunity)

describe('opportunity query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the opportunity list', async () => {
    const opportunities = [{ id: 1, name: 'Deal' }]
    mockedGetOpportunities.mockResolvedValue(opportunities as never)

    const { result } = renderHook(() => useOpportunities({ stage: 'PROPOSAL' }), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(opportunities))
    expect(mockedGetOpportunities).toHaveBeenCalledWith({ stage: 'PROPOSAL' })
  })

  it('loads a single opportunity', async () => {
    const opportunity = { id: 1, name: 'Deal' }
    mockedGetOpportunity.mockResolvedValue(opportunity as never)

    const { result } = renderHook(() => useOpportunity(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(opportunity))
  })
})
