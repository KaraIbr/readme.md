import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Card } from '@atoms/Card/Card'
import { Skeleton } from '@atoms/Skeleton/Skeleton'
import { useDashboardStats } from '../queries/useDashboardStats'
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts'

const STAGE_COLORS: Record<string, string> = {
  NEW: '#3B82F6',
  QUALIFYING: '#F59E0B',
  PROPOSAL_PHASE: '#8B5CF6',
  CLOSED_WON: '#10B981',
  CLOSED_LOST: '#6B7280',
  DRAFT: '#94A3B8',
  SENT: '#0EA5E9',
  NEGOTIATION: '#F97316',
  WON: '#10B981',
  LOST: '#EF4444',
  SUPERSEDED: '#A1A1AA',
}

const LEAD_STAGE_LABELS: Record<string, string> = {
  NEW: 'New',
  QUALIFYING: 'Qualifying',
  PROPOSAL_PHASE: 'Proposal Phase',
  CLOSED_WON: 'Won',
  CLOSED_LOST: 'Lost',
}

const PROPOSAL_STAGE_LABELS: Record<string, string> = {
  DRAFT: 'Draft',
  SENT: 'Sent',
  NEGOTIATION: 'Negotiation',
  WON: 'Won',
  LOST: 'Lost',
  SUPERSEDED: 'Superseded',
}

function DashboardSkeleton() {
  return (
    <div>
      <PageHeader title="Dashboard" description="Welcome to VERP CRM" />
      <div className="px-6 pb-6 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} variant="card" />
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {Array.from({ length: 2 }).map((_, i) => (
            <Skeleton key={i} variant="card" />
          ))}
        </div>
      </div>
    </div>
  )
}

const stageColors: Record<string, string> = {
  NEW: 'bg-info',
  QUALIFYING: 'bg-warning',
  PROPOSAL_PHASE: 'bg-primary',
  CLOSED_WON: 'bg-success',
  CLOSED_LOST: 'bg-neutral-300',
}

const stageLabels: Record<string, string> = {
  NEW: 'New Leads',
  QUALIFYING: 'Qualifying',
  PROPOSAL_PHASE: 'Proposal Phase',
  CLOSED_WON: 'Closed Won',
  CLOSED_LOST: 'Closed Lost',
}

function RecentActivity({ transitions }: { transitions: { id: number; entity_type: string; entity_id: number; to_stage: string; transitioned_at: string }[] }) {
  if (transitions.length === 0) {
    return (
      <Card variant="bordered" header={<h3 className="text-h6 text-text">Recent Activity</h3>}>
        <div className="py-8 text-center text-caption text-text-tertiary">No recent activity</div>
      </Card>
    )
  }

  return (
    <Card variant="bordered" header={<h3 className="text-h6 text-text">Recent Activity</h3>}>
      <div className="divide-y divide-border-light -mx-5 -mb-5">
        {transitions.slice(0, 10).map((t) => (
          <div key={t.id} className="px-5 py-3.5 flex items-center gap-3">
            <div className="size-8 rounded-full bg-primary-soft text-primary flex items-center justify-center text-xs font-semibold">
              {t.entity_type === 'lead' ? 'L' : 'P'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-small text-text">
                {t.entity_type === 'lead' ? 'Lead' : 'Proposal'} #{t.entity_id} moved to <span className="font-medium">{t.to_stage}</span>
              </p>
            </div>
            <span className="text-caption text-text-tertiary whitespace-nowrap">
              {new Date(t.transitioned_at).toLocaleDateString()}
            </span>
          </div>
        ))}
      </div>
    </Card>
  )
}

export function Component() {
  const { data: stats, isLoading } = useDashboardStats()

  if (isLoading) {
    return <DashboardSkeleton />
  }

  const totalContacts = stats?.total_contacts ?? 0
  const totalLeads = stats?.total_leads ?? 0
  const pendingVisits = stats?.pending_visits ?? 0
  const revenue = stats?.revenue_won ?? 0
  const leadsByStage = stats?.leads_by_stage ?? {}
  const proposalsByStage = stats?.proposals_by_stage ?? {}
  const transitions = stats?.recent_transitions ?? []

  const pipelineStages = ['NEW', 'QUALIFYING', 'PROPOSAL_PHASE', 'CLOSED_WON', 'CLOSED_LOST']

  const leadChartData = pipelineStages
    .filter((s) => leadsByStage[s])
    .map((stage) => ({
      name: LEAD_STAGE_LABELS[stage] ?? stage,
      value: leadsByStage[stage],
      color: STAGE_COLORS[stage] ?? '#6B7280',
    }))
  if (leadChartData.length === 0 && totalLeads > 0) {
    for (const [stage, count] of Object.entries(leadsByStage)) {
      leadChartData.push({
        name: LEAD_STAGE_LABELS[stage] ?? stage,
        value: count,
        color: STAGE_COLORS[stage] ?? '#6B7280',
      })
    }
  }

  const proposalChartData = Object.entries(proposalsByStage).map(([stage, count]) => ({
    name: PROPOSAL_STAGE_LABELS[stage] ?? stage,
    value: count,
    color: STAGE_COLORS[stage] ?? '#6B7280',
  }))

  return (
    <div>
      <PageHeader title="Dashboard" description="Welcome to VERP CRM" />
      <div className="px-6 pb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <Card variant="elevated" padding="lg">
            <p className="text-small text-text-secondary">Total Contacts</p>
            <p className="text-h3 text-text mt-1">{totalContacts}</p>
          </Card>
          <Card variant="elevated" padding="lg">
            <p className="text-small text-text-secondary">Active Leads</p>
            <p className="text-h3 text-text mt-1">{totalLeads}</p>
          </Card>
          <Card variant="elevated" padding="lg">
            <p className="text-small text-text-secondary">Pending Visits</p>
            <p className="text-h3 text-text mt-1">{pendingVisits}</p>
          </Card>
          <Card variant="elevated" padding="lg">
            <p className="text-small text-text-secondary">Revenue (Won)</p>
            <p className="text-h3 text-text mt-1">MXN {(revenue / 1000).toFixed(1)}k</p>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card variant="bordered" padding="lg" header={<h3 className="text-h6 text-text">Leads by Stage</h3>}>
            {leadChartData.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-caption text-text-tertiary">No data</div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie data={leadChartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} innerRadius={50} label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}>
                    {leadChartData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </Card>
          <Card variant="bordered" padding="lg" header={<h3 className="text-h6 text-text">Proposals by Stage</h3>}>
            {proposalChartData.length === 0 ? (
              <div className="flex items-center justify-center h-64 text-caption text-text-tertiary">No data</div>
            ) : (
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={proposalChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                    {proposalChartData.map((entry, i) => (
                      <Cell key={i} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <Card variant="bordered" padding="lg" header={<h3 className="text-h6 text-text">Pipeline Overview</h3>}>
              <div className="space-y-4">
                {pipelineStages.map((stage) => {
                  const count = leadsByStage[stage] ?? 0
                  const pct = totalLeads > 0 ? (count / totalLeads) * 100 : 0
                  return (
                    <div key={stage} className="flex items-center justify-between">
                      <span className="text-small text-text-secondary">{stageLabels[stage]}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-32 h-2 bg-neutral-100 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${stageColors[stage]}`} style={{ width: `${pct}%` }} />
                        </div>
                        <span className="text-small font-medium text-text">{count}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </Card>
          </div>
          <div>
            <RecentActivity transitions={transitions} />
          </div>
        </div>
      </div>
    </div>
  )
}

Component.displayName = 'DashboardPage'
