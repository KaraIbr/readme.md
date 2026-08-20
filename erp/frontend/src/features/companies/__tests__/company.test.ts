import { describe, it, expect } from 'vitest'
import { companyCreateSchema, companyDetailSchema } from '../schemas/company.schema'
import { api } from '../../../test/mocks/api-client'
import {
  getCompanies,
  getCompany,
  createCompany,
  updateCompany,
  deleteCompany,
  getCompanyPeople,
  createCompanyPerson,
  updateCompanyPerson,
  deleteCompanyPerson,
} from '../services/company.service'

describe('company schemas', () => {
  it('accepts a valid create payload', () => {
    const result = companyCreateSchema.safeParse({
      name: 'Acme Solar',
      promoter_id: 1,
      people: [{ name: 'Jane', phone: '555-0100', position: 'CEO' }],
    })
    expect(result.success).toBe(true)
  })

  it('rejects empty name', () => {
    expect(
      companyCreateSchema.safeParse({
        name: '',
        people: [{ name: 'Jane', phone: '555', position: 'CEO' }],
      }).success,
    ).toBe(false)
  })

  it('requires at least one person', () => {
    expect(companyCreateSchema.safeParse({ name: 'Acme', people: [] }).success).toBe(false)
  })

  it('rejects a person missing position', () => {
    expect(
      companyCreateSchema.safeParse({
        name: 'Acme',
        people: [{ name: 'Jane', phone: '555' }],
      }).success,
    ).toBe(false)
  })

  it('accepts an empty email string for a person', () => {
    const result = companyCreateSchema.safeParse({
      name: 'Acme',
      people: [{ name: 'Jane', phone: '555', email: '', position: 'CEO' }],
    })
    expect(result.success).toBe(true)
  })

  it('coerces empty promoter_id to undefined', () => {
    const result = companyCreateSchema.safeParse({
      name: 'Acme',
      promoter_id: '',
      people: [{ name: 'Jane', phone: '555', position: 'CEO' }],
    })
    expect(result.success).toBe(true)
    if (result.success) {
      expect(result.data.promoter_id).toBeUndefined()
    }
  })

  it('detail schema does not require people', () => {
    const result = companyDetailSchema.safeParse({ name: 'Acme' })
    expect(result.success).toBe(true)
  })
})

describe('company api service', () => {
  it('lists companies', async () => {
    const companies = [{ id: 1, name: 'Acme' }]
    api.get.mockResolvedValue({ data: companies })

    const result = await getCompanies()

    expect(api.get).toHaveBeenCalledWith('/companies/')
    expect(result).toEqual(companies)
  })

  it('fetches a single company', async () => {
    const company = { id: 1, name: 'Acme' }
    api.get.mockResolvedValue({ data: company })

    const result = await getCompany(1)

    expect(api.get).toHaveBeenCalledWith('/companies/1')
    expect(result).toEqual(company)
  })

  it('creates a company remapping people to company_people', async () => {
    const body = {
      name: 'Acme',
      people: [{ name: 'Jane', phone: '555', position: 'CEO' }],
    }
    const expected = {
      name: 'Acme',
      company_people: [{ name: 'Jane', phone: '555', position: 'CEO' }],
    }
    api.post.mockResolvedValue({ data: { id: 2, ...expected } })

    const result = await createCompany(body)

    expect(api.post).toHaveBeenCalledWith('/companies/', expected)
    expect(result.id).toBe(2)
  })

  it('updates a company', async () => {
    const body = { name: 'Acme 2' }
    api.patch.mockResolvedValue({ data: { id: 1, ...body } })

    await updateCompany(1, body)

    expect(api.patch).toHaveBeenCalledWith('/companies/1', body)
  })

  it('deletes a company', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteCompany(1)

    expect(api.delete).toHaveBeenCalledWith('/companies/1')
  })

  it('lists people of a company', async () => {
    const people = [{ id: 1, name: 'Jane' }]
    api.get.mockResolvedValue({ data: people })

    const result = await getCompanyPeople(1)

    expect(api.get).toHaveBeenCalledWith('/contacts/1/people')
    expect(result).toEqual(people)
  })

  it('creates a company person', async () => {
    const body = { name: 'John', phone: '555', position: 'CTO' }
    api.post.mockResolvedValue({ data: { id: 2, ...body } })

    await createCompanyPerson(1, body)

    expect(api.post).toHaveBeenCalledWith('/contacts/1/people', body)
  })

  it('updates a company person', async () => {
    const body = { position: 'CFO' }
    api.patch.mockResolvedValue({ data: { id: 2, ...body } })

    await updateCompanyPerson(1, 2, body)

    expect(api.patch).toHaveBeenCalledWith('/contacts/1/people/2', body)
  })

  it('deletes a company person', async () => {
    api.delete.mockResolvedValue({ data: null })

    await deleteCompanyPerson(1, 2)

    expect(api.delete).toHaveBeenCalledWith('/contacts/1/people/2')
  })
})
