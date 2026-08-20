import { lazy } from 'react'

export const LoginPage = lazy(() => import('../../features/auth/pages/LoginPage').then(m => ({ default: m.Component })))
export const DashboardPage = lazy(() => import('../../features/dashboard/pages/DashboardPage').then(m => ({ default: m.Component })))

export const ContactListPage = lazy(() => import('../../features/contacts/pages/ContactListPage').then(m => ({ default: m.Component })))
export const ContactDetailPage = lazy(() => import('../../features/contacts/pages/ContactDetailPage').then(m => ({ default: m.Component })))
export const ContactCreatePage = lazy(() => import('../../features/contacts/pages/ContactCreatePage').then(m => ({ default: m.Component })))

export const LeadListPage = lazy(() => import('../../features/leads/pages/LeadListPage').then(m => ({ default: m.Component })))
export const LeadDetailPage = lazy(() => import('../../features/leads/pages/LeadDetailPage').then(m => ({ default: m.Component })))
export const LeadCreatePage = lazy(() => import('../../features/leads/pages/LeadCreatePage').then(m => ({ default: m.Component })))

export const ProposalListPage = lazy(() => import('../../features/proposals/pages/ProposalListPage').then(m => ({ default: m.Component })))
export const ProposalDetailPage = lazy(() => import('../../features/proposals/pages/ProposalDetailPage').then(m => ({ default: m.Component })))
export const ProposalCreatePage = lazy(() => import('../../features/proposals/pages/ProposalCreatePage').then(m => ({ default: m.Component })))

export const VisitListPage = lazy(() => import('../../features/technical-visits/pages/VisitListPage').then(m => ({ default: m.Component })))
export const VisitDetailPage = lazy(() => import('../../features/technical-visits/pages/VisitDetailPage').then(m => ({ default: m.Component })))
export const VisitCreatePage = lazy(() => import('../../features/technical-visits/pages/VisitCreatePage').then(m => ({ default: m.Component })))

export const CalendarPage = lazy(() => import('../../features/calendar/pages/CalendarPage').then(m => ({ default: m.Component })))
export const PipelinePage = lazy(() => import('../../features/pipeline/pages/PipelinePage').then(m => ({ default: m.Component })))
export const AgentPage = lazy(() => import('../../features/agent/pages/AgentPage').then(m => ({ default: m.Component })))

export const ActivityListPage = lazy(() => import('../../features/activities/pages/ActivityListPage').then(m => ({ default: m.Component })))
export const ActivityDetailPage = lazy(() => import('../../features/activities/pages/ActivityDetailPage').then(m => ({ default: m.Component })))

export const TaskListPage = lazy(() => import('../../features/tasks/pages/TaskListPage').then(m => ({ default: m.Component })))
export const TaskDetailPage = lazy(() => import('../../features/tasks/pages/TaskDetailPage').then(m => ({ default: m.Component })))

export const CompanyListPage = lazy(() => import('../../features/companies/pages/CompanyListPage').then(m => ({ default: m.Component })))
export const CompanyDetailPage = lazy(() => import('../../features/companies/pages/CompanyDetailPage').then(m => ({ default: m.Component })))
export const CompanyEditPage = lazy(() => import('../../features/companies/pages/CompanyEditPage').then(m => ({ default: m.Component })))

export const OpportunityListPage = lazy(() => import('../../features/opportunities/pages/OpportunityListPage').then(m => ({ default: m.Component })))
export const OpportunityCreatePage = lazy(() => import('../../features/opportunities/pages/OpportunityCreatePage').then(m => ({ default: m.Component })))
export const OpportunityDetailPage = lazy(() => import('../../features/opportunities/pages/OpportunityDetailPage').then(m => ({ default: m.Component })))

export const AdminPage = lazy(() => import('../../features/admin/pages/AdminPage').then(m => ({ default: m.Component })))
export const AdminUsersPage = lazy(() => import('../../features/admin/pages/AdminUsersPage').then(m => ({ default: m.Component })))
export const AdminAuditPage = lazy(() => import('../../features/admin/pages/AdminAuditPage').then(m => ({ default: m.Component })))
export const AdminSettingsPage = lazy(() => import('../../features/settings/pages/SettingsPage').then(m => ({ default: m.Component })))
export const AdminPermissionsPage = lazy(() => import('../../features/admin/pages/AdminPermissionsPage').then(m => ({ default: m.Component })))
