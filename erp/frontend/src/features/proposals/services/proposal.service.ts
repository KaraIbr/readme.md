import { api } from '@services/api-client'
import { env } from '@lib/env'
import { wrapPaginated } from '@shared/utils/pagination'
import type { PaginatedResponse } from '@shared/types'
import type {
  ProposalRead,
  ProposalCreate,
  ProposalUpdate,
  ProposalStageChange,
  ProposalLost,
  ProposalFilters,
  ProposalCommercialDocumentRead,
  ProposalDocumentRead,
} from '../types'

export async function getProposals(params?: ProposalFilters): Promise<PaginatedResponse<ProposalRead>> {
  const { data } = await api.get<ProposalRead[]>('/proposals/', { params })
  return wrapPaginated(data)
}

export async function getProposal(id: number): Promise<ProposalRead> {
  const { data } = await api.get<ProposalRead>(`/proposals/${id}`)
  return data
}

export async function createProposal(body: ProposalCreate): Promise<ProposalRead> {
  const { data } = await api.post<ProposalRead>('/proposals/', body)
  return data
}

export async function updateProposal(id: number, body: ProposalUpdate): Promise<ProposalRead> {
  const { data } = await api.patch<ProposalRead>(`/proposals/${id}`, body)
  return data
}

export async function deleteProposal(id: number): Promise<void> {
  await api.delete(`/proposals/${id}`)
}

export async function moveProposalStage(id: number, body: ProposalStageChange): Promise<ProposalRead> {
  const { data } = await api.post<ProposalRead>(`/proposals/${id}/stage`, body)
  return data
}

export async function markProposalWon(id: number): Promise<ProposalRead> {
  const { data } = await api.post<ProposalRead>(`/proposals/${id}/won`)
  return data
}

export async function markProposalLost(id: number, body: ProposalLost): Promise<ProposalRead> {
  const { data } = await api.post<ProposalRead>(`/proposals/${id}/lost`, body)
  return data
}

export async function getCommercialPdfs(proposalId: number): Promise<ProposalCommercialDocumentRead[]> {
  const { data } = await api.get<ProposalCommercialDocumentRead[]>(`/proposals/${proposalId}/commercial-pdf`)
  return data
}

export async function uploadCommercialPdf(proposalId: number, formData: FormData): Promise<ProposalCommercialDocumentRead> {
  const { data } = await api.post<ProposalCommercialDocumentRead>(`/proposals/${proposalId}/commercial-pdf`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export function getCommercialPdfDownloadUrl(proposalId: number, documentId: number): string {
  return `${env.apiBaseUrl}/proposals/${proposalId}/commercial-pdf/${documentId}/download`
}

export async function deleteCommercialPdf(proposalId: number, documentId: number): Promise<void> {
  await api.delete(`/proposals/${proposalId}/commercial-pdf/${documentId}`)
}

export async function getProposalDocuments(proposalId: number): Promise<ProposalDocumentRead[]> {
  const { data } = await api.get<ProposalDocumentRead[]>(`/proposals/${proposalId}/documents`)
  return data
}

export async function uploadProposalDocument(proposalId: number, formData: FormData): Promise<ProposalDocumentRead> {
  const { data } = await api.post<ProposalDocumentRead>(`/proposals/${proposalId}/documents`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export function getProposalDocumentDownloadUrl(proposalId: number, documentId: number): string {
  return `${env.apiBaseUrl}/proposals/${proposalId}/documents/${documentId}/download`
}

export async function deleteProposalDocument(proposalId: number, documentId: number): Promise<void> {
  await api.delete(`/proposals/${proposalId}/documents/${documentId}`)
}
