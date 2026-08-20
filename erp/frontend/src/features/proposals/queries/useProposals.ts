import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import {
  getProposals,
  getProposal,
  getCommercialPdfs,
  getProposalDocuments,
} from '../services/proposal.service'
import type { ProposalFilters } from '../types'

export function useProposalList(filters?: ProposalFilters) {
  return useQuery({
    queryKey: queryKeys.proposals.list(filters as Record<string, unknown>),
    queryFn: () => getProposals(filters),
  })
}

export function useProposal(id: number) {
  return useQuery({
    queryKey: queryKeys.proposals.detail(id),
    queryFn: () => getProposal(id),
    enabled: !!id,
  })
}

export function useProposalCommercialPdfs(proposalId: number) {
  return useQuery({
    queryKey: queryKeys.proposals.commercialPdf(proposalId),
    queryFn: () => getCommercialPdfs(proposalId),
    enabled: !!proposalId,
  })
}

export function useProposalDocuments(proposalId: number) {
  return useQuery({
    queryKey: queryKeys.proposals.documents(proposalId),
    queryFn: () => getProposalDocuments(proposalId),
    enabled: !!proposalId,
  })
}
