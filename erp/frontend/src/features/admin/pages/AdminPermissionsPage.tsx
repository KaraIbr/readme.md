import { useState, useMemo } from 'react'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Badge } from '@atoms/Badge/Badge'
import { Spinner } from '@atoms/Spinner/Spinner'
import { usePermissionCatalog } from '@features/permissions/queries/useUserPermissions'

const ROLE_DESCRIPTIONS: Record<string, string> = {
  ADMIN: 'Full access to all CRM features and permissions management',
  MANAGER: 'Full access except price field management',
  SALES: 'Contact and lead management, read-only proposals and pipeline',
  TECH: 'Technical operations: proposals, visits, pipeline',
}

const ROLE_COLORS: Record<string, 'info' | 'success' | 'warning' | 'default'> = {
  ADMIN: 'info',
  MANAGER: 'success',
  SALES: 'warning',
  TECH: 'default',
}

function groupPermissions(entries: { key: string; description: string }[]) {
  const groups: Record<string, { key: string; description: string }[]> = {}
  for (const entry of entries) {
    const domain = entry.key.split('.').slice(0, 2).join('.')
    if (!groups[domain]) groups[domain] = []
    groups[domain].push(entry)
  }
  return groups
}

const DOMAIN_LABELS: Record<string, string> = {
  'crm.permissions': 'Permissions',
  'crm.roles': 'Roles',
  'crm.contacts': 'Contacts',
  'crm.leads': 'Leads',
  'crm.proposals': 'Proposals',
  'crm.technical_visits': 'Technical Visits',
  'crm.pipeline': 'Pipeline',
  'crm.agent': 'Agent',
}

function PermissionCatalogSection({ entries }: { entries: { key: string; description: string }[] }) {
  const groups = useMemo(() => groupPermissions(entries), [entries])

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-semibold text-text">Permission Catalog</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {Object.entries(groups).map(([domain, perms]) => (
          <div key={domain} className="bg-white rounded-lg border border-border p-4">
            <p className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-2">
              {DOMAIN_LABELS[domain] ?? domain}
            </p>
            <ul className="space-y-1.5">
              {perms.map((p) => (
                <li key={p.key} className="flex items-start gap-2">
                  <span className="text-xs font-mono text-primary shrink-0 mt-0.5">{p.key}</span>
                  <span className="text-xs text-text-tertiary">{p.description}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  )
}

function RoleCard({ role }: { role: string }) {
  const { data: catalog } = usePermissionCatalog()
  const [expanded, setExpanded] = useState(false)

  const rolePermissions = useMemo(() => {
    if (!catalog) return []
    if (role === 'ADMIN' || role === 'MANAGER') return catalog
    if (role === 'SALES') {
      return catalog.filter(
        (p) =>
          p.key.startsWith('crm.contacts.') ||
          p.key.startsWith('crm.leads.') ||
          p.key === 'crm.proposals.read' ||
          p.key === 'crm.proposals.commercial_documents.read' ||
          p.key === 'crm.proposals.documents.read' ||
          p.key === 'crm.proposals.technical_visits.read' ||
          p.key === 'crm.technical_visits.read' ||
          p.key === 'crm.technical_visits.attachments.read' ||
          p.key === 'crm.pipeline.read' ||
          p.key === 'crm.agent.chat',
      ).filter((p) => p.key !== 'crm.proposals.price.set' && p.key !== 'crm.proposals.price.update')
    }
    if (role === 'TECH') {
      const denied = new Set([
        'crm.permissions.manage', 'crm.roles.assign',
        'crm.contacts.create', 'crm.contacts.update', 'crm.contacts.delete',
        'crm.leads.create', 'crm.leads.update', 'crm.leads.delete',
        'crm.leads.assign', 'crm.leads.stage.update', 'crm.leads.close',
        'crm.leads.documents.create', 'crm.leads.documents.delete',
        'crm.leads.electricity_bills.create', 'crm.leads.electricity_bills.delete',
        'crm.leads.interactions.create', 'crm.leads.interactions.read',
        'crm.leads.interactions.update', 'crm.leads.interactions.delete',
        'crm.proposals.price.set', 'crm.proposals.price.update',
      ])
      return catalog.filter((p) => !denied.has(p.key))
    }
    return []
  }, [catalog, role])

  return (
    <div className="bg-white rounded-xl border border-border overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-5 hover:bg-neutral-50 transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <Badge variant={ROLE_COLORS[role] ?? 'default'} size="md">{role}</Badge>
          <p className="text-sm text-text-secondary">{ROLE_DESCRIPTIONS[role]}</p>
        </div>
        <svg
          className={`size-4 text-text-tertiary transition-transform ${expanded ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {expanded && (
        <div className="border-t border-border px-5 py-4">
          <p className="text-xs font-semibold text-text-secondary mb-2">Permissions ({rolePermissions.length})</p>
          <div className="flex flex-wrap gap-1.5">
            {rolePermissions.length === 0 ? (
              <p className="text-xs text-text-tertiary">No permissions for this role</p>
            ) : (
              rolePermissions.map((p) => (
                <span key={p.key} className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-neutral-100 text-xs text-text-secondary">
                  {p.key}
                </span>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export function Component() {
  const { data: catalog, isLoading: catalogLoading } = usePermissionCatalog()
  const [activeSection, setActiveSection] = useState<'roles' | 'catalog'>('roles')

  return (
    <div>
      <PageHeader
        title="Admin"
        description="Manage roles and permissions"
      />
      <div className="px-6 pb-6 space-y-6">
        <div className="flex gap-0 border-b border-border">
          <button
            onClick={() => setActiveSection('roles')}
            className={`px-4 py-2.5 text-sm font-medium transition-colors relative ${
              activeSection === 'roles'
                ? 'text-primary'
                : 'text-text-secondary hover:text-text'
            }`}
          >
            Role Templates
            {activeSection === 'roles' && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
            )}
          </button>
          <button
            onClick={() => setActiveSection('catalog')}
            className={`px-4 py-2.5 text-sm font-medium transition-colors relative ${
              activeSection === 'catalog'
                ? 'text-primary'
                : 'text-text-secondary hover:text-text'
            }`}
          >
            Permission Catalog
            {activeSection === 'catalog' && (
              <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary rounded-full" />
            )}
          </button>
        </div>

        {activeSection === 'roles' && (
          <div className="space-y-3">
            {Object.keys(ROLE_DESCRIPTIONS).map((role) => (
              <RoleCard key={role} role={role} />
            ))}
          </div>
        )}

        {activeSection === 'catalog' && (
          <>
            {catalogLoading ? (
              <div className="flex items-center justify-center py-16">
                <Spinner size="lg" />
              </div>
            ) : catalog ? (
              <PermissionCatalogSection entries={catalog} />
            ) : (
              <p className="text-sm text-text-tertiary text-center py-8">No permissions data available</p>
            )}
          </>
        )}
      </div>
    </div>
  )
}

Component.displayName = 'AdminPermissionsPage'
