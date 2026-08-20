import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useUsers, useUser } from '../queries/useAdminUsers'
import { getUsers, getUser } from '../services/admin.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/admin.service', () => ({
  getUsers: vi.fn(),
  getUser: vi.fn(),
}))

const mockedGetUsers = vi.mocked(getUsers)
const mockedGetUser = vi.mocked(getUser)

describe('admin user query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the user list', async () => {
    const users = [{ id: 1, email: 'a@example.com' }]
    mockedGetUsers.mockResolvedValue(users as never)

    const { result } = renderHook(() => useUsers(), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(users))
  })

  it('loads a single user', async () => {
    const user = { id: 1, email: 'a@example.com' }
    mockedGetUser.mockResolvedValue(user as never)

    const { result } = renderHook(() => useUser(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(user))
  })
})
