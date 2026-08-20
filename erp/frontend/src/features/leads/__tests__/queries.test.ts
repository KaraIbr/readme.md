import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import {
  useLeadList,
  useLead,
  useLeadDocuments,
  useLeadElectricityBills,
  useLeadInteractions,
} from '../queries/useLeads'
import { getLeads, getLead, getLeadDocuments, getLeadElectricityBills, getLeadInteractions } from '../services/lead.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/lead.service', () => ({
  getLeads: vi.fn(),
  getLead: vi.fn(),
  getLeadDocuments: vi.fn(),
  getLeadElectricityBills: vi.fn(),
  getLeadInteractions: vi.fn(),
}))

const mockedGetLeads = vi.mocked(getLeads)
const mockedGetLead = vi.mocked(getLead)
const mockedGetLeadDocuments = vi.mocked(getLeadDocuments)
const mockedGetLeadElectricityBills = vi.mocked(getLeadElectricityBills)
const mockedGetLeadInteractions = vi.mocked(getLeadInteractions)

describe('lead query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the lead list', async () => {
    const page = { items: [{ id: 1, title: 'Solar' }], total: 1, limit: 1, offset: 0 }
    mockedGetLeads.mockResolvedValue(page as never)

    const { result } = renderHook(() => useLeadList({ stage: 'NEW' }), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(page))
    expect(mockedGetLeads).toHaveBeenCalledWith({ stage: 'NEW' })
  })

  it('loads a single lead', async () => {
    const lead = { id: 1, title: 'Solar' }
    mockedGetLead.mockResolvedValue(lead as never)

    const { result } = renderHook(() => useLead(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(lead))
    expect(mockedGetLead).toHaveBeenCalledWith(1)
  })

  it('does not fetch a lead when id is falsy', async () => {
    const { result } = renderHook(() => useLead(0), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.isPending).toBe(true))
    expect(mockedGetLead).not.toHaveBeenCalled()
  })

  it('loads lead documents', async () => {
    const docs = [{ id: 1, title: 'contract.pdf' }]
    mockedGetLeadDocuments.mockResolvedValue(docs as never)

    const { result } = renderHook(() => useLeadDocuments(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(docs))
  })

  it('loads lead electricity bills', async () => {
    const bills = [{ id: 1, title: 'bill.pdf' }]
    mockedGetLeadElectricityBills.mockResolvedValue(bills as never)

    const { result } = renderHook(() => useLeadElectricityBills(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(bills))
  })

  it('loads lead interactions', async () => {
    const interactions = [{ id: 1, title: 'Call' }]
    mockedGetLeadInteractions.mockResolvedValue(interactions as never)

    const { result } = renderHook(() => useLeadInteractions(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(interactions))
  })
})
