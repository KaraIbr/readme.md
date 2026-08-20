import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useCompanies, useCompany, useCompanyPeople } from '../queries/useCompanies'
import { getCompanies, getCompany, getCompanyPeople } from '../services/company.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/company.service', () => ({
  getCompanies: vi.fn(),
  getCompany: vi.fn(),
  getCompanyPeople: vi.fn(),
}))

const mockedGetCompanies = vi.mocked(getCompanies)
const mockedGetCompany = vi.mocked(getCompany)
const mockedGetCompanyPeople = vi.mocked(getCompanyPeople)

describe('company query hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads the company list', async () => {
    const companies = [{ id: 1, name: 'Acme' }]
    mockedGetCompanies.mockResolvedValue(companies as never)

    const { result } = renderHook(() => useCompanies(), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(companies))
  })

  it('loads a single company', async () => {
    const company = { id: 1, name: 'Acme' }
    mockedGetCompany.mockResolvedValue(company as never)

    const { result } = renderHook(() => useCompany(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(company))
  })

  it('loads company people', async () => {
    const people = [{ id: 1, name: 'Jane' }]
    mockedGetCompanyPeople.mockResolvedValue(people as never)

    const { result } = renderHook(() => useCompanyPeople(1), { wrapper: createQueryWrapper() })

    await waitFor(() => expect(result.current.data).toEqual(people))
  })
})
