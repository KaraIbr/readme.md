import { describe, it, expect } from 'vitest'
import {
  proposalCreateSchema,
  proposalUpdateSchema,
  proposalStageChangeSchema,
  proposalLostSchema,
} from '../schemas/proposal.schema'
import { api } from '../../../test/mocks/api-client'
import {
  getProposals,
  getProposal,
  createProposal,
  updateProposal,
  deleteProposal,
  moveProposalStage,
  markProposalWon,
  markProposalLost,
  getCommercialPdfs,
  uploadCommercialPdf,
  getCommercialPdfDownloadUrl,
  deleteCommercialPdf,
  getProposalDocuments,
  uploadProposalDocument,
  getProposalDocumentDownloadUrl,
  deleteProposalDocument,
} from '../services/proposal.service'

describe('proposal schemas', () => {
  it('accepts a valid create payload', () => {
    const result = proposalCreateSchema.safeParse({
      lead_id: 1,
      name: 'Solar proposal',
      system_type: 'PV',
      currency: 'MXN',
    })
    expect(result.success).toBe(true)
  })

  it('rejects missing lead_id', () => {
    const result = proposalCreateSchema.safeParse({ name: 'Solar proposal' })
    expect(result.success).toBe(false)
  })

  it('rejects empty name', () => {
    const result = proposalCreateSchema.safeParse({ lead_id: 1, name: '' })
    expect(result.success).toBe(false)
  })

  it('rejects an unknown system type', () => {
    const result = proposalCreateSchema.safeParse({
      lead_id: 1,
      name: 'Solar',
      system_type: 'WIND',
    })
    expect(result.success).toBe(false)
  })

  it('rejects an unknown currency', () => {
    const result = proposalCreateSchema.safeParse({
      lead_id: 1,
      name: 'Solar',
      currency: 'BRL',
    })
    expect(result.success).toBe(false)
  })

  it('accepts nested pv_system with positive power', () => {
    const result = proposalCreateSchema.safeParse({
      lead_id: 1,
      name: 'Solar',
      pv_system: { panel_count: 10, panel_power: 550 },
    })
    expect(result.success).toBe(true)
  })

  it('rejects nested pv_system with non-positive power', () => {
    const result = proposalCreateSchema.safeParse({
      lead_id: 1,
      name: 'Solar',
      pv_system: { panel_power: -5 },
    })
    expect(result.success).toBe(false)
  })

  it('accepts a partial update payload', () => {
    const result = proposalUpdateSchema.safeParse({ total_price: 1000 })
    expect(result.success).toBe(true)
  })

  it('accepts a valid stage change', () => {
    expect(proposalStageChangeSchema.safeParse({ stage: 'SENT' }).success).toBe(true)
  })

  it('rejects a terminal stage in stage change', () => {
    expect(proposalStageChangeSchema.safeParse({ stage: 'WON' }).success).toBe(false)
  })

  it('requires a loss reason', () => {
    expect(proposalLostSchema.safeParse({ loss_reason: '' }).success).toBe(false)
    expect(proposalLostSchema.safeParse({ loss_reason: 'Too expensive' }).success).toBe(true)
  })
})

describe('proposal api service', () => {
  it('lists proposals with pagination wrapper', async () => {
    const proposals = [{ id: 1, name: 'Solar' }]
    api.get.mockResolvedValue({ data: proposals })

    const result = await getProposals({ stage: 'DRAFT' })

    expect(api.get).toHaveBeenCalledWith('/proposals/', { params: { stage: 'DRAFT' } })
    expect(result).toEqual({ items: proposals, total: 1, limit: 1, offset: 0 })
  })

  it('fetches a single proposal', async () => {
    const proposal = { id: 1, name: 'Solar' }
    api.get.mockResolvedValue({ data: proposal })

    const result = await getProposal(1)

    expect(api.get).toHaveBeenCalledWith('/proposals/1')
    expect(result).toEqual(proposal)
  })

  it('creates a proposal', async () => {
    const body = { lead_id: 1, name: 'Solar proposal' }
    api.post.mockResolvedValue({ data: { id: 2, ...body } })

    const result = await createProposal(body)

    expect(api.post).toHaveBeenCalledWith('/proposals/', body)
    expect(result.id).toBe(2)
  })

  it('updates a proposal', async () => {
    const body = { name: 'Renamed' }
    api.patch.mockResolvedValue({ data: { id: 1, ...body } })

    await updateProposal(1, body)

    expect(api.patch).toHaveBeenCalledWith('/proposals/1', body)
  })

  it('deletes a proposal', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteProposal(1)

    expect(api.delete).toHaveBeenCalledWith('/proposals/1')
  })

  it('moves a proposal stage', async () => {
    const body = { stage: 'SENT' } as const
    api.post.mockResolvedValue({ data: { id: 1, ...body } })

    await moveProposalStage(1, body)

    expect(api.post).toHaveBeenCalledWith('/proposals/1/stage', body)
  })

  it('marks a proposal won', async () => {
    api.post.mockResolvedValue({ data: { id: 1, current_stage: 'WON' } })

    await markProposalWon(1)

    expect(api.post).toHaveBeenCalledWith('/proposals/1/won')
  })

  it('marks a proposal lost', async () => {
    const body = { loss_reason: 'Budget' }
    api.post.mockResolvedValue({ data: { id: 1, ...body } })

    await markProposalLost(1, body)

    expect(api.post).toHaveBeenCalledWith('/proposals/1/lost', body)
  })

  it('lists commercial pdfs', async () => {
    const docs = [{ id: 1, title: 'pdf' }]
    api.get.mockResolvedValue({ data: docs })

    const result = await getCommercialPdfs(1)

    expect(api.get).toHaveBeenCalledWith('/proposals/1/commercial-pdf')
    expect(result).toEqual(docs)
  })

  it('uploads a commercial pdf as multipart form data', async () => {
    const formData = new FormData()
    api.post.mockResolvedValue({ data: { id: 1 } })

    await uploadCommercialPdf(1, formData)

    expect(api.post).toHaveBeenCalledWith('/proposals/1/commercial-pdf', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  })

  it('builds the commercial pdf download url', () => {
    expect(getCommercialPdfDownloadUrl(1, 2)).toBe('/api/v1/proposals/1/commercial-pdf/2/download')
  })

  it('deletes a commercial pdf', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteCommercialPdf(1, 2)

    expect(api.delete).toHaveBeenCalledWith('/proposals/1/commercial-pdf/2')
  })

  it('lists proposal documents', async () => {
    const docs = [{ id: 1, title: 'doc' }]
    api.get.mockResolvedValue({ data: docs })

    const result = await getProposalDocuments(1)

    expect(api.get).toHaveBeenCalledWith('/proposals/1/documents')
    expect(result).toEqual(docs)
  })

  it('uploads a proposal document as multipart form data', async () => {
    const formData = new FormData()
    api.post.mockResolvedValue({ data: { id: 1 } })

    await uploadProposalDocument(1, formData)

    expect(api.post).toHaveBeenCalledWith('/proposals/1/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  })

  it('builds the document download url', () => {
    expect(getProposalDocumentDownloadUrl(1, 2)).toBe('/api/v1/proposals/1/documents/2/download')
  })

  it('deletes a proposal document', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteProposalDocument(1, 2)

    expect(api.delete).toHaveBeenCalledWith('/proposals/1/documents/2')
  })
})
