import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import {
  createLead,
  updateLead,
  deleteLead,
  moveLeadStage,
  closeLead,
  uploadLeadDocument,
  deleteLeadDocument,
  uploadLeadElectricityBill,
  deleteLeadElectricityBill,
  createLeadInteraction,
  updateLeadInteraction,
  deleteLeadInteraction,
} from '../services/lead.service'

export function useCreateLead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createLead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.all })
    },
  })
}

export function useUpdateLead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Parameters<typeof updateLead>[1] }) => updateLead(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.all })
    },
  })
}

export function useDeleteLead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteLead,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.all })
    },
  })
}

export function useMoveLeadStage() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Parameters<typeof moveLeadStage>[1] }) => moveLeadStage(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.all })
    },
  })
}

export function useCloseLead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Parameters<typeof closeLead>[1] }) => closeLead(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.all })
    },
  })
}

export function useUploadLeadDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, formData }: { leadId: number; formData: FormData }) => uploadLeadDocument(leadId, formData),
    onSuccess: (_data, { leadId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.documents(leadId) })
    },
  })
}

export function useDeleteLeadDocument() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, documentId }: { leadId: number; documentId: number }) => deleteLeadDocument(leadId, documentId),
    onSuccess: (_data, { leadId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.documents(leadId) })
    },
  })
}

export function useUploadLeadElectricityBill() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, formData }: { leadId: number; formData: FormData }) => uploadLeadElectricityBill(leadId, formData),
    onSuccess: (_data, { leadId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.electricityBills(leadId) })
    },
  })
}

export function useDeleteLeadElectricityBill() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, billId }: { leadId: number; billId: number }) => deleteLeadElectricityBill(leadId, billId),
    onSuccess: (_data, { leadId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.electricityBills(leadId) })
    },
  })
}

export function useCreateLeadInteraction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, body }: { leadId: number; body: Parameters<typeof createLeadInteraction>[1] }) => createLeadInteraction(leadId, body),
    onSuccess: (_data, { leadId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.interactions(leadId) })
    },
  })
}

export function useUpdateLeadInteraction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, interactionId, body }: { leadId: number; interactionId: number; body: Parameters<typeof updateLeadInteraction>[2] }) => updateLeadInteraction(leadId, interactionId, body),
    onSuccess: (_data, { leadId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.interactions(leadId) })
    },
  })
}

export function useDeleteLeadInteraction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ leadId, interactionId }: { leadId: number; interactionId: number }) => deleteLeadInteraction(leadId, interactionId),
    onSuccess: (_data, { leadId }) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.leads.interactions(leadId) })
    },
  })
}
