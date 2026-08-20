import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { getUsers, getUser } from '../services/admin.service'

export function useUsers() {
  return useQuery({
    queryKey: queryKeys.admin.users.list(),
    queryFn: getUsers,
  })
}

export function useUser(id: number) {
  return useQuery({
    queryKey: queryKeys.admin.users.detail(id),
    queryFn: () => getUser(id),
    enabled: !!id,
  })
}
