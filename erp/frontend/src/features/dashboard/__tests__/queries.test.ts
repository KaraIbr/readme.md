import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useDashboardStats } from '../queries/useDashboardStats'
import { getDashboardStats } from '../services/dashboard.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/dashboard.service', () => ({
  getDashboardStats: vi.fn(),
}))

const mockedGetDashboardStats = vi.mocked(getDashboardStats)

describe('dashboard query hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads dashboard stats', async () => {
    const stats = { total_contacts: 1, total_leads: 0 }
    mockedGetDashboardStats.mockResolvedValue(stats as never)

    const { result } = renderHook(() => useDashboardStats(), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(stats))
    expect(mockedGetDashboardStats).toHaveBeenCalled()
  })
})
