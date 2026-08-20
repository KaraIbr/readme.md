import { api } from '@services/api-client'
import type { OpportunityRead, OpportunityCreate, OpportunityUpdate, OpportunityStageChange, OpportunityClose } from '../types'

export async function getOpportunities(params?: { stage?: string }): Promise<OpportunityRead[]> {
  const { data } = await api.get<OpportunityRead[]>('/opportunities/', { params })
  return data
}

export async function getOpportunity(id: number): Promise<OpportunityRead> {
  const { data } = await api.get(`/opportunities/${id}`)
  return data
}

export async function createOpportunity(body: OpportunityCreate): Promise<OpportunityRead> {
  const { data } = await api.post('/opportunities/', body)
  return data
}

export async function updateOpportunity(id: number, body: OpportunityUpdate): Promise<OpportunityRead> {
  const { data } = await api.patch(`/opportunities/${id}`, body)
  return data
}

export async function moveOpportunityStage(id: number, body: OpportunityStageChange): Promise<OpportunityRead> {
  const { data } = await api.post(`/opportunities/${id}/stage`, body)
  return data
}

export async function closeOpportunity(id: number, body: OpportunityClose): Promise<OpportunityRead> {
  const { data } = await api.post(`/opportunities/${id}/close`, body)
  return data
}

export async function deleteOpportunity(id: number): Promise<void> {
  await api.delete(`/opportunities/${id}`)
}
