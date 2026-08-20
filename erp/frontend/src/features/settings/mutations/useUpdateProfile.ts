import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { updateProfile } from '../services/settings.service'
import type { ProfileUpdate } from '../types'

export function useUpdateProfile(id: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: ProfileUpdate) => updateProfile(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.auth.me })
    },
  })
}
