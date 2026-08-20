import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import {
  useCreateActivity,
  useUpdateActivity,
  useDeleteActivity,
  useCompleteActivity,
} from '../mutations/useActivityMutations'
import {
  createActivity,
  updateActivity,
  deleteActivity,
  completeActivity,
} from '../services/activity.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/activity.service', () => ({
  createActivity: vi.fn(),
  updateActivity: vi.fn(),
  deleteActivity: vi.fn(),
  completeActivity: vi.fn(),
}))

const mockedCreateActivity = vi.mocked(createActivity)
const mockedUpdateActivity = vi.mocked(updateActivity)
const mockedDeleteActivity = vi.mocked(deleteActivity)
const mockedCompleteActivity = vi.mocked(completeActivity)

describe('activity mutation hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates an activity', async () => {
    mockedCreateActivity.mockResolvedValue({ id: 1 } as never)
    const body = { activity_type: 'CALL', title: 'Intro call' } as const
    const { result } = renderHook(() => useCreateActivity(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(body)

    expect(mockedCreateActivity).toHaveBeenCalledWith(body, expect.anything())
  })

  it('updates an activity', async () => {
    mockedUpdateActivity.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateActivity(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, data: { title: 'Rescheduled' } })

    expect(mockedUpdateActivity).toHaveBeenCalledWith(1, { title: 'Rescheduled' })
  })

  it('deletes an activity', async () => {
    mockedDeleteActivity.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteActivity(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(1)

    expect(mockedDeleteActivity).toHaveBeenCalledWith(1, expect.anything())
  })

  it('completes an activity', async () => {
    mockedCompleteActivity.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useCompleteActivity(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(1)

    expect(mockedCompleteActivity).toHaveBeenCalledWith(1, expect.anything())
  })
})
