import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import {
  useCreateVisit,
  useUpdateVisit,
  useCompleteVisit,
  useCancelVisit,
  useSetVisitRequirement,
  useUploadVisitAttachment,
  useDeleteVisitAttachment,
} from '../mutations/useVisitMutations'
import {
  createVisit,
  updateVisit,
  completeVisit,
  cancelVisit,
  setVisitRequirement,
  uploadVisitAttachment,
  deleteVisitAttachment,
} from '../services/visit.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/visit.service', () => ({
  createVisit: vi.fn(),
  updateVisit: vi.fn(),
  completeVisit: vi.fn(),
  cancelVisit: vi.fn(),
  setVisitRequirement: vi.fn(),
  uploadVisitAttachment: vi.fn(),
  deleteVisitAttachment: vi.fn(),
}))

const mockedCreateVisit = vi.mocked(createVisit)
const mockedUpdateVisit = vi.mocked(updateVisit)
const mockedCompleteVisit = vi.mocked(completeVisit)
const mockedCancelVisit = vi.mocked(cancelVisit)
const mockedSetVisitRequirement = vi.mocked(setVisitRequirement)
const mockedUploadVisitAttachment = vi.mocked(uploadVisitAttachment)
const mockedDeleteVisitAttachment = vi.mocked(deleteVisitAttachment)

describe('visit mutation hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates a visit', async () => {
    mockedCreateVisit.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useCreateVisit(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ leadId: 1, body: { scheduled_at: '2026-01-20' } })

    expect(mockedCreateVisit).toHaveBeenCalledWith(1, { scheduled_at: '2026-01-20' })
  })

  it('updates a visit', async () => {
    mockedUpdateVisit.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateVisit(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, body: { receiver_name: 'Owner' } })

    expect(mockedUpdateVisit).toHaveBeenCalledWith(1, { receiver_name: 'Owner' })
  })

  it('completes a visit', async () => {
    mockedCompleteVisit.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useCompleteVisit(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(1)

    expect(mockedCompleteVisit).toHaveBeenCalledWith(1, expect.anything())
  })

  it('cancels a visit', async () => {
    mockedCancelVisit.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useCancelVisit(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, reason: 'Client unavailable' })

    expect(mockedCancelVisit).toHaveBeenCalledWith(1, 'Client unavailable')
  })

  it('sets the visit requirement', async () => {
    mockedSetVisitRequirement.mockResolvedValue({ requirement: 'REQUIRED' })
    const { result } = renderHook(() => useSetVisitRequirement(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ leadId: 1, requirement: 'REQUIRED' })

    expect(mockedSetVisitRequirement).toHaveBeenCalledWith(1, 'REQUIRED')
  })

  it('uploads a visit attachment', async () => {
    mockedUploadVisitAttachment.mockResolvedValue({ id: 1 } as never)
    const formData = new FormData()
    const { result } = renderHook(() => useUploadVisitAttachment(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ visitId: 1, formData })

    expect(mockedUploadVisitAttachment).toHaveBeenCalledWith(1, formData)
  })

  it('deletes a visit attachment', async () => {
    mockedDeleteVisitAttachment.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteVisitAttachment(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ visitId: 1, attachmentId: 2 })

    expect(mockedDeleteVisitAttachment).toHaveBeenCalledWith(1, 2)
  })
})
