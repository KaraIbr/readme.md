import { api } from '@services/api-client'
import type { CompanyRead, CompanyCreate, CompanyUpdate, CompanyPerson, CompanyPersonCreate, CompanyPersonUpdate } from '../types'

export async function getCompanies(): Promise<CompanyRead[]> {
  const { data } = await api.get<CompanyRead[]>('/companies/')
  return data
}

export async function getCompany(id: number): Promise<CompanyRead> {
  const { data } = await api.get(`/companies/${id}`)
  return data
}

export async function createCompany(body: CompanyCreate): Promise<CompanyRead> {
  const { people, ...rest } = body
  const { data } = await api.post('/companies/', { ...rest, company_people: people })
  return data
}

export async function updateCompany(id: number, body: CompanyUpdate): Promise<CompanyRead> {
  const { data } = await api.patch(`/companies/${id}`, body)
  return data
}

export async function deleteCompany(id: number): Promise<void> {
  await api.delete(`/companies/${id}`)
}

export async function getCompanyPeople(companyId: number): Promise<CompanyPerson[]> {
  const { data } = await api.get(`/contacts/${companyId}/people`)
  return data
}

export async function createCompanyPerson(companyId: number, body: CompanyPersonCreate): Promise<CompanyPerson> {
  const { data } = await api.post(`/contacts/${companyId}/people`, body)
  return data
}

export async function updateCompanyPerson(companyId: number, id: number, body: CompanyPersonUpdate): Promise<CompanyPerson> {
  const { data } = await api.patch(`/contacts/${companyId}/people/${id}`, body)
  return data
}

export async function deleteCompanyPerson(companyId: number, id: number): Promise<void> {
  await api.delete(`/contacts/${companyId}/people/${id}`)
}
