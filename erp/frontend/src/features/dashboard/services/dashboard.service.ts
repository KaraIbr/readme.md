import { api } from '@services/api-client'

export interface DashboardStats {
  total_contacts: number
  total_leads: number
  active_leads: number
  won_leads: number
  pending_visits: number
  revenue_won: number
  leads_by_stage: Record<string, number>
  proposals_by_stage: Record<string, number>
  recent_transitions: {
    id: number
    entity_type: string
    entity_id: number
    to_stage: string
    transitioned_at: string
  }[]
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const { data } = await api.get<DashboardStats>('/dashboard/stats')
  return data
}
