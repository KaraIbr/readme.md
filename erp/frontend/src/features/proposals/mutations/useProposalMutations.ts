import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import {
  createProposal,
  updateProposal,
  deleteProposal,
  moveProposalStage,
  markProposalWon,
  markProposalLost,
  uploadCommercialPdf,
  deleteCommercialPdf,
  uploadProposalDocument,
  deleteProposalDocument,
} from '../services/proposal.service'

export function useCreateProposal() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createProposal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.all })
    },
  })
}

export function useUpdateProposal() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Parameters<typeof updateProposal>[1] }) => updateProposal(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.all })
    },
  })
}

export function useDeleteProposal() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteProposal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.all })
    },
  })
}

export function useMoveProposalStage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Parameters<typeof moveProposalStage>[1] }) => moveProposalStage(id, body),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.detail(variables.id) })
    },
  })
}

export function useMarkProposalWon() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: markProposalWon,
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.detail(variables) })
    },
  })
}

export function useMarkProposalLost() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Parameters<typeof markProposalLost>[1] }) => markProposalLost(id, body),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.detail(variables.id) })
    },
  })
}

export function useUploadCommercialPdf() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ proposalId, formData }: { proposalId: number; formData: FormData }) => uploadCommercialPdf(proposalId, formData),
    onSuccess: (_data, { proposalId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.commercialPdf(proposalId) })
    },
  })
}

export function useDeleteCommercialPdf() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ proposalId, documentId }: { proposalId: number; documentId: number }) => deleteCommercialPdf(proposalId, documentId),
    onSuccess: (_data, { proposalId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.commercialPdf(proposalId) })
    },
  })
}

export function useUploadProposalDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ proposalId, formData }: { proposalId: number; formData: FormData }) => uploadProposalDocument(proposalId, formData),
    onSuccess: (_data, { proposalId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.documents(proposalId) })
    },
  })
}

export function useDeleteProposalDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ proposalId, documentId }: { proposalId: number; documentId: number }) => deleteProposalDocument(proposalId, documentId),
    onSuccess: (_data, { proposalId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.documents(proposalId) })
    },
  })
}
