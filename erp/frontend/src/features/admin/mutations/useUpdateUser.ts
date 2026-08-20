import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { updateUser } from '../services/admin.service'
import type { AdminUserUpdate } from '../types'

export function useUpdateUser(id: number) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (body: AdminUserUpdate) => updateUser(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.users.detail(id) })
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.users.all })
    },
  })
}
