import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import {
  getLeads,
  getLead,
  getLeadDocuments,
  getLeadElectricityBills,
  getLeadInteractions,
} from '../services/lead.service'
import type { LeadFilters } from '../types'

export function useLeadList(filters?: LeadFilters) {
  return useQuery({
    queryKey: queryKeys.leads.list(filters as Record<string, unknown>),
    queryFn: () => getLeads(filters),
  })
}

export function useLead(id: number) {
  return useQuery({
    queryKey: queryKeys.leads.detail(id),
    queryFn: () => getLead(id),
    enabled: !!id,
  })
}

export function useLeadDocuments(leadId: number) {
  return useQuery({
    queryKey: queryKeys.leads.documents(leadId),
    queryFn: () => getLeadDocuments(leadId),
    enabled: !!leadId,
  })
}

export function useLeadElectricityBills(leadId: number) {
  return useQuery({
    queryKey: queryKeys.leads.electricityBills(leadId),
    queryFn: () => getLeadElectricityBills(leadId),
    enabled: !!leadId,
  })
}

export function useLeadInteractions(leadId: number) {
  return useQuery({
    queryKey: queryKeys.leads.interactions(leadId),
    queryFn: () => getLeadInteractions(leadId),
    enabled: !!leadId,
  })
}
