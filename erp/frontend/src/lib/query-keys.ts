export const queryKeys = {
  auth: {
    me: ['auth', 'me'] as const,
  },
  permissions: {
    catalog: ['permissions', 'catalog'] as const,
    user: (userId: number) => ['permissions', 'user', userId] as const,
    currentUser: ['permissions', 'me'] as const,
  },
  contacts: {
    all: ['contacts'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.contacts.all, 'list', filters] as const,
    detail: (id: number) => [...queryKeys.contacts.all, 'detail', id] as const,
    promoters: {
      all: ['promoters'] as const,
      list: (filters?: Record<string, unknown>) => [...queryKeys.contacts.promoters.all, 'list', filters] as const,
    },
    companyPeople: (companyId: number) => [...queryKeys.contacts.all, 'people', companyId] as const,
  },
  leads: {
    all: ['leads'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.leads.all, 'list', filters] as const,
    detail: (id: number) => [...queryKeys.leads.all, 'detail', id] as const,
    documents: (leadId: number) => [...queryKeys.leads.all, 'documents', leadId] as const,
    electricityBills: (leadId: number) => [...queryKeys.leads.all, 'electricity-bills', leadId] as const,
    interactions: (leadId: number) => [...queryKeys.leads.all, 'interactions', leadId] as const,
  },
  opportunities: {
    all: ['opportunities'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.opportunities.all, 'list', filters] as const,
    detail: (id: number) => [...queryKeys.opportunities.all, 'detail', id] as const,
  },
  proposals: {
    all: ['proposals'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.proposals.all, 'list', filters] as const,
    detail: (id: number) => [...queryKeys.proposals.all, 'detail', id] as const,
    documents: (proposalId: number) => [...queryKeys.proposals.all, 'documents', proposalId] as const,
    commercialPdf: (proposalId: number) => [...queryKeys.proposals.all, 'commercial-pdf', proposalId] as const,
  },
  technicalVisits: {
    all: ['technical-visits'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.technicalVisits.all, 'list', filters] as const,
    detail: (id: number) => [...queryKeys.technicalVisits.all, 'detail', id] as const,
    leadVisits: (leadId: number) => [...queryKeys.technicalVisits.all, 'lead', leadId] as const,
    attachments: (visitId: number) => [...queryKeys.technicalVisits.all, 'attachments', visitId] as const,
  },
  pipeline: {
    transitions: (filters?: Record<string, unknown>) => ['pipeline', 'transitions', filters] as const,
    summary: (entityType: string, entityId: number) => ['pipeline', 'summary', entityType, entityId] as const,
  },
  agent: {
    chat: ['agent', 'chat'] as const,
  },
  dashboard: {
    stats: ['dashboard', 'stats'] as const,
  },
  activities: {
    all: ['activities'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.activities.all, 'list', filters] as const,
    detail: (id: number) => [...queryKeys.activities.all, 'detail', id] as const,
  },
  companies: {
    all: ['companies'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.companies.all, 'list', filters] as const,
    detail: (id: number) => [...queryKeys.companies.all, 'detail', id] as const,
    people: (companyId: number) => [...queryKeys.companies.all, 'people', companyId] as const,
  },
  tasks: {
    all: ['tasks'] as const,
    list: (filters?: Record<string, unknown>) => [...queryKeys.tasks.all, 'list', filters] as const,
    detail: (id: number) => [...queryKeys.tasks.all, 'detail', id] as const,
  },
  admin: {
    users: { all: ['admin', 'users'] as const, list: (filters?: Record<string, unknown>) => [...queryKeys.admin.users.all, 'list', filters] as const, detail: (id: number) => [...queryKeys.admin.users.all, 'detail', id] as const },
  },
} as const
