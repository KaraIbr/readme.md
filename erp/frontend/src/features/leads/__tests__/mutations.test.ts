import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import {
  useCreateLead,
  useUpdateLead,
  useDeleteLead,
  useMoveLeadStage,
  useCloseLead,
  useUploadLeadDocument,
  useDeleteLeadDocument,
  useUploadLeadElectricityBill,
  useDeleteLeadElectricityBill,
  useCreateLeadInteraction,
  useUpdateLeadInteraction,
  useDeleteLeadInteraction,
} from '../mutations/useLeadMutations'
import {
  createLead,
  updateLead,
  deleteLead,
  moveLeadStage,
  closeLead,
  uploadLeadDocument,
  deleteLeadDocument,
  uploadLeadElectricityBill,
  deleteLeadElectricityBill,
  createLeadInteraction,
  updateLeadInteraction,
  deleteLeadInteraction,
} from '../services/lead.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/lead.service', () => ({
  createLead: vi.fn(),
  updateLead: vi.fn(),
  deleteLead: vi.fn(),
  moveLeadStage: vi.fn(),
  closeLead: vi.fn(),
  uploadLeadDocument: vi.fn(),
  deleteLeadDocument: vi.fn(),
  uploadLeadElectricityBill: vi.fn(),
  deleteLeadElectricityBill: vi.fn(),
  createLeadInteraction: vi.fn(),
  updateLeadInteraction: vi.fn(),
  deleteLeadInteraction: vi.fn(),
}))

const mockedCreateLead = vi.mocked(createLead)
const mockedUpdateLead = vi.mocked(updateLead)
const mockedDeleteLead = vi.mocked(deleteLead)
const mockedMoveLeadStage = vi.mocked(moveLeadStage)
const mockedCloseLead = vi.mocked(closeLead)
const mockedUploadLeadDocument = vi.mocked(uploadLeadDocument)
const mockedDeleteLeadDocument = vi.mocked(deleteLeadDocument)
const mockedUploadLeadElectricityBill = vi.mocked(uploadLeadElectricityBill)
const mockedDeleteLeadElectricityBill = vi.mocked(deleteLeadElectricityBill)
const mockedCreateLeadInteraction = vi.mocked(createLeadInteraction)
const mockedUpdateLeadInteraction = vi.mocked(updateLeadInteraction)
const mockedDeleteLeadInteraction = vi.mocked(deleteLeadInteraction)

describe('lead mutation hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates a lead', async () => {
    mockedCreateLead.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useCreateLead(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ contact_id: 1, title: 'Solar', interest_type: 'BESS' })

    expect(mockedCreateLead).toHaveBeenCalledWith({ contact_id: 1, title: 'Solar', interest_type: 'BESS' }, expect.anything())
  })

  it('updates a lead', async () => {
    mockedUpdateLead.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateLead(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, body: { title: 'Renamed' } })

    expect(mockedUpdateLead).toHaveBeenCalledWith(1, { title: 'Renamed' })
  })

  it('deletes a lead', async () => {
    mockedDeleteLead.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteLead(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(1)

    expect(mockedDeleteLead).toHaveBeenCalledWith(1, expect.anything())
  })

  it('moves a lead stage', async () => {
    mockedMoveLeadStage.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useMoveLeadStage(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, body: { stage: 'QUALIFYING' } })

    expect(mockedMoveLeadStage).toHaveBeenCalledWith(1, { stage: 'QUALIFYING' })
  })

  it('closes a lead', async () => {
    mockedCloseLead.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useCloseLead(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, body: { outcome: 'WON' } })

    expect(mockedCloseLead).toHaveBeenCalledWith(1, { outcome: 'WON' })
  })

  it('uploads a lead document', async () => {
    mockedUploadLeadDocument.mockResolvedValue({ id: 1 } as never)
    const formData = new FormData()
    const { result } = renderHook(() => useUploadLeadDocument(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ leadId: 1, formData })

    expect(mockedUploadLeadDocument).toHaveBeenCalledWith(1, formData)
  })

  it('deletes a lead document', async () => {
    mockedDeleteLeadDocument.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteLeadDocument(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ leadId: 1, documentId: 2 })

    expect(mockedDeleteLeadDocument).toHaveBeenCalledWith(1, 2)
  })

  it('uploads a lead electricity bill', async () => {
    mockedUploadLeadElectricityBill.mockResolvedValue({ id: 1 } as never)
    const formData = new FormData()
    const { result } = renderHook(() => useUploadLeadElectricityBill(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ leadId: 1, formData })

    expect(mockedUploadLeadElectricityBill).toHaveBeenCalledWith(1, formData)
  })

  it('deletes a lead electricity bill', async () => {
    mockedDeleteLeadElectricityBill.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteLeadElectricityBill(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ leadId: 1, billId: 2 })

    expect(mockedDeleteLeadElectricityBill).toHaveBeenCalledWith(1, 2)
  })

  it('creates a lead interaction', async () => {
    mockedCreateLeadInteraction.mockResolvedValue({ id: 1 } as never)
    const body = { interaction_type: 'CALL', title: 'Call', notes: 'ok', interaction_date: '2026-01-15' } as const
    const { result } = renderHook(() => useCreateLeadInteraction(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ leadId: 1, body })

    expect(mockedCreateLeadInteraction).toHaveBeenCalledWith(1, body)
  })

  it('updates a lead interaction', async () => {
    mockedUpdateLeadInteraction.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateLeadInteraction(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ leadId: 1, interactionId: 2, body: { notes: 'Updated' } })

    expect(mockedUpdateLeadInteraction).toHaveBeenCalledWith(1, 2, { notes: 'Updated' })
  })

  it('deletes a lead interaction', async () => {
    mockedDeleteLeadInteraction.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteLeadInteraction(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ leadId: 1, interactionId: 2 })

    expect(mockedDeleteLeadInteraction).toHaveBeenCalledWith(1, 2)
  })
})
