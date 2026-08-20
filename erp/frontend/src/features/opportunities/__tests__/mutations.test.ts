import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import {
  useCreateOpportunity,
  useUpdateOpportunity,
  useDeleteOpportunity,
  useMoveOpportunityStage,
  useCloseOpportunity,
} from '../mutations/useOpportunityMutations'
import {
  createOpportunity,
  updateOpportunity,
  deleteOpportunity,
  moveOpportunityStage,
  closeOpportunity,
} from '../services/opportunity.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/opportunity.service', () => ({
  createOpportunity: vi.fn(),
  updateOpportunity: vi.fn(),
  deleteOpportunity: vi.fn(),
  moveOpportunityStage: vi.fn(),
  closeOpportunity: vi.fn(),
}))

const mockedCreateOpportunity = vi.mocked(createOpportunity)
const mockedUpdateOpportunity = vi.mocked(updateOpportunity)
const mockedDeleteOpportunity = vi.mocked(deleteOpportunity)
const mockedMoveOpportunityStage = vi.mocked(moveOpportunityStage)
const mockedCloseOpportunity = vi.mocked(closeOpportunity)

describe('opportunity mutation hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates an opportunity', async () => {
    mockedCreateOpportunity.mockResolvedValue({ id: 1 } as never)
    const body = { name: 'Deal', contact_id: 1 }
    const { result } = renderHook(() => useCreateOpportunity(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(body)

    expect(mockedCreateOpportunity).toHaveBeenCalledWith(body, expect.anything())
  })

  it('updates an opportunity', async () => {
    mockedUpdateOpportunity.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateOpportunity(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, data: { value: 5000 } })

    expect(mockedUpdateOpportunity).toHaveBeenCalledWith(1, { value: 5000 })
  })

  it('deletes an opportunity', async () => {
    mockedDeleteOpportunity.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteOpportunity(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(1)

    expect(mockedDeleteOpportunity).toHaveBeenCalledWith(1, expect.anything())
  })

  it('moves an opportunity stage', async () => {
    mockedMoveOpportunityStage.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useMoveOpportunityStage(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, stage: { stage: 'NEGOTIATION' } })

    expect(mockedMoveOpportunityStage).toHaveBeenCalledWith(1, { stage: 'NEGOTIATION' })
  })

  it('closes an opportunity', async () => {
    mockedCloseOpportunity.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useCloseOpportunity(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, data: { outcome: 'WON' } })

    expect(mockedCloseOpportunity).toHaveBeenCalledWith(1, { outcome: 'WON' })
  })
})
