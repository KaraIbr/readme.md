import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useVisitList, useVisit, useVisitAttachments } from '../queries/useVisits'
import { getVisits, getVisit, getVisitAttachments } from '../services/visit.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/visit.service', () => ({
  getVisits: vi.fn(),
  getVisit: vi.fn(),
  getVisitAttachments: vi.fn(),
}))

const mockedGetVisits = vi.mocked(getVisits)
const mockedGetVisit = vi.mocked(getVisit)
const mockedGetVisitAttachments = vi.mocked(getVisitAttachments)

describe('visit query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the visit list', async () => {
    const page = { items: [{ id: 1, status: 'SCHEDULED' }], total: 1, limit: 1, offset: 0 }
    mockedGetVisits.mockResolvedValue(page as never)

    const { result } = renderHook(() => useVisitList({ status: 'SCHEDULED' }), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(page))
    expect(mockedGetVisits).toHaveBeenCalledWith({ status: 'SCHEDULED' })
  })

  it('loads a single visit', async () => {
    const visit = { id: 1, status: 'REQUESTED' }
    mockedGetVisit.mockResolvedValue(visit as never)

    const { result } = renderHook(() => useVisit(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(visit))
  })

  it('loads visit attachments', async () => {
    const attachments = [{ id: 1, title: 'photo.jpg' }]
    mockedGetVisitAttachments.mockResolvedValue(attachments as never)

    const { result } = renderHook(() => useVisitAttachments(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(attachments))
  })
})
