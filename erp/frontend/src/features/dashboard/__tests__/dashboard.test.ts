import { describe, it, expect } from 'vitest'
import { api } from '../../../test/mocks/api-client'
import { getDashboardStats } from '../services/dashboard.service'

describe('dashboard api service', () => {
  it('fetches dashboard stats', async () => {
    const stats = {
      total_contacts: 10,
      total_leads: 5,
      active_leads: 3,
      won_leads: 1,
      pending_visits: 2,
      revenue_won: 5000,
      leads_by_stage: { NEW: 3 },
      proposals_by_stage: { DRAFT: 1 },
      recent_transitions: [],
    }
    api.get.mockResolvedValue({ data: stats })

    const result = await getDashboardStats()

    expect(api.get).toHaveBeenCalledWith('/dashboard/stats')
    expect(result).toEqual(stats)
  })
})
