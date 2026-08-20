import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import {
  useProposalList,
  useProposal,
  useProposalCommercialPdfs,
  useProposalDocuments,
} from '../queries/useProposals'
import { getProposals, getProposal, getCommercialPdfs, getProposalDocuments } from '../services/proposal.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/proposal.service', () => ({
  getProposals: vi.fn(),
  getProposal: vi.fn(),
  getCommercialPdfs: vi.fn(),
  getProposalDocuments: vi.fn(),
}))

const mockedGetProposals = vi.mocked(getProposals)
const mockedGetProposal = vi.mocked(getProposal)
const mockedGetCommercialPdfs = vi.mocked(getCommercialPdfs)
const mockedGetProposalDocuments = vi.mocked(getProposalDocuments)

describe('proposal query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the proposal list', async () => {
    const page = { items: [{ id: 1, name: 'Solar' }], total: 1, limit: 1, offset: 0 }
    mockedGetProposals.mockResolvedValue(page as never)

    const { result } = renderHook(() => useProposalList({ stage: 'DRAFT' }), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(page))
    expect(mockedGetProposals).toHaveBeenCalledWith({ stage: 'DRAFT' })
  })

  it('loads a single proposal', async () => {
    const proposal = { id: 1, name: 'Solar' }
    mockedGetProposal.mockResolvedValue(proposal as never)

    const { result } = renderHook(() => useProposal(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(proposal))
  })

  it('loads commercial pdfs', async () => {
    const pdfs = [{ id: 1, title: 'pdf' }]
    mockedGetCommercialPdfs.mockResolvedValue(pdfs as never)

    const { result } = renderHook(() => useProposalCommercialPdfs(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(pdfs))
  })

  it('loads proposal documents', async () => {
    const docs = [{ id: 1, title: 'doc' }]
    mockedGetProposalDocuments.mockResolvedValue(docs as never)

    const { result } = renderHook(() => useProposalDocuments(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(docs))
  })
})
