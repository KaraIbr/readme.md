import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { deleteUser } from '../services/admin.service'

export function useDeleteUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.users.all })
    },
  })
}
