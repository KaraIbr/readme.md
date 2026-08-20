import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import {
  useCreateProposal,
  useUpdateProposal,
  useDeleteProposal,
  useMoveProposalStage,
  useMarkProposalWon,
  useMarkProposalLost,
  useUploadCommercialPdf,
  useDeleteCommercialPdf,
  useUploadProposalDocument,
  useDeleteProposalDocument,
} from '../mutations/useProposalMutations'
import {
  createProposal,
  updateProposal,
  deleteProposal,
  moveProposalStage,
  markProposalWon,
  markProposalLost,
  uploadCommercialPdf,
  deleteCommercialPdf,
  uploadProposalDocument,
  deleteProposalDocument,
} from '../services/proposal.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/proposal.service', () => ({
  createProposal: vi.fn(),
  updateProposal: vi.fn(),
  deleteProposal: vi.fn(),
  moveProposalStage: vi.fn(),
  markProposalWon: vi.fn(),
  markProposalLost: vi.fn(),
  uploadCommercialPdf: vi.fn(),
  deleteCommercialPdf: vi.fn(),
  uploadProposalDocument: vi.fn(),
  deleteProposalDocument: vi.fn(),
}))

const mockedCreateProposal = vi.mocked(createProposal)
const mockedUpdateProposal = vi.mocked(updateProposal)
const mockedDeleteProposal = vi.mocked(deleteProposal)
const mockedMoveProposalStage = vi.mocked(moveProposalStage)
const mockedMarkProposalWon = vi.mocked(markProposalWon)
const mockedMarkProposalLost = vi.mocked(markProposalLost)
const mockedUploadCommercialPdf = vi.mocked(uploadCommercialPdf)
const mockedDeleteCommercialPdf = vi.mocked(deleteCommercialPdf)
const mockedUploadProposalDocument = vi.mocked(uploadProposalDocument)
const mockedDeleteProposalDocument = vi.mocked(deleteProposalDocument)

describe('proposal mutation hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates a proposal', async () => {
    mockedCreateProposal.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useCreateProposal(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ lead_id: 1, name: 'Solar' })

    expect(mockedCreateProposal).toHaveBeenCalledWith({ lead_id: 1, name: 'Solar' }, expect.anything())
  })

  it('updates a proposal', async () => {
    mockedUpdateProposal.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateProposal(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, body: { name: 'Renamed' } })

    expect(mockedUpdateProposal).toHaveBeenCalledWith(1, { name: 'Renamed' })
  })

  it('deletes a proposal', async () => {
    mockedDeleteProposal.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteProposal(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(1)

    expect(mockedDeleteProposal).toHaveBeenCalledWith(1, expect.anything())
  })

  it('moves a proposal stage', async () => {
    mockedMoveProposalStage.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useMoveProposalStage(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, body: { stage: 'SENT' } })

    expect(mockedMoveProposalStage).toHaveBeenCalledWith(1, { stage: 'SENT' })
  })

  it('marks a proposal won', async () => {
    mockedMarkProposalWon.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useMarkProposalWon(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(1)

    expect(mockedMarkProposalWon).toHaveBeenCalledWith(1, expect.anything())
  })

  it('marks a proposal lost', async () => {
    mockedMarkProposalLost.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useMarkProposalLost(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, body: { loss_reason: 'Budget' } })

    expect(mockedMarkProposalLost).toHaveBeenCalledWith(1, { loss_reason: 'Budget' })
  })

  it('uploads a commercial pdf', async () => {
    mockedUploadCommercialPdf.mockResolvedValue({ id: 1 } as never)
    const formData = new FormData()
    const { result } = renderHook(() => useUploadCommercialPdf(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ proposalId: 1, formData })

    expect(mockedUploadCommercialPdf).toHaveBeenCalledWith(1, formData)
  })

  it('deletes a commercial pdf', async () => {
    mockedDeleteCommercialPdf.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteCommercialPdf(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ proposalId: 1, documentId: 2 })

    expect(mockedDeleteCommercialPdf).toHaveBeenCalledWith(1, 2)
  })

  it('uploads a proposal document', async () => {
    mockedUploadProposalDocument.mockResolvedValue({ id: 1 } as never)
    const formData = new FormData()
    const { result } = renderHook(() => useUploadProposalDocument(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ proposalId: 1, formData })

    expect(mockedUploadProposalDocument).toHaveBeenCalledWith(1, formData)
  })

  it('deletes a proposal document', async () => {
    mockedDeleteProposalDocument.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteProposalDocument(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ proposalId: 1, documentId: 2 })

    expect(mockedDeleteProposalDocument).toHaveBeenCalledWith(1, 2)
  })
})
