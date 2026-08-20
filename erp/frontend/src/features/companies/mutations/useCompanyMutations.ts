import { useMutation, useQueryClient } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { createCompany, updateCompany, deleteCompany, createCompanyPerson, updateCompanyPerson, deleteCompanyPerson } from '../services/company.service'

export function useCreateCompany() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createCompany,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies.all })
    },
  })
}

export function useUpdateCompany() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateCompany>[1] }) => updateCompany(id, data),
    onSuccess: (_data, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies.all })
      queryClient.invalidateQueries({ queryKey: queryKeys.companies.detail(variables.id) })
    },
  })
}

export function useDeleteCompany() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteCompany,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies.all })
    },
  })
}

export function useCreateCompanyPerson(companyId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (body: Parameters<typeof createCompanyPerson>[1]) => createCompanyPerson(companyId, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies.people(companyId) })
    },
  })
}

export function useUpdateCompanyPerson(companyId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Parameters<typeof updateCompanyPerson>[2] }) => updateCompanyPerson(companyId, id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies.people(companyId) })
    },
  })
}

export function useDeleteCompanyPerson(companyId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => deleteCompanyPerson(companyId, id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.companies.people(companyId) })
    },
  })
}
