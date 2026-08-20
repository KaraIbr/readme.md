import { useQuery } from '@tanstack/react-query'
import { queryKeys } from '@lib/query-keys'
import { getCompanies, getCompany, getCompanyPeople } from '../services/company.service'

export function useCompanies() {
  return useQuery({
    queryKey: queryKeys.companies.list(),
    queryFn: getCompanies,
  })
}

export function useCompany(id: number) {
  return useQuery({
    queryKey: queryKeys.companies.detail(id),
    queryFn: () => getCompany(id),
    enabled: !!id,
  })
}

export function useCompanyPeople(companyId: number) {
  return useQuery({
    queryKey: queryKeys.companies.people(companyId),
    queryFn: () => getCompanyPeople(companyId),
    enabled: !!companyId,
  })
}
