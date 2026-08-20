import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook } from '@testing-library/react'
import {
  useCreateCompany,
  useUpdateCompany,
  useDeleteCompany,
  useCreateCompanyPerson,
  useUpdateCompanyPerson,
  useDeleteCompanyPerson,
} from '../mutations/useCompanyMutations'
import {
  createCompany,
  updateCompany,
  deleteCompany,
  createCompanyPerson,
  updateCompanyPerson,
  deleteCompanyPerson,
} from '../services/company.service'
import { createQueryWrapper } from '../../../test/query-utils'

vi.mock('../services/company.service', () => ({
  createCompany: vi.fn(),
  updateCompany: vi.fn(),
  deleteCompany: vi.fn(),
  createCompanyPerson: vi.fn(),
  updateCompanyPerson: vi.fn(),
  deleteCompanyPerson: vi.fn(),
}))

const mockedCreateCompany = vi.mocked(createCompany)
const mockedUpdateCompany = vi.mocked(updateCompany)
const mockedDeleteCompany = vi.mocked(deleteCompany)
const mockedCreateCompanyPerson = vi.mocked(createCompanyPerson)
const mockedUpdateCompanyPerson = vi.mocked(updateCompanyPerson)
const mockedDeleteCompanyPerson = vi.mocked(deleteCompanyPerson)

describe('company mutation hooks', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates a company', async () => {
    mockedCreateCompany.mockResolvedValue({ id: 1 } as never)
    const body = { name: 'Acme', people: [{ name: 'Jane', phone: '555', position: 'CEO' }] }
    const { result } = renderHook(() => useCreateCompany(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(body)

    expect(mockedCreateCompany).toHaveBeenCalledWith(body, expect.anything())
  })

  it('updates a company', async () => {
    mockedUpdateCompany.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateCompany(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 1, data: { name: 'Acme 2' } })

    expect(mockedUpdateCompany).toHaveBeenCalledWith(1, { name: 'Acme 2' })
  })

  it('deletes a company', async () => {
    mockedDeleteCompany.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteCompany(), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(1)

    expect(mockedDeleteCompany).toHaveBeenCalledWith(1, expect.anything())
  })

  it('creates a company person', async () => {
    mockedCreateCompanyPerson.mockResolvedValue({ id: 1 } as never)
    const body = { name: 'John', phone: '555', position: 'CTO' }
    const { result } = renderHook(() => useCreateCompanyPerson(1), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(body)

    expect(mockedCreateCompanyPerson).toHaveBeenCalledWith(1, body)
  })

  it('updates a company person', async () => {
    mockedUpdateCompanyPerson.mockResolvedValue({ id: 1 } as never)
    const { result } = renderHook(() => useUpdateCompanyPerson(1), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync({ id: 2, data: { position: 'CFO' } })

    expect(mockedUpdateCompanyPerson).toHaveBeenCalledWith(1, 2, { position: 'CFO' })
  })

  it('deletes a company person', async () => {
    mockedDeleteCompanyPerson.mockResolvedValue(undefined)
    const { result } = renderHook(() => useDeleteCompanyPerson(1), { wrapper: createQueryWrapper() })

    await result.current.mutateAsync(2)

    expect(mockedDeleteCompanyPerson).toHaveBeenCalledWith(1, 2)
  })
})
