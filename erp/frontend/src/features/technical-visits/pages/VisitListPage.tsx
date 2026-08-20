import { useState, useMemo, useCallback } from 'react'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { DataTable } from '@organisms/DataTable/DataTable'
import { Button } from '@atoms/Button/Button'
import { Badge } from '@atoms/Badge/Badge'
import { AdvancedFilter } from '@organisms/AdvancedFilter/AdvancedFilter'
import type { FilterField } from '@organisms/AdvancedFilter/AdvancedFilter'
import { useVisitList } from '../queries/useVisits'
import { STATUS_LABELS, STATUS_VARIANTS, VISIT_STATUSES } from '../types'
import type { TechnicalVisitRead } from '../types'
import type { Column } from '@organisms/DataTable/DataTable'
import { VisitDetailDrawer } from '../components/VisitDetailDrawer'
import { VisitCreateDrawer } from '../components/VisitCreateDrawer'

const filterFields: FilterField[] = [
  { key: 'search', label: 'Search', type: 'text', placeholder: 'Search by lead ID...' },
  { key: 'statusFilter', label: 'Status', type: 'select', options: VISIT_STATUSES.map((s) => ({ label: STATUS_LABELS[s], value: s })) },
]

export function Component() {
  const [showCreateDrawer, setShowCreateDrawer] = useState(false)
  const [selectedVisitId, setSelectedVisitId] = useState<number | null>(null)
  const [filters, setFilters] = useState<Record<string, string>>({})
  const { data, isLoading } = useVisitList({ status: filters.statusFilter ? (filters.statusFilter as TechnicalVisitRead['status']) : undefined })

  const filtered = useMemo(() => {
    let result = data?.items ?? []
    const search = filters.search ?? ''
    if (search) {
      result = result.filter(v => String(v.lead_id).includes(search.toLowerCase()))
    }
    return result
  }, [data, filters])

  const handleRowClick = useCallback((id: number) => {
    setSelectedVisitId(id)
  }, [])

  const handleCloseDrawer = useCallback(() => {
    setSelectedVisitId(null)
  }, [])

  const columns: Column<TechnicalVisitRead>[] = [
    {
      key: 'id',
      header: 'ID',
      render: (v) => (
        <button className="text-primary hover:underline font-medium text-left" onClick={() => handleRowClick(v.id)}>
          #{v.id}
        </button>
      ),
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
      render: (v) => (
        <span className="text-sm text-text">#{v.lead_id}</span>
      ),
    },
    {
      key: 'scheduled_at',
      header: 'Scheduled',
      render: (v) => v.scheduled_at ? new Date(v.scheduled_at).toLocaleDateString() : <span className="text-text-tertiary">\u2014</span>,
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

  return (
    <div>
      <PageHeader
        title="Technical Visits"
        description="Manage site visits and inspections"
        actions={
          <Button onClick={() => setShowCreateDrawer(true)}>New Visit</Button>
        }
      />
      <div className="px-6 pb-6 space-y-4">
        <div className="bg-white rounded-xl border border-border p-4">
          <AdvancedFilter
            fields={filterFields}
            values={filters}
            onChange={(key, value) => setFilters((prev) => ({ ...prev, [key]: value }))}
            onClear={() => setFilters({})}
          />
        </div>
        <DataTable<TechnicalVisitRead>
          columns={columns}
          data={filtered}
          keyExtractor={(v) => String(v.id)}
          loading={isLoading}
          sortable
          emptyTitle="No visits found"
          emptyDescription="Create your first visit to get started"
        />
      </div>

      <VisitCreateDrawer
        open={showCreateDrawer}
        onClose={() => setShowCreateDrawer(false)}
      />

      <VisitDetailDrawer
        visitId={selectedVisitId}
        onClose={handleCloseDrawer}
      />
    </div>
  )
}

Component.displayName = 'VisitListPage'
