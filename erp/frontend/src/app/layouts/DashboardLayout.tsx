import { useState, useCallback, useMemo, useRef, useEffect, type ReactNode } from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Sidebar } from '@organisms/Sidebar/Sidebar'
import type { SidebarItem } from '@organisms/Sidebar/Sidebar'
import { Topbar } from '@organisms/Topbar/Topbar'
import { Avatar } from '@atoms/Avatar/Avatar'
import { env } from '../../lib/env'
import { AuthGuard } from '@features/auth/components/AuthGuard'
import { useAuth } from '@features/auth/hooks/useAuth'
import { useEffectivePermissions } from '@features/permissions/queries/useUserPermissions'
import logo from '@src/assets/logo.png'
import { TopbarFilterContext } from '@lib/TopbarFilterContext'

interface NavItem {
  key: string
  label: string
  path: string
  category: string
}

const generalItems: NavItem[] = [
  { key: 'dashboard', label: 'Dashboard', path: '/dashboard', category: 'GENERAL' },
  { key: 'agent', label: 'Agent', path: '/agent', category: 'GENERAL' },
]

const crmItems: NavItem[] = [
  { key: 'activities', label: 'Activities', path: '/activities', category: 'CRM' },
  { key: 'companies', label: 'Companies', path: '/companies', category: 'CRM' },
  { key: 'contacts', label: 'Contacts', path: '/contacts', category: 'CRM' },
  { key: 'proposals', label: 'Proposals', path: '/proposals', category: 'CRM' },
  { key: 'pipeline', label: 'Pipeline', path: '/pipeline', category: 'CRM' },
  { key: 'leads', label: 'Leads', path: '/leads', category: 'CRM' },
  { key: 'tasks', label: 'Tasks', path: '/tasks', category: 'CRM' },
]

const technicalItems: NavItem[] = [
  { key: 'calendar', label: 'Calendar', path: '/calendar', category: 'TECHNICAL' },
  { key: 'technical-visits', label: 'Visits', path: '/technical-visits', category: 'TECHNICAL' },
]

const allNavItems = [...generalItems, ...crmItems, ...technicalItems]

const breadcrumbLabels: Record<string, { label: string; parent?: string }> = {
  dashboard: { label: 'Dashboard' },
  agent: { label: 'Agent' },
  activities: { label: 'Activities', parent: 'CRM' },
  companies: { label: 'Companies', parent: 'CRM' },
  contacts: { label: 'Contacts', parent: 'CRM' },
  proposals: { label: 'Proposals', parent: 'CRM' },
  pipeline: { label: 'Pipeline', parent: 'CRM' },
  leads: { label: 'Leads', parent: 'CRM' },
  tasks: { label: 'Tasks', parent: 'CRM' },
  opportunities: { label: 'Opportunities', parent: 'CRM' },
  'technical-visits': { label: 'Visits', parent: 'Technical' },
  calendar: { label: 'Calendar', parent: 'Technical' },
  admin: { label: 'Admin' },
  audit: { label: 'Audit Log', parent: 'Admin' },
  settings: { label: 'Settings', parent: 'Admin' },
  permissions: { label: 'Permissions', parent: 'Admin' },
}

function buildBreadcrumbs(pathname: string): { label: string; path?: string }[] {
  const parts = pathname.split('/').filter(Boolean)
  const crumbs: { label: string; path?: string }[] = []

  if (parts[0] === 'admin') {
    crumbs.push({ label: 'Admin', path: '/admin' })
    if (parts[1]) {
      const info = breadcrumbLabels[parts[1]]
      crumbs.push({ label: info?.label ?? parts[1] })
    }
    return crumbs
  }

  if (parts[0] === 'dashboard') {
    return [{ label: 'Dashboard' }]
  }

  for (let i = 0; i < parts.length; i++) {
    const key = parts[i]
    const info = breadcrumbLabels[key]
    if (info?.parent && i === 0) {
      crumbs.push({ label: info.parent })
    }
    if (info) {
      const isLast = i === parts.length - 1
      if (parts.length > 1 && isLast && /^\d+$/.test(parts[i])) {
        crumbs.push({ label: `#${parts[i]}` })
      } else if (!isLast || parts.length === 1) {
        crumbs.push({ label: info.label, path: '/' + parts.slice(0, i + 1).join('/') })
      } else {
        crumbs.push({ label: info.label })
      }
    }
  }
  return crumbs
}

function NavIcon({ type }: { type: string }) {
  if (type === 'dashboard') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="1" y="1" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.5"/><rect x="11" y="1" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.5"/><rect x="1" y="11" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.5"/><rect x="11" y="11" width="8" height="8" rx="2" stroke="currentColor" strokeWidth="1.5"/></svg>
  if (type === 'contacts') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M14 17C14 14.7909 11.3137 13 8 13C4.68629 13 2 14.7909 2 17" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><circle cx="8" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/><path d="M15 5L18 8M18 8L15 11M18 8H11" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
  if (type === 'leads') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 2L12.47 7.04L18 7.91L13.73 11.93L14.94 17.38L10 14.68L5.06 17.38L6.27 11.93L2 7.91L7.53 7.04L10 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
  if (type === 'proposals') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 4C4 2.89543 4.89543 2 6 2H14C15.1046 2 16 2.89543 16 4V18L10 15L4 18V4Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
  if (type === 'technical-visits') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5"/><path d="M10 6V10L13 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
  if (type === 'calendar') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="2" y="3" width="16" height="15" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M2 7H18" stroke="currentColor" strokeWidth="1.5"/><path d="M6 1V5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M14 1V5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
  if (type === 'pipeline') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M2 6H8L10 10L12 6H18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 14H18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><circle cx="5" cy="14" r="2" fill="currentColor"/><circle cx="15" cy="14" r="2" fill="currentColor"/></svg>
  if (type === 'agent') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="5" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M4 18C4 14.6863 6.68629 12 10 12C13.3137 12 16 14.6863 16 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
  if (type === 'activities') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 2L4 11H9L8 18L16 9H11L12 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
  if (type === 'companies') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="3" y="2" width="14" height="16" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M7 6H13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M7 9H13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M7 12H10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
  if (type === 'tasks') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect x="3" y="2" width="14" height="16" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M6 8L8 10L11 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M6 12L8 14L11 10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
  if (type === 'opportunities') return <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 2C12.2 2 14 3.8 14 6C14 8.2 12.2 10 10 10C7.8 10 6 8.2 6 6C6 3.8 7.8 2 10 2Z" stroke="currentColor" strokeWidth="1.5"/><path d="M2 18C2 14.1 5.6 11 10 11C14.4 11 18 14.1 18 18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>
  return null
}

function GearIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3"/>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
    </svg>
  )
}

function HelpIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10"/>
      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  )
}

function DashboardShell() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  const { role } = useEffectivePermissions()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try { return localStorage.getItem('sidebar_collapsed') === 'true' } catch { return false }
  })
  const [showUserMenu, setShowUserMenu] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  const initials = useMemo(() => {
    if (user?.full_name) {
      return user.full_name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
    }
    return (user?.email?.[0] ?? 'U').toUpperCase()
  }, [user])

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setShowUserMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleToggleCollapse = useCallback(() => {
    setSidebarCollapsed((prev) => {
      const next = !prev
      try { localStorage.setItem('sidebar_collapsed', String(next)) } catch { /* ignore */ }
      return next
    })
  }, [])

  const sidebarItems: SidebarItem[] = allNavItems.map((item) => ({
    key: item.key,
    label: item.label,
    icon: <NavIcon type={item.key} />,
    active: item.path === '/dashboard'
      ? location.pathname === '/' || location.pathname === '/dashboard'
      : location.pathname.startsWith(item.path),
    onClick: () => navigate(item.path),
    category: item.category,
  }))

  const bottomSidebarItems: SidebarItem[] = [
    {
      key: 'settings',
      label: 'Settings',
      icon: <GearIcon />,
      active: location.pathname.startsWith('/admin'),
      onClick: () => navigate('/admin'),
    },
    {
      key: 'help',
      label: 'Help & support',
      icon: <HelpIcon />,
      onClick: () => { window.location.href = 'mailto:karinibarra11@gmail.com' },
    },
  ]

  const breadcrumbs = useMemo(() => buildBreadcrumbs(location.pathname), [location.pathname])

  const [topbarFilter, setTopbarFilter] = useState<ReactNode>(null)

  return (
    <div className="flex h-screen overflow-hidden bg-neutral-25">
      <Sidebar
        items={sidebarItems}
        collapsed={sidebarCollapsed}
        onToggleCollapse={handleToggleCollapse}
        collapseAtTop
        categoryOptions={{
          GENERAL: { showLabel: true, showDivider: false },
          CRM: { showLabel: true, showDivider: false },
          TECHNICAL: { showLabel: true, showDivider: false },
        }}
        header={
          <div className="flex items-center gap-3">
            <div className="size-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
              <img src={logo} alt="Company Logo" width="200" />
            </div>
            <div className="min-w-0">
              <div className="text-h6 text-text truncate">VERP</div>
              {role && (
                <div className="text-[10px] font-semibold uppercase tracking-wider text-text-tertiary truncate leading-tight">{role}</div>
              )}
            </div>
          </div>
        }
        bottomItems={bottomSidebarItems}
        footer={`v${env.appVersion}`}
      />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar
          center={topbarFilter}
          left={
            <nav className="flex items-center gap-1.5 text-sm">
              {breadcrumbs.map((crumb, i) => (
                <span key={i} className="flex items-center gap-1.5">
                  {i > 0 && (
                    <svg className="w-3.5 h-3.5 text-text-tertiary" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="9 18 15 12 9 6" />
                    </svg>
                  )}
                  {crumb.path ? (
                    <button
                      type="button"
                      onClick={() => navigate(crumb.path!)}
                      className="text-text-secondary hover:text-text transition-colors text-sm"
                    >
                      {crumb.label}
                    </button>
                  ) : (
                    <span className="text-text font-medium text-sm">{crumb.label}</span>
                  )}
                </span>
              ))}
            </nav>
          }
          right={
            <div className="flex items-center gap-3">
              <button
                type="button"
                className="size-9 flex items-center justify-center rounded-lg text-text-tertiary hover:bg-neutral-100 transition-colors relative"
              >
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M10 2C7.79086 2 6 3.79086 6 6V9.3821C6 9.76081 5.88686 10.1301 5.67539 10.4412L4.55279 12.0729C4.03785 12.8106 4.55796 13.8461 5.44721 13.8461H14.5528C15.442 13.8461 15.9622 12.8106 15.4472 12.0729L14.3246 10.4412C14.1131 10.1301 14 9.76081 14 9.3821V6C14 3.79086 12.2091 2 10 2Z" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                  <path d="M12 14C12 15.1046 11.1046 16 10 16C8.89543 16 8 15.1046 8 14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                <span className="absolute top-2.5 right-2.5 size-1.5 bg-danger rounded-full animate-pulse-dot" />
              </button>
              <div className="relative" ref={menuRef}>
                <button
                  type="button"
                  onClick={() => setShowUserMenu((v) => !v)}
                  className="rounded-lg hover:ring-2 hover:ring-primary/30 transition-all"
                >
                  <Avatar size="sm" initials={initials} />
                </button>
                {showUserMenu && (
                  <div className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl border border-border shadow-lg py-2 z-50 animate-scale-in origin-top-right">
                    <div className="px-4 py-2 border-b border-border">
                      <p className="text-sm font-medium text-text truncate">
                        {user?.full_name || user?.email || 'User'}
                      </p>
                      {user?.full_name && (
                        <p className="text-xs text-text-secondary truncate mt-0.5">{user.email}</p>
                      )}
                    </div>
                    <button
                      type="button"
                      onClick={() => { logout() }}
                      className="w-full flex items-center gap-2.5 px-4 py-2.5 text-sm text-danger hover:bg-danger-soft/20 transition-colors"
                    >
                      <svg width="16" height="16" viewBox="0 0 20 20" fill="none">
                        <path d="M7 17H4C3.44772 17 3 16.5523 3 16V4C3 3.44772 3.44772 3 4 3H7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                        <path d="M13 14L17 10L13 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                        <path d="M17 10H7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
                      </svg>
                      Sign out
                    </button>
                  </div>
                )}
              </div>
            </div>
          }
        />
        <main className="flex-1 overflow-y-auto">
          <TopbarFilterContext.Provider value={[topbarFilter, setTopbarFilter]}>
            <AuthGuard>
              <div className="animate-fade-in">
                <Outlet />
              </div>
            </AuthGuard>
          </TopbarFilterContext.Provider>
        </main>
      </div>
    </div>
  )
}

export function DashboardLayout() {
  return <DashboardShell />
}
