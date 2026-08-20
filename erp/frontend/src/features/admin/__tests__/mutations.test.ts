import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useCreateUser } from '../mutations/useCreateUser'
import { useUpdateUser } from '../mutations/useUpdateUser'
import { useDeleteUser } from '../mutations/useDeleteUser'
import { createUser, updateUser, deleteUser } from '../services/admin.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/admin.service', () => ({
  createUser: vi.fn(),
  updateUser: vi.fn(),
  deleteUser: vi.fn(),
}))

const mockedCreateUser = vi.mocked(createUser)
const mockedUpdateUser = vi.mocked(updateUser)
const mockedDeleteUser = vi.mocked(deleteUser)

describe('admin user mutation hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates a user', async () => {
    mockedCreateUser.mockResolvedValue({ id: 1 } as never)
    const body = { email: 'a@example.com', password: 'strong-password', role: 'SALES' }
    const { result } = renderHook(() => useCreateUser(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(body)

    expect(mockedCreateUser).toHaveBeenCalledWith(body, expect.anything())
  })

  it('updates a user', async () => {
    mockedUpdateUser.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateUser(1), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ full_name: 'Updated' })

    expect(mockedUpdateUser).toHaveBeenCalledWith(1, { full_name: 'Updated' })
  })

  it('deletes a user', async () => {
    mockedDeleteUser.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteUser(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(3)

    expect(mockedDeleteUser).toHaveBeenCalledWith(3, expect.anything())
  })
})
