import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { DataTable } from '@organisms/DataTable/DataTable'
import { Badge } from '@atoms/Badge/Badge'
import { Spinner } from '@atoms/Spinner/Spinner'
import { EmptyState } from '@molecules/EmptyState/EmptyState'
import { useTransitions } from '@features/pipeline/queries/usePipeline'
import { useUsers } from '../queries/useAdminUsers'
import type { StageTransitionRead } from '@features/pipeline/types'
import type { Column } from '@organisms/DataTable/DataTable'

const ENTITY_LABELS: Record<string, string> = {
  lead: 'Lead',
  proposal: 'Proposal',
}

function actionVariant(stage: string): 'info' | 'warning' | 'success' | 'danger' | 'default' {
  if (stage === 'WON' || stage === 'CLOSED_WON') return 'success'
  if (stage === 'LOST' || stage === 'CLOSED_LOST') return 'danger'
  if (stage === 'QUALIFYING' || stage === 'SENT') return 'warning'
  if (stage === 'PROPOSAL_PHASE' || stage === 'NEGOTIATION') return 'info'
  return 'default'
}

function formatTimestamp(ts: string): string {
  return new Date(ts).toLocaleString()
}

export function Component() {
  const navigate = useNavigate()
  const { data: transitions, isLoading: transitionsLoading, isError } = useTransitions({ limit: 200 })
  const { data: users } = useUsers()

  const userMap = useMemo(() => {
    const map = new Map<number, string>()
    if (!users) return map
    for (const u of users) {
      map.set(u.id, u.full_name || u.email)
    }
    return map
  }, [users])

  const resolveUser = (userId: number): string => userMap.get(userId) ?? `User #${userId}`

  const columns: Column<StageTransitionRead>[] = [
    {
      key: 'id',
      header: 'ID',
      render: (t) => <span className="font-mono text-xs text-text-tertiary">#{t.id}</span>,
    },
    {
      key: 'entity_type',
      header: 'Type',
      render: (t) => (
        <Badge variant="default" size="sm">
          {ENTITY_LABELS[t.entity_type] ?? t.entity_type}
        </Badge>
      ),
    },
    {
      key: 'entity_id',
      header: 'Entity',
      render: (t) => {
        const path = t.entity_type === 'lead' ? '/leads' : '/proposals'
        return (
          <button
            className="text-primary hover:underline font-medium text-left"
            onClick={() => navigate(`${path}/${t.entity_id}`)}
          >
            #{t.entity_id}
          </button>
        )
      },
    },
    {
      key: 'to_stage',
      header: 'Transition',
      render: (t) => (
        <div className="flex items-center gap-1.5">
          {t.from_stage && (
            <Badge variant="default" size="sm">{t.from_stage}</Badge>
          )}
          {t.from_stage && (
            <svg className="size-3 text-text-tertiary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
            </svg>
          )}
          <Badge variant={actionVariant(t.to_stage)} size="sm">{t.to_stage}</Badge>
        </div>
      ),
    },
    {
      key: 'transitioned_by',
      header: 'User',
      render: (t) => (
        <span className="text-sm text-text-secondary">{resolveUser(t.transitioned_by)}</span>
      ),
    },
    {
      key: 'transitioned_at',
      header: 'Timestamp',
      render: (t) => (
        <span className="text-sm text-text-tertiary whitespace-nowrap">{formatTimestamp(t.transitioned_at)}</span>
      ),
    },
    {
      key: 'reason',
      header: 'Reason',
      render: (t) => t.reason ?? t.notes ?? <span className="text-text-tertiary">—</span>,
    },
  ]

  if (isError) {
    return (
      <div>
        <PageHeader title="Admin" description="Audit log" />
        <div className="px-6 pb-6">
          <EmptyState title="Failed to load audit log" description="Could not fetch pipeline transitions. Check your permissions." />
        </div>
      </div>
    )
  }

  return (
    <div>
      <PageHeader title="Admin" description="Audit log — pipeline stage transitions" />
      <div className="px-6 pb-6">
        {transitionsLoading ? (
          <div className="flex items-center justify-center py-20">
            <Spinner size="lg" />
          </div>
        ) : transitions && transitions.length > 0 ? (
          <DataTable<StageTransitionRead>
            columns={columns}
            data={transitions}
            keyExtractor={(t) => String(t.id)}
            emptyTitle="No transitions found"
            emptyDescription="Stage transitions will appear here as leads and proposals move through the pipeline."
          />
        ) : (
          <EmptyState
            title="No transitions yet"
            description="Stage transitions will appear here as leads and proposals move through the pipeline."
          />
        )}
      </div>
    </div>
  )
}

Component.displayName = 'AdminAuditPage'
