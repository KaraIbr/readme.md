import { describe, it, expect } from 'vitest'
import {
  leadCreateSchema,
  leadUpdateSchema,
  leadCloseSchema,
  leadStageChangeSchema,
  leadInteractionCreateSchema,
  leadInteractionUpdateSchema,
} from '../schemas/lead.schema'
import { api } from '../../../test/mocks/api-client'
import {
  getLeads,
  getLead,
  createLead,
  updateLead,
  deleteLead,
  moveLeadStage,
  closeLead,
  getLeadDocuments,
  uploadLeadDocument,
  getLeadDocumentDownloadUrl,
  deleteLeadDocument,
  getLeadElectricityBills,
  uploadLeadElectricityBill,
  getLeadElectricityBillDownloadUrl,
  deleteLeadElectricityBill,
  getLeadInteractions,
  getLeadInteraction,
  createLeadInteraction,
  updateLeadInteraction,
  deleteLeadInteraction,
} from '../services/lead.service'

describe('lead schemas', () => {
  it('accepts a valid create payload', () => {
    const result = leadCreateSchema.safeParse({
      contact_id: 1,
      title: 'Solar for warehouse',
      interest_type: 'Photovoltaic',
      qualification_score: 80,
    })
    expect(result.success).toBe(true)
  })

  it('rejects missing contact_id', () => {
    const result = leadCreateSchema.safeParse({ title: 'Solar', interest_type: 'BESS' })
    expect(result.success).toBe(false)
  })

  it('rejects empty title', () => {
    const result = leadCreateSchema.safeParse({
      contact_id: 1,
      title: '',
      interest_type: 'BESS',
    })
    expect(result.success).toBe(false)
  })

  it('rejects an unknown interest type', () => {
    const result = leadCreateSchema.safeParse({
      contact_id: 1,
      title: 'Solar',
      interest_type: 'Other',
    })
    expect(result.success).toBe(false)
  })

  it('rejects qualification score out of range', () => {
    expect(
      leadCreateSchema.safeParse({
        contact_id: 1,
        title: 'Solar',
        interest_type: 'BESS',
        qualification_score: 150,
      }).success,
    ).toBe(false)
    expect(
      leadCreateSchema.safeParse({
        contact_id: 1,
        title: 'Solar',
        interest_type: 'BESS',
        qualification_score: -1,
      }).success,
    ).toBe(false)
  })

  it('accepts a partial update payload', () => {
    const result = leadUpdateSchema.safeParse({ title: 'Renamed' })
    expect(result.success).toBe(true)
  })

  it('accepts close payload with a valid outcome', () => {
    expect(leadCloseSchema.safeParse({ outcome: 'WON' }).success).toBe(true)
  })

  it('rejects close payload with an invalid outcome', () => {
    expect(leadCloseSchema.safeParse({ outcome: 'MAYBE' }).success).toBe(false)
  })

  it('accepts a valid stage change', () => {
    expect(leadStageChangeSchema.safeParse({ stage: 'QUALIFYING' }).success).toBe(true)
  })

  it('rejects an invalid stage change', () => {
    expect(leadStageChangeSchema.safeParse({ stage: 'CLOSED_WON' }).success).toBe(false)
  })

  it('accepts a valid interaction create payload', () => {
    const result = leadInteractionCreateSchema.safeParse({
      interaction_type: 'CALL',
      title: 'Intro call',
      notes: 'Went well',
      interaction_date: '2026-01-15',
    })
    expect(result.success).toBe(true)
  })

  it('rejects interaction without a title', () => {
    const result = leadInteractionCreateSchema.safeParse({
      interaction_type: 'CALL',
      notes: 'Went well',
      interaction_date: '2026-01-15',
    })
    expect(result.success).toBe(false)
  })

  it('accepts a partial interaction update payload', () => {
    const result = leadInteractionUpdateSchema.safeParse({ notes: 'Updated' })
    expect(result.success).toBe(true)
  })
})

describe('lead api service', () => {
  it('lists leads with pagination wrapper', async () => {
    const leads = [{ id: 1, title: 'Solar' }]
    api.get.mockResolvedValue({ data: leads })

    const result = await getLeads({ stage: 'NEW' })

    expect(api.get).toHaveBeenCalledWith('/leads/', { params: { stage: 'NEW' } })
    expect(result).toEqual({ items: leads, total: 1, limit: 1, offset: 0 })
  })

  it('fetches a single lead', async () => {
    const lead = { id: 1, title: 'Solar' }
    api.get.mockResolvedValue({ data: lead })

    const result = await getLead(1)

    expect(api.get).toHaveBeenCalledWith('/leads/1')
    expect(result).toEqual(lead)
  })

  it('creates a lead', async () => {
    const body = { contact_id: 1, title: 'Solar', interest_type: 'BESS' as const }
    api.post.mockResolvedValue({ data: { id: 2, ...body } })

    const result = await createLead(body)

    expect(api.post).toHaveBeenCalledWith('/leads/', body)
    expect(result.id).toBe(2)
  })

  it('updates a lead', async () => {
    const body = { title: 'Renamed' }
    api.patch.mockResolvedValue({ data: { id: 1, ...body } })

    await updateLead(1, body)

    expect(api.patch).toHaveBeenCalledWith('/leads/1', body)
  })

  it('deletes a lead', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteLead(1)

    expect(api.delete).toHaveBeenCalledWith('/leads/1')
  })

  it('moves a lead stage', async () => {
    const body = { stage: 'QUALIFYING' } as const
    api.post.mockResolvedValue({ data: { id: 1, ...body } })

    await moveLeadStage(1, body)

    expect(api.post).toHaveBeenCalledWith('/leads/1/stage', body)
  })

  it('closes a lead', async () => {
    const body = { outcome: 'WON', notes: 'Signed' } as const
    api.post.mockResolvedValue({ data: { id: 1, ...body } })

    await closeLead(1, body)

    expect(api.post).toHaveBeenCalledWith('/leads/1/close', body)
  })

  it('lists lead documents', async () => {
    const docs = [{ id: 1, title: 'contract.pdf' }]
    api.get.mockResolvedValue({ data: docs })

    const result = await getLeadDocuments(1)

    expect(api.get).toHaveBeenCalledWith('/leads/1/documents')
    expect(result).toEqual(docs)
  })

  it('uploads a lead document as multipart form data', async () => {
    const formData = new FormData()
    api.post.mockResolvedValue({ data: { id: 1 } })

    await uploadLeadDocument(1, formData)

    expect(api.post).toHaveBeenCalledWith('/leads/1/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  })

  it('builds the document download url', () => {
    expect(getLeadDocumentDownloadUrl(1, 2)).toBe('/api/v1/leads/1/documents/2/download')
  })

  it('deletes a lead document', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteLeadDocument(1, 2)

    expect(api.delete).toHaveBeenCalledWith('/leads/1/documents/2')
  })

  it('lists electricity bills', async () => {
    const bills = [{ id: 1, title: 'bill.pdf' }]
    api.get.mockResolvedValue({ data: bills })

    const result = await getLeadElectricityBills(1)

    expect(api.get).toHaveBeenCalledWith('/leads/1/electricity-bills')
    expect(result).toEqual(bills)
  })

  it('uploads an electricity bill as multipart form data', async () => {
    const formData = new FormData()
    api.post.mockResolvedValue({ data: { id: 1 } })

    await uploadLeadElectricityBill(1, formData)

    expect(api.post).toHaveBeenCalledWith('/leads/1/electricity-bills', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  })

  it('builds the electricity bill download url', () => {
    expect(getLeadElectricityBillDownloadUrl(1, 2)).toBe('/api/v1/leads/1/electricity-bills/2/download')
  })

  it('deletes an electricity bill', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteLeadElectricityBill(1, 2)

    expect(api.delete).toHaveBeenCalledWith('/leads/1/electricity-bills/2')
  })

  it('lists lead interactions', async () => {
    const interactions = [{ id: 1, title: 'Call' }]
    api.get.mockResolvedValue({ data: interactions })

    const result = await getLeadInteractions(1)

    expect(api.get).toHaveBeenCalledWith('/leads/1/interactions')
    expect(result).toEqual(interactions)
  })

  it('fetches a single interaction', async () => {
    const interaction = { id: 1, title: 'Call' }
    api.get.mockResolvedValue({ data: interaction })

    const result = await getLeadInteraction(1, 2)

    expect(api.get).toHaveBeenCalledWith('/leads/1/interactions/2')
    expect(result).toEqual(interaction)
  })

  it('creates an interaction', async () => {
    const body = { interaction_type: 'CALL', title: 'Call', notes: 'ok', interaction_date: '2026-01-15' } as const
    api.post.mockResolvedValue({ data: { id: 1, ...body } })

    await createLeadInteraction(1, body)

    expect(api.post).toHaveBeenCalledWith('/leads/1/interactions', body)
  })

  it('updates an interaction', async () => {
    const body = { notes: 'Updated' }
    api.patch.mockResolvedValue({ data: { id: 1, ...body } })

    await updateLeadInteraction(1, 2, body)

    expect(api.patch).toHaveBeenCalledWith('/leads/1/interactions/2', body)
  })

  it('deletes an interaction', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteLeadInteraction(1, 2)

    expect(api.delete).toHaveBeenCalledWith('/leads/1/interactions/2')
  })
})
