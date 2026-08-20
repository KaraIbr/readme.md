import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { createActivity, updateActivity, deleteActivity, completeActivity } from '../services/activity.service'

export function useCreateActivity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createActivity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.activities.all })
    },
  })
}

export function useUpdateActivity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateActivity>[1] }) => updateActivity(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.activities.all })
    },
  })
}

export function useDeleteActivity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteActivity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.activities.all })
    },
  })
}

export function useCompleteActivity() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: completeActivity,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.activities.all })
    },
  })
}
