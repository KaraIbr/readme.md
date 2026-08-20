import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { createUser } from '../services/admin.service'

export function useCreateUser() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.users.all })
    },
  })
}
