import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useTasks, useTask } from '../queries/useTasks'
import { getTasks, getTask } from '../services/task.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/task.service', () => ({
  getTasks: vi.fn(),
  getTask: vi.fn(),
}))

const mockedGetTasks = vi.mocked(getTasks)
const mockedGetTask = vi.mocked(getTask)

describe('task query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the task list', async () => {
    const tasks = [{ id: 1, title: 'Follow up' }]
    mockedGetTasks.mockResolvedValue(tasks as never)

    const { result } = renderHook(() => useTasks({ status: 'TODO' }), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(tasks))
    expect(mockedGetTasks).toHaveBeenCalledWith({ status: 'TODO' })
  })

  it('loads a single task', async () => {
    const task = { id: 1, title: 'Follow up' }
    mockedGetTask.mockResolvedValue(task as never)

    const { result } = renderHook(() => useTask(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(task))
  })
})
