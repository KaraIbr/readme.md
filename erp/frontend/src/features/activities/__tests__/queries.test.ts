import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useActivities, useActivity } from '../queries/useActivities'
import { getActivities, getActivity } from '../services/activity.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/activity.service', () => ({
  getActivities: vi.fn(),
  getActivity: vi.fn(),
}))

const mockedGetActivities = vi.mocked(getActivities)
const mockedGetActivity = vi.mocked(getActivity)

describe('activity query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the activity list', async () => {
    const activities = [{ id: 1, title: 'Intro call' }]
    mockedGetActivities.mockResolvedValue(activities as never)

    const { result } = renderHook(() => useActivities({ activity_type: 'CALL' }), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(activities))
    expect(mockedGetActivities).toHaveBeenCalledWith({ activity_type: 'CALL' })
  })

  it('loads a single activity', async () => {
    const activity = { id: 1, title: 'Intro call' }
    mockedGetActivity.mockResolvedValue(activity as never)

    const { result } = renderHook(() => useActivity(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(activity))
  })
})
