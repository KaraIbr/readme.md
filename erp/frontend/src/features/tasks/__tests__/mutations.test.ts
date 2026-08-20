import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import {
  useCreateTask,
  useUpdateTask,
  useDeleteTask,
  useChangeTaskStatus,
} from '../mutations/useTaskMutations'
import { createTask, updateTask, deleteTask, changeTaskStatus } from '../services/task.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/task.service', () => ({
  createTask: vi.fn(),
  updateTask: vi.fn(),
  deleteTask: vi.fn(),
  changeTaskStatus: vi.fn(),
}))

const mockedCreateTask = vi.mocked(createTask)
const mockedUpdateTask = vi.mocked(updateTask)
const mockedDeleteTask = vi.mocked(deleteTask)
const mockedChangeTaskStatus = vi.mocked(changeTaskStatus)

describe('task mutation hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates a task', async () => {
    mockedCreateTask.mockResolvedValue({ id: 1 } as never)
    const body = { title: 'Follow up', priority: 'HIGH' } as const
    const { result } = renderHook(() => useCreateTask(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(body)

    expect(mockedCreateTask).toHaveBeenCalledWith(body, expect.anything())
  })

  it('updates a task', async () => {
    mockedUpdateTask.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateTask(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, body: { priority: 'URGENT' } })

    expect(mockedUpdateTask).toHaveBeenCalledWith(1, { priority: 'URGENT' })
  })

  it('deletes a task', async () => {
    mockedDeleteTask.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteTask(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(1)

    expect(mockedDeleteTask).toHaveBeenCalledWith(1, expect.anything())
  })

  it('changes a task status', async () => {
    mockedChangeTaskStatus.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useChangeTaskStatus(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, status: 'DONE' })

    expect(mockedChangeTaskStatus).toHaveBeenCalledWith(1, { status: 'DONE' })
  })
})
