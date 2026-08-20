import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { createOpportunity, updateOpportunity, deleteOpportunity, moveOpportunityStage, closeOpportunity } from '../services/opportunity.service'

export function useCreateOpportunity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createOpportunity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.all })
    },
  })
}

export function useUpdateOpportunity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateOpportunity>[1] }) => updateOpportunity(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.all })
    },
  })
}

export function useDeleteOpportunity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteOpportunity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.all })
    },
  })
}

export function useMoveOpportunityStage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, stage }: { id: number; stage: Parameters<typeof moveOpportunityStage>[1] }) => moveOpportunityStage(id, stage),
    onSuccess: (_data, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.detail(id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.all })
    },
  })
}

export function useCloseOpportunity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof closeOpportunity>[1] }) => closeOpportunity(id, data),
    onSuccess: (_data, { id }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.detail(id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.opportunities.all })
    },
  })
}
