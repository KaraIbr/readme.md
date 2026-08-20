import { useMemo } from 'react'
import { Badge } from '@atoms/Badge/Badge'
import { EmptyState } from '@molecules/EmptyState/EmptyState'
import { DataTable } from '@organisms/DataTable/DataTable'
import type { Column } from '@organisms/DataTable/DataTable'
import type { TechnicalVisitRead } from '../types'
import { STATUS_LABELS, STATUS_VARIANTS } from '../types'
import { VisitCard } from './VisitCard'

interface VisitsListCardsProps {
  mode: 'cards'
  visits: TechnicalVisitRead[]
  onVisitClick?: (id: number) => void
  loading?: boolean
  emptyTitle?: string
  emptyDescription?: string
  emptyAction?: React.ReactNode
  className?: string
}

interface VisitsListTableProps {
  mode: 'table'
  visits: TechnicalVisitRead[]
  onVisitClick?: (id: number) => void
  loading?: boolean
  emptyTitle?: string
  emptyDescription?: string
  sortable?: boolean
  className?: string
}

type VisitsListProps = VisitsListCardsProps | VisitsListTableProps

function LoadingSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="p-3 rounded-lg border border-border animate-pulse">
          <div className="flex items-center justify-between">
            <div className="h-4 w-20 bg-neutral-200 rounded" />
            <div className="h-5 w-16 bg-neutral-200 rounded-full" />
          </div>
          <div className="mt-2 h-3 w-32 bg-neutral-200 rounded" />
        </div>
      ))}
    </div>
  )
}

function CardsMode({
  visits,
  onVisitClick,
  emptyTitle = 'No visits',
  emptyDescription,
  emptyAction,
  className = '',
}: Omit<VisitsListCardsProps, 'mode' | 'loading'>) {
  if (visits.length === 0) {
    return (
      <EmptyState
        title={emptyTitle}
        description={emptyDescription}
        action={emptyAction}
        className={className}
      />
    )
  }

  return (
    <div className={`space-y-2 ${className}`}>
      {visits.map((v) => (
        <VisitCard key={v.id} visit={v} onClick={onVisitClick} />
      ))}
    </div>
  )
}

const tableColumns: Column<TechnicalVisitRead>[] = [
  {
    key: 'id',
    header: 'ID',
    render: (v) => <span className="font-medium text-primary">#{v.id}</span>,
  },
  {
    key: 'status',
    header: 'Status',
    render: (v) => (
      <Badge variant={STATUS_VARIANTS[v.status]} size="sm">{STATUS_LABELS[v.status]}</Badge>
    ),
  },
  {
    key: 'lead_id',
    header: 'Lead',
    render: (v) => <span className="text-text">#{v.lead_id}</span>,
  },
  {
    key: 'scheduled_at',
    header: 'Scheduled',
    render: (v) => v.scheduled_at
      ? new Date(v.scheduled_at).toLocaleDateString()
      : <span className="text-text-tertiary">\u2014</span>,
  },
  {
    key: 'receiver_name',
    header: 'Receiver',
    render: (v) => v.receiver_name ?? <span className="text-text-tertiary">\u2014</span>,
  },
  {
    key: 'created_at',
    header: 'Created',
    render: (v) => new Date(v.created_at).toLocaleDateString(),
  },
]

function TableMode({
  visits,
  onVisitClick,
  emptyTitle = 'No visits found',
  emptyDescription,
  sortable = true,
  className = '',
}: Omit<VisitsListTableProps, 'mode' | 'loading'>) {
  const handleRowClick = useMemo(() => {
    if (!onVisitClick) return undefined
    return (v: TechnicalVisitRead) => onVisitClick(v.id)
  }, [onVisitClick])

  return (
    <DataTable<TechnicalVisitRead>
      columns={tableColumns}
      data={visits}
      keyExtractor={(v) => String(v.id)}
      sortable={sortable}
      onRowClick={handleRowClick}
      emptyTitle={emptyTitle}
      emptyDescription={emptyDescription}
      className={className}
    />
  )
}

export function VisitsList(props: VisitsListProps) {
  const { mode, visits, onVisitClick, loading, ...rest } = props

  if (loading) {
    if (mode === 'table') {
      return <DataTable columns={[]} data={[]} keyExtractor={() => ''} loading />
    }
    return <LoadingSkeleton />
  }

  if (mode === 'cards') {
    return <CardsMode visits={visits} onVisitClick={onVisitClick} {...rest} />
  }

  return <TableMode visits={visits} onVisitClick={onVisitClick} {...rest} />
}
