import { api } from '@services/api-client'
import { env } from '@lib/env'
import { wrapPaginated } from '@shared/utils/pagination'
import type { PaginatedResponse } from '@shared/types'
import type {
  TechnicalVisitRead,
  TechnicalVisitAttachmentRead,
  VisitCreate,
  VisitUpdate,
  VisitFilters,
} from '../types'

export async function getVisits(params?: VisitFilters): Promise<PaginatedResponse<TechnicalVisitRead>> {
  const { data } = await api.get<TechnicalVisitRead[]>('/technical-visits/', { params })
  return wrapPaginated(data)
}

export async function createVisit(leadId: number, body: Omit<VisitCreate, 'lead_id'>): Promise<TechnicalVisitRead> {
  const { data } = await api.post<TechnicalVisitRead>(`/leads/${leadId}/technical-visits`, body)
  return data
}

export async function updateVisit(id: number, body: VisitUpdate): Promise<TechnicalVisitRead> {
  const { data } = await api.patch<TechnicalVisitRead>(`/technical-visits/${id}`, body)
  return data
}

export async function getVisit(id: number): Promise<TechnicalVisitRead> {
  const { data } = await api.get<TechnicalVisitRead>(`/technical-visits/${id}`)
  return data
}

export async function completeVisit(id: number): Promise<TechnicalVisitRead> {
  const { data } = await api.post<TechnicalVisitRead>(`/technical-visits/${id}/complete`)
  return data
}

export async function cancelVisit(id: number, reason: string): Promise<TechnicalVisitRead> {
  const { data } = await api.post<TechnicalVisitRead>(`/technical-visits/${id}/cancel`, { reason })
  return data
}

export async function getVisitAttachments(visitId: number): Promise<TechnicalVisitAttachmentRead[]> {
  const { data } = await api.get<TechnicalVisitAttachmentRead[]>(`/technical-visits/${visitId}/attachments`)
  return data
}

export async function uploadVisitAttachment(visitId: number, formData: FormData): Promise<TechnicalVisitAttachmentRead> {
  const { data } = await api.post<TechnicalVisitAttachmentRead>(`/technical-visits/${visitId}/attachments`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function setVisitRequirement(leadId: number, requirement: 'UNDETERMINED' | 'NOT_REQUIRED' | 'REQUIRED'): Promise<unknown> {
  const { data } = await api.post(`/leads/${leadId}/technical-visit-requirement`, { requirement })
  return data
}

export function getVisitAttachmentDownloadUrl(visitId: number, attachmentId: number): string {
  return `${env.apiBaseUrl}/technical-visits/${visitId}/attachments/${attachmentId}/download`
}

export async function deleteVisitAttachment(visitId: number, attachmentId: number): Promise<void> {
  await api.delete(`/technical-visits/${visitId}/attachments/${attachmentId}`)
}
