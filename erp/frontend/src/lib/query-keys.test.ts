import { describe, it, expect } from 'vitest'
import { queryKeys } from './query-keys'

describe('queryKeys', () => {
  it('builds auth keys', () => {
    expect(queryKeys.auth.me).toEqual(['auth', 'me'])
  })

  it('builds permission keys', () => {
    expect(queryKeys.permissions.catalog).toEqual(['permissions', 'catalog'])
    expect(queryKeys.permissions.user(5)).toEqual(['permissions', 'user', 5])
    expect(queryKeys.permissions.currentUser).toEqual(['permissions', 'me'])
  })

  it('builds contact keys', () => {
    expect(queryKeys.contacts.all).toEqual(['contacts'])
    expect(queryKeys.contacts.list({ q: 'acme' })).toEqual(['contacts', 'list', { q: 'acme' }])
    expect(queryKeys.contacts.detail(1)).toEqual(['contacts', 'detail', 1])
    expect(queryKeys.contacts.promoters.all).toEqual(['promoters'])
    expect(queryKeys.contacts.promoters.list()).toEqual(['promoters', 'list', undefined])
    expect(queryKeys.contacts.companyPeople(1)).toEqual(['contacts', 'people', 1])
  })

  it('builds lead keys', () => {
    expect(queryKeys.leads.all).toEqual(['leads'])
    expect(queryKeys.leads.list({ stage: 'NEW' })).toEqual(['leads', 'list', { stage: 'NEW' }])
    expect(queryKeys.leads.detail(1)).toEqual(['leads', 'detail', 1])
    expect(queryKeys.leads.documents(1)).toEqual(['leads', 'documents', 1])
    expect(queryKeys.leads.electricityBills(1)).toEqual(['leads', 'electricity-bills', 1])
    expect(queryKeys.leads.interactions(1)).toEqual(['leads', 'interactions', 1])
  })

  it('builds opportunity keys', () => {
    expect(queryKeys.opportunities.all).toEqual(['opportunities'])
    expect(queryKeys.opportunities.list()).toEqual(['opportunities', 'list', undefined])
    expect(queryKeys.opportunities.detail(1)).toEqual(['opportunities', 'detail', 1])
  })

  it('builds proposal keys', () => {
    expect(queryKeys.proposals.all).toEqual(['proposals'])
    expect(queryKeys.proposals.list()).toEqual(['proposals', 'list', undefined])
    expect(queryKeys.proposals.detail(1)).toEqual(['proposals', 'detail', 1])
    expect(queryKeys.proposals.documents(1)).toEqual(['proposals', 'documents', 1])
    expect(queryKeys.proposals.commercialPdf(1)).toEqual(['proposals', 'commercial-pdf', 1])
  })

  it('builds technical visit keys', () => {
    expect(queryKeys.technicalVisits.all).toEqual(['technical-visits'])
    expect(queryKeys.technicalVisits.list()).toEqual(['technical-visits', 'list', undefined])
    expect(queryKeys.technicalVisits.detail(1)).toEqual(['technical-visits', 'detail', 1])
    expect(queryKeys.technicalVisits.leadVisits(1)).toEqual(['technical-visits', 'lead', 1])
    expect(queryKeys.technicalVisits.attachments(1)).toEqual(['technical-visits', 'attachments', 1])
  })

  it('builds pipeline keys', () => {
    expect(queryKeys.pipeline.transitions()).toEqual(['pipeline', 'transitions', undefined])
    expect(queryKeys.pipeline.summary('lead', 1)).toEqual(['pipeline', 'summary', 'lead', 1])
  })

  it('builds agent, dashboard and activity keys', () => {
    expect(queryKeys.agent.chat).toEqual(['agent', 'chat'])
    expect(queryKeys.dashboard.stats).toEqual(['dashboard', 'stats'])
    expect(queryKeys.activities.all).toEqual(['activities'])
    expect(queryKeys.activities.list()).toEqual(['activities', 'list', undefined])
    expect(queryKeys.activities.detail(1)).toEqual(['activities', 'detail', 1])
  })

  it('builds company keys', () => {
    expect(queryKeys.companies.all).toEqual(['companies'])
    expect(queryKeys.companies.list()).toEqual(['companies', 'list', undefined])
    expect(queryKeys.companies.detail(1)).toEqual(['companies', 'detail', 1])
    expect(queryKeys.companies.people(1)).toEqual(['companies', 'people', 1])
  })

  it('builds task and admin keys', () => {
    expect(queryKeys.tasks.all).toEqual(['tasks'])
    expect(queryKeys.tasks.list()).toEqual(['tasks', 'list', undefined])
    expect(queryKeys.tasks.detail(1)).toEqual(['tasks', 'detail', 1])
    expect(queryKeys.admin.users.all).toEqual(['admin', 'users'])
    expect(queryKeys.admin.users.list()).toEqual(['admin', 'users', 'list', undefined])
    expect(queryKeys.admin.users.detail(1)).toEqual(['admin', 'users', 'detail', 1])
  })
})
