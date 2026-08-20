import { describe, it, expect } from 'vitest'
import { taskCreateSchema, taskUpdateSchema, taskStatusChangeSchema } from '../schemas/task.schema'
import { api } from '../../../test/mocks/api-client'
import {
  getTasks,
  getTask,
  createTask,
  updateTask,
  changeTaskStatus,
  deleteTask,
} from '../services/task.service'

describe('task schemas', () => {
  it('accepts a valid create payload', () => {
    const result = taskCreateSchema.safeParse({
      title: 'Follow up',
      priority: 'HIGH',
      due_date: '2026-01-20',
    })
    expect(result.success).toBe(true)
  })

  it('rejects empty title', () => {
    expect(taskCreateSchema.safeParse({ title: '' }).success).toBe(false)
  })

  it('rejects an unknown priority', () => {
    expect(taskCreateSchema.safeParse({ title: 'Follow up', priority: 'MAX' }).success).toBe(false)
  })

  it('rejects a non-positive contact_id', () => {
    expect(taskCreateSchema.safeParse({ title: 'Follow up', contact_id: 0 }).success).toBe(false)
  })

  it('accepts a partial update payload', () => {
    const result = taskUpdateSchema.safeParse({ priority: 'URGENT' })
    expect(result.success).toBe(true)
  })

  it('accepts a valid status change', () => {
    expect(taskStatusChangeSchema.safeParse({ status: 'DONE' }).success).toBe(true)
  })

  it('rejects an invalid status change', () => {
    expect(taskStatusChangeSchema.safeParse({ status: 'PENDING' }).success).toBe(false)
  })
})

describe('task api service', () => {
  it('lists tasks with filters', async () => {
    const tasks = [{ id: 1, title: 'Follow up' }]
    api.get.mockResolvedValue({ data: tasks })

    const result = await getTasks({ status: 'TODO' })

    expect(api.get).toHaveBeenCalledWith('/tasks/', { params: { status: 'TODO' } })
    expect(result).toEqual(tasks)
  })

  it('fetches a single task', async () => {
    const task = { id: 1, title: 'Follow up' }
    api.get.mockResolvedValue({ data: task })

    const result = await getTask(1)

    expect(api.get).toHaveBeenCalledWith('/tasks/1')
    expect(result).toEqual(task)
  })

  it('creates a task', async () => {
    const body = { title: 'Follow up', priority: 'HIGH' as const }
    api.post.mockResolvedValue({ data: { id: 2, ...body } })

    const result = await createTask(body)

    expect(api.post).toHaveBeenCalledWith('/tasks/', body)
    expect(result.id).toBe(2)
  })

  it('updates a task', async () => {
    const body = { priority: 'URGENT' } as const
    api.patch.mockResolvedValue({ data: { id: 1, ...body } })

    await updateTask(1, body)

    expect(api.patch).toHaveBeenCalledWith('/tasks/1', body)
  })

  it('changes a task status', async () => {
    const body = { status: 'DONE' } as const
    api.post.mockResolvedValue({ data: { id: 1, ...body } })

    await changeTaskStatus(1, body)

    expect(api.post).toHaveBeenCalledWith('/tasks/1/status', body)
  })

  it('deletes a task', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteTask(1)

    expect(api.delete).toHaveBeenCalledWith('/tasks/1')
  })
})
