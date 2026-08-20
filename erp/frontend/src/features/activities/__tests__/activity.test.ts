import { describe, it, expect } from 'vitest'
import { activityCreateSchema } from '../schemas/activity.schema'
import { api } from '../../../test/mocks/api-client'
import {
  getActivities,
  getActivity,
  createActivity,
  updateActivity,
  completeActivity,
  deleteActivity,
} from '../services/activity.service'

describe('activity schemas', () => {
  it('accepts a valid create payload', () => {
    const result = activityCreateSchema.safeParse({
      activity_type: 'CALL',
      title: 'Intro call',
      scheduled_at: '2026-01-15T10:00:00Z',
    })
    expect(result.success).toBe(true)
  })

  it('rejects an unknown activity type', () => {
    expect(activityCreateSchema.safeParse({ activity_type: 'CHAT', title: 'x' }).success).toBe(false)
  })

  it('rejects empty title', () => {
    expect(activityCreateSchema.safeParse({ activity_type: 'CALL', title: '' }).success).toBe(false)
  })

  it('coerces empty contact_id to undefined', () => {
    const result = activityCreateSchema.safeParse({
      activity_type: 'EMAIL',
      title: 'Send update',
      contact_id: '',
    })
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.contact_id).toBeUndefined()
    }
  })

  it('accepts numeric optional ids', () => {
    const result = activityCreateSchema.safeParse({
      activity_type: 'MEETING',
      title: 'Site visit',
      contact_id: 3,
      lead_id: 4,
      assigned_to: 2,
    })
    expect(result.success).toBe(true)
  })
})

describe('activity api service', () => {
  it('lists activities with filters', async () => {
    const activities = [{ id: 1, title: 'Intro call' }]
    api.get.mockResolvedValue({ data: activities })

    const result = await getActivities({ activity_type: 'CALL' })

    expect(api.get).toHaveBeenCalledWith('/activities/', { params: { activity_type: 'CALL' } })
    expect(result).toEqual(activities)
  })

  it('fetches a single activity', async () => {
    const activity = { id: 1, title: 'Intro call' }
    api.get.mockResolvedValue({ data: activity })

    const result = await getActivity(1)

    expect(api.get).toHaveBeenCalledWith('/activities/1')
    expect(result).toEqual(activity)
  })

  it('creates an activity', async () => {
    const body = { activity_type: 'CALL', title: 'Intro call' } as const
    api.post.mockResolvedValue({ data: { id: 2, ...body } })

    const result = await createActivity(body)

    expect(api.post).toHaveBeenCalledWith('/activities/', body)
    expect(result.id).toBe(2)
  })

  it('updates an activity', async () => {
    const body = { title: 'Rescheduled' }
    api.patch.mockResolvedValue({ data: { id: 1, ...body } })

    await updateActivity(1, body)

    expect(api.patch).toHaveBeenCalledWith('/activities/1', body)
  })

  it('completes an activity', async () => {
    api.post.mockResolvedValue({ data: { id: 1, completed_at: '2026-01-16' } })

    await completeActivity(1)

    expect(api.post).toHaveBeenCalledWith('/activities/1/complete')
  })

  it('deletes an activity', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteActivity(1)

    expect(api.delete).toHaveBeenCalledWith('/activities/1')
  })
})
