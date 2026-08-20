/** CRM permission keys aligned with backend catalog (see CRM/wiki/guides/crm-permissions.md). */

export type CRMRole = 'ADMIN' | 'MANAGER' | 'SALES' | 'TECH'

export const CrmPermissions = {
  contacts: {
    create: 'crm.contacts.create',
    read: 'crm.contacts.read',
    update: 'crm.contacts.update',
    delete: 'crm.contacts.delete',
  },
  leads: {
    create: 'crm.leads.create',
    read: 'crm.leads.read',
    update: 'crm.leads.update',
    delete: 'crm.leads.delete',
    assign: 'crm.leads.assign',
    stageUpdate: 'crm.leads.stage.update',
    close: 'crm.leads.close',
    documents: {
      create: 'crm.leads.documents.create',
      read: 'crm.leads.documents.read',
      delete: 'crm.leads.documents.delete',
    },
    electricityBills: {
      create: 'crm.leads.electricity_bills.create',
      read: 'crm.leads.electricity_bills.read',
      delete: 'crm.leads.electricity_bills.delete',
    },
    interactions: {
      create: 'crm.leads.interactions.create',
      read: 'crm.leads.interactions.read',
      update: 'crm.leads.interactions.update',
      delete: 'crm.leads.interactions.delete',
    },
  },
  proposals: {
    create: 'crm.proposals.create',
    read: 'crm.proposals.read',
    update: 'crm.proposals.update',
    delete: 'crm.proposals.delete',
    assignTech: 'crm.proposals.assign_tech',
    stageUpdate: 'crm.proposals.stage.update',
    markWon: 'crm.proposals.mark_won',
    markLost: 'crm.proposals.mark_lost',
    price: {
      set: 'crm.proposals.price.set',
      update: 'crm.proposals.price.update',
    },
    commercialDocuments: {
      create: 'crm.proposals.commercial_documents.create',
      read: 'crm.proposals.commercial_documents.read',
      delete: 'crm.proposals.commercial_documents.delete',
    },
    documents: {
      create: 'crm.proposals.documents.create',
      read: 'crm.proposals.documents.read',
      delete: 'crm.proposals.documents.delete',
    },
    technicalVisits: {
      link: 'crm.proposals.technical_visits.link',
      read: 'crm.proposals.technical_visits.read',
      unlink: 'crm.proposals.technical_visits.unlink',
    },
  },
  technicalVisits: {
    create: 'crm.technical_visits.create',
    read: 'crm.technical_visits.read',
    update: 'crm.technical_visits.update',
    assign: 'crm.technical_visits.assign',
    complete: 'crm.technical_visits.complete',
    cancel: 'crm.technical_visits.cancel',
    attachments: {
      create: 'crm.technical_visits.attachments.create',
      read: 'crm.technical_visits.attachments.read',
      delete: 'crm.technical_visits.attachments.delete',
    },
  },
  activities: {
    create: 'crm.activities.create',
    read: 'crm.activities.read',
    update: 'crm.activities.update',
    delete: 'crm.activities.delete',
  },
  pipeline: {
    read: 'crm.pipeline.read',
  },
  permissions: {
    read: 'crm.permissions.read',
    manage: 'crm.permissions.manage',
    assignRole: 'crm.roles.assign',
  },
  agent: {
    chat: 'crm.agent.chat',
  },
} as const

/** IAM permission keys (IAM service, not CRM). */
export const IamPermissions = {
  users: {
    create: 'iam.users.create',
    read: 'iam.users.read',
    update: 'iam.users.update',
    deactivate: 'iam.users.deactivate',
    delete: 'iam.users.delete',
  },
  permissions: {
    read: 'iam.permissions.read',
    manage: 'iam.permissions.manage',
  },
  services: {
    read: 'iam.services.read',
    manage: 'iam.services.manage',
  },
} as const

/** Nav item → minimum permission to show (any one of listed). */
export const NavPermissionRequirements: Record<string, string | string[]> = {
  dashboard: [],
  pipeline: CrmPermissions.pipeline.read,
  leads: CrmPermissions.leads.read,
  proposals: CrmPermissions.proposals.read,
  calendar: CrmPermissions.activities.read,
  activities: CrmPermissions.activities.read,
  'technical-visits': CrmPermissions.technicalVisits.read,
  agent: CrmPermissions.agent.chat,
  companies: CrmPermissions.contacts.read,
  contacts: CrmPermissions.contacts.read,
}

export function roleDefaultPath(role: CRMRole | null): string {
  switch (role) {
    case 'TECH':
      return '/proposals'
    case 'SALES':
      return '/pipeline'
    case 'ADMIN':
    case 'MANAGER':
    default:
      return '/dashboard'
  }
}

export function canAny(perms: Set<string>, required: string | string[] | undefined): boolean {
  if (required === undefined || (Array.isArray(required) && required.length === 0)) {
    return true
  }
  const keys = Array.isArray(required) ? required : [required]
  return keys.some((k) => perms.has(k))
}

/** @deprecated Use CrmPermissions / IamPermissions */
export const Permissions = {
  contacts: {
    view: CrmPermissions.contacts.read,
    create: CrmPermissions.contacts.create,
    edit: CrmPermissions.contacts.update,
    delete: CrmPermissions.contacts.delete,
  },
  leads: {
    view: CrmPermissions.leads.read,
    create: CrmPermissions.leads.create,
    edit: CrmPermissions.leads.update,
    delete: CrmPermissions.leads.delete,
  },
  admin: {
    users: {
      view: IamPermissions.users.read,
      create: IamPermissions.users.create,
      edit: IamPermissions.users.update,
      delete: IamPermissions.users.delete,
      role: CrmPermissions.permissions.assignRole,
    },
  },
} as const
