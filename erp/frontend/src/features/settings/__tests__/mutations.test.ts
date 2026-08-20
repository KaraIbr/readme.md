import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import { useUpdateProfile } from '../mutations/useUpdateProfile'
import { updateProfile } from '../services/settings.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/settings.service', () => ({
  updateProfile: vi.fn(),
}))

const mockedUpdateProfile = vi.mocked(updateProfile)

describe('profile mutation hook', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('updates the profile', async () => {
    mockedUpdateProfile.mockResolvedValue(undefined)
    const { result } = renderHook(() => useUpdateProfile(7), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ full_name: 'New Name', email: 'new@example.com' })

    expect(mockedUpdateProfile).toHaveBeenCalledWith(7, { full_name: 'New Name', email: 'new@example.com' })
  })
})
