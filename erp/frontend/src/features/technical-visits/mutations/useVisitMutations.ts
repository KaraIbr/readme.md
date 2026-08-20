import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import {
  createVisit,
  updateVisit,
  completeVisit,
  cancelVisit,
  setVisitRequirement,
  uploadVisitAttachment,
  deleteVisitAttachment,
} from '../services/visit.service'

export function useCreateVisit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, body }: { leadId: number; body: Parameters<typeof createVisit>[1] }) => createVisit(leadId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.technicalVisits.all })
    },
  })
}

export function useUpdateVisit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Parameters<typeof updateVisit>[1] }) => updateVisit(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.technicalVisits.all })
    },
  })
}

export function useCompleteVisit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: completeVisit,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.technicalVisits.all })
    },
  })
}

export function useCancelVisit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, reason }: { id: number; reason: string }) => cancelVisit(id, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.technicalVisits.all })
    },
  })
}

export function useSetVisitRequirement() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, requirement }: { leadId: number; requirement: 'UNDETERMINED' | 'NOT_REQUIRED' | 'REQUIRED' }) => setVisitRequirement(leadId, requirement),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.all })
    },
  })
}

export function useUploadVisitAttachment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ visitId, formData }: { visitId: number; formData: FormData }) => uploadVisitAttachment(visitId, formData),
    onSuccess: (_data, { visitId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.technicalVisits.attachments(visitId) })
    },
  })
}

export function useDeleteVisitAttachment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ visitId, attachmentId }: { visitId: number; attachmentId: number }) => deleteVisitAttachment(visitId, attachmentId),
    onSuccess: (_data, { visitId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.technicalVisits.attachments(visitId) })
    },
  })
}
