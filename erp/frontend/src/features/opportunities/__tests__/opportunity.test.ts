import { describe, it, expect } from 'vitest'
import { opportunityCreateSchema } from '../schemas/opportunity.schema'
import { api } from '../../../test/mocks/api-client'
import {
  getOpportunities,
  getOpportunity,
  createOpportunity,
  updateOpportunity,
  moveOpportunityStage,
  closeOpportunity,
  deleteOpportunity,
} from '../services/opportunity.service'

describe('opportunity schemas', () => {
  it('accepts a valid create payload', () => {
    const result = opportunityCreateSchema.safeParse({
      name: 'Expansion deal',
      contact_id: 1,
      value: 25000,
    })
    expect(result.success).toBe(true)
  })

  it('rejects empty name', () => {
    expect(opportunityCreateSchema.safeParse({ name: '', contact_id: 1 }).success).toBe(false)
  })

  it('rejects missing contact', () => {
    expect(opportunityCreateSchema.safeParse({ name: 'Deal' }).success).toBe(false)
  })

  it('rejects a non-positive contact_id', () => {
    expect(opportunityCreateSchema.safeParse({ name: 'Deal', contact_id: 0 }).success).toBe(false)
  })

  it('coerces empty lead_id to undefined', () => {
    const result = opportunityCreateSchema.safeParse({
      name: 'Deal',
      contact_id: 1,
      lead_id: '',
    })
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.lead_id).toBeUndefined()
    }
  })
})

describe('opportunity api service', () => {
  it('lists opportunities with stage filter', async () => {
    const opportunities = [{ id: 1, name: 'Deal' }]
    api.get.mockResolvedValue({ data: opportunities })

    const result = await getOpportunities({ stage: 'PROPOSAL' })

    expect(api.get).toHaveBeenCalledWith('/opportunities/', { params: { stage: 'PROPOSAL' } })
    expect(result).toEqual(opportunities)
  })

  it('fetches a single opportunity', async () => {
    const opportunity = { id: 1, name: 'Deal' }
    api.get.mockResolvedValue({ data: opportunity })

    const result = await getOpportunity(1)

    expect(api.get).toHaveBeenCalledWith('/opportunities/1')
    expect(result).toEqual(opportunity)
  })

  it('creates an opportunity', async () => {
    const body = { name: 'Deal', contact_id: 1, value: 1000 }
    api.post.mockResolvedValue({ data: { id: 2, ...body } })

    const result = await createOpportunity(body)

    expect(api.post).toHaveBeenCalledWith('/opportunities/', body)
    expect(result.id).toBe(2)
  })

  it('updates an opportunity', async () => {
    const body = { value: 5000 }
    api.patch.mockResolvedValue({ data: { id: 1, ...body } })

    await updateOpportunity(1, body)

    expect(api.patch).toHaveBeenCalledWith('/opportunities/1', body)
  })

  it('moves an opportunity stage', async () => {
    const body = { stage: 'NEGOTIATION' } as const
    api.post.mockResolvedValue({ data: { id: 1, ...body } })

    await moveOpportunityStage(1, body)

    expect(api.post).toHaveBeenCalledWith('/opportunities/1/stage', body)
  })

  it('closes an opportunity', async () => {
    const body = { outcome: 'WON' } as const
    api.post.mockResolvedValue({ data: { id: 1, ...body } })

    await closeOpportunity(1, body)

    expect(api.post).toHaveBeenCalledWith('/opportunities/1/close', body)
  })

  it('deletes an opportunity', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteOpportunity(1)

    expect(api.delete).toHaveBeenCalledWith('/opportunities/1')
  })
})
