import { api } from '@services/api-client'
import { env } from '@lib/env'
import { wrapPaginated } from '@shared/utils/pagination'
import type { PaginatedResponse } from '@shared/types'
import type {
  LeadRead,
  LeadCreate,
  LeadUpdate,
  LeadClose,
  LeadStageChange,
  LeadFilters,
  LeadDocumentRead,
  LeadElectricityBillRead,
  LeadInteractionCreate,
  LeadInteractionUpdate,
  LeadInteractionRead,
} from '../types'

export async function getLeads(params?: LeadFilters): Promise<PaginatedResponse<LeadRead>> {
  const { data } = await api.get<LeadRead[]>('/leads/', { params })
  return wrapPaginated(data)
}

export async function getLead(id: number): Promise<LeadRead> {
  const { data } = await api.get<LeadRead>(`/leads/${id}`)
  return data
}

export async function createLead(body: LeadCreate): Promise<LeadRead> {
  const { data } = await api.post<LeadRead>('/leads/', body)
  return data
}

export async function updateLead(id: number, body: LeadUpdate): Promise<LeadRead> {
  const { data } = await api.patch<LeadRead>(`/leads/${id}`, body)
  return data
}

export async function deleteLead(id: number): Promise<void> {
  await api.delete(`/leads/${id}`)
}

export async function moveLeadStage(id: number, body: LeadStageChange): Promise<LeadRead> {
  const { data } = await api.post<LeadRead>(`/leads/${id}/stage`, body)
  return data
}

export async function closeLead(id: number, body: LeadClose): Promise<LeadRead> {
  const { data } = await api.post<LeadRead>(`/leads/${id}/close`, body)
  return data
}

export async function getLeadDocuments(leadId: number): Promise<LeadDocumentRead[]> {
  const { data } = await api.get<LeadDocumentRead[]>(`/leads/${leadId}/documents`)
  return data
}

export async function uploadLeadDocument(leadId: number, formData: FormData): Promise<LeadDocumentRead> {
  const { data } = await api.post<LeadDocumentRead>(`/leads/${leadId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export function getLeadDocumentDownloadUrl(leadId: number, documentId: number): string {
  return `${env.apiBaseUrl}/leads/${leadId}/documents/${documentId}/download`
}

export async function deleteLeadDocument(leadId: number, documentId: number): Promise<void> {
  await api.delete(`/leads/${leadId}/documents/${documentId}`)
}

export async function getLeadElectricityBills(leadId: number): Promise<LeadElectricityBillRead[]> {
  const { data } = await api.get<LeadElectricityBillRead[]>(`/leads/${leadId}/electricity-bills`)
  return data
}

export async function uploadLeadElectricityBill(leadId: number, formData: FormData): Promise<LeadElectricityBillRead> {
  const { data } = await api.post<LeadElectricityBillRead>(`/leads/${leadId}/electricity-bills`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export function getLeadElectricityBillDownloadUrl(leadId: number, billId: number): string {
  return `${env.apiBaseUrl}/leads/${leadId}/electricity-bills/${billId}/download`
}

export async function deleteLeadElectricityBill(leadId: number, billId: number): Promise<void> {
  await api.delete(`/leads/${leadId}/electricity-bills/${billId}`)
}

export async function getLeadInteractions(leadId: number): Promise<LeadInteractionRead[]> {
  const { data } = await api.get<LeadInteractionRead[]>(`/leads/${leadId}/interactions`)
  return data
}

export async function getLeadInteraction(leadId: number, interactionId: number): Promise<LeadInteractionRead> {
  const { data } = await api.get<LeadInteractionRead>(`/leads/${leadId}/interactions/${interactionId}`)
  return data
}

export async function createLeadInteraction(leadId: number, body: LeadInteractionCreate): Promise<LeadInteractionRead> {
  const { data } = await api.post<LeadInteractionRead>(`/leads/${leadId}/interactions`, body)
  return data
}

export async function updateLeadInteraction(leadId: number, interactionId: number, body: LeadInteractionUpdate): Promise<LeadInteractionRead> {
  const { data } = await api.patch<LeadInteractionRead>(`/leads/${leadId}/interactions/${interactionId}`, body)
  return data
}

export async function deleteLeadInteraction(leadId: number, interactionId: number): Promise<void> {
  await api.delete(`/leads/${leadId}/interactions/${interactionId}`)
}
