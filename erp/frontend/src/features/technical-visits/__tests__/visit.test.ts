import { describe, it, expect } from 'vitest'
import { visitAssigneeSchema, visitCreateSchema, visitUpdateSchema } from '../schemas/visit.schema'
import { api } from '../../../test/mocks/api-client'
import {
  getVisits,
  createVisit,
  updateVisit,
  getVisit,
  completeVisit,
  cancelVisit,
  getVisitAttachments,
  uploadVisitAttachment,
  setVisitRequirement,
  getVisitAttachmentDownloadUrl,
  deleteVisitAttachment,
} from '../services/visit.service'

describe('visit schemas', () => {
  it('accepts a valid create payload', () => {
    const result = visitCreateSchema.safeParse({
      lead_id: 1,
      scheduled_at: '2026-01-20T14:00:00Z',
      assignees: [{ name: 'Tech', user_id: 2 }],
    })
    expect(result.success).toBe(true)
  })

  it('rejects missing lead_id', () => {
    expect(visitCreateSchema.safeParse({ scheduled_at: '2026-01-20' }).success).toBe(false)
  })

  it('rejects an assignee without a name', () => {
    expect(
      visitCreateSchema.safeParse({ lead_id: 1, assignees: [{ user_id: 2 }] }).success,
    ).toBe(false)
  })

  it('defaults assignees to an empty list', () => {
    const result = visitCreateSchema.safeParse({ lead_id: 1 })
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.assignees).toEqual([])
    }
  })

  it('accepts a partial update payload', () => {
    const result = visitUpdateSchema.safeParse({ receiver_name: 'Owner' })
    expect(result.success).toBe(true)
  })

  it('validates the assignee schema directly', () => {
    expect(visitAssigneeSchema.safeParse({ name: 'Tech', user_id: 2 }).success).toBe(true)
    expect(visitAssigneeSchema.safeParse({ name: '' }).success).toBe(false)
  })
})

describe('visit api service', () => {
  it('lists visits with pagination wrapper', async () => {
    const visits = [{ id: 1, status: 'SCHEDULED' }]
    api.get.mockResolvedValue({ data: visits })

    const result = await getVisits({ status: 'SCHEDULED' })

    expect(api.get).toHaveBeenCalledWith('/technical-visits/', { params: { status: 'SCHEDULED' } })
    expect(result).toEqual({ items: visits, total: 1, limit: 1, offset: 0 })
  })

  it('creates a visit scoped to a lead', async () => {
    const body = { scheduled_at: '2026-01-20T14:00:00Z', assignees: [{ name: 'Tech' }] }
    api.post.mockResolvedValue({ data: { id: 1, lead_id: 1, ...body } })

    const result = await createVisit(1, body)

    expect(api.post).toHaveBeenCalledWith('/leads/1/technical-visits', body)
    expect(result.id).toBe(1)
  })

  it('updates a visit', async () => {
    const body = { receiver_name: 'Owner' }
    api.patch.mockResolvedValue({ data: { id: 1, ...body } })

    await updateVisit(1, body)

    expect(api.patch).toHaveBeenCalledWith('/technical-visits/1', body)
  })

  it('fetches a single visit', async () => {
    const visit = { id: 1, status: 'REQUESTED' }
    api.get.mockResolvedValue({ data: visit })

    const result = await getVisit(1)

    expect(api.get).toHaveBeenCalledWith('/technical-visits/1')
    expect(result).toEqual(visit)
  })

  it('completes a visit', async () => {
    api.post.mockResolvedValue({ data: { id: 1, status: 'COMPLETED' } })

    await completeVisit(1)

    expect(api.post).toHaveBeenCalledWith('/technical-visits/1/complete')
  })

  it('cancels a visit with a reason', async () => {
    api.post.mockResolvedValue({ data: { id: 1, status: 'CANCELLED' } })

    await cancelVisit(1, 'Client unavailable')

    expect(api.post).toHaveBeenCalledWith('/technical-visits/1/cancel', {
      reason: 'Client unavailable',
    })
  })

  it('lists visit attachments', async () => {
    const attachments = [{ id: 1, title: 'photo.jpg' }]
    api.get.mockResolvedValue({ data: attachments })

    const result = await getVisitAttachments(1)

    expect(api.get).toHaveBeenCalledWith('/technical-visits/1/attachments')
    expect(result).toEqual(attachments)
  })

  it('uploads a visit attachment as multipart form data', async () => {
    const formData = new FormData()
    api.post.mockResolvedValue({ data: { id: 1 } })

    await uploadVisitAttachment(1, formData)

    expect(api.post).toHaveBeenCalledWith('/technical-visits/1/attachments', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  })

  it('sets the visit requirement for a lead', async () => {
    api.post.mockResolvedValue({ data: { requirement: 'REQUIRED' } })

    const result = await setVisitRequirement(1, 'REQUIRED')

    expect(api.post).toHaveBeenCalledWith('/leads/1/technical-visit-requirement', {
      requirement: 'REQUIRED',
    })
    expect(result).toEqual({ requirement: 'REQUIRED' })
  })

  it('builds the attachment download url', () => {
    expect(getVisitAttachmentDownloadUrl(1, 2)).toBe('/api/v1/technical-visits/1/attachments/2/download')
  })

  it('deletes a visit attachment', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteVisitAttachment(1, 2)

    expect(api.delete).toHaveBeenCalledWith('/technical-visits/1/attachments/2')
  })
})
