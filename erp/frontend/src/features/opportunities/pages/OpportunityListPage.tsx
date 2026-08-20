import { useState, useMemo, useCallback } from 'react'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { DataTable } from '@organisms/DataTable/DataTable'
import { Button } from '@atoms/Button/Button'
import { Badge } from '@atoms/Badge/Badge'
import { AdvancedFilter } from '@organisms/AdvancedFilter/AdvancedFilter'
import type { FilterField } from '@organisms/AdvancedFilter/AdvancedFilter'
import { useOpportunities } from '../queries/useOpportunities'
import { STAGE_LABELS, STAGE_VARIANTS, OPPORTUNITY_STAGES } from '../types'
import type { OpportunityRead } from '../types'
import type { Column } from '@organisms/DataTable/DataTable'
import { OpportunityDetailDrawer } from '../components/OpportunityDetailDrawer'
import { OpportunityCreateDrawer } from '../components/OpportunityCreateDrawer'

const filterFields: FilterField[] = [
  { key: 'search', label: 'Search', type: 'text', placeholder: 'Search by name...' },
  { key: 'stageFilter', label: 'Stage', type: 'select', options: OPPORTUNITY_STAGES.map((s) => ({ label: STAGE_LABELS[s], value: s })) },
]

export function Component() {
  const [showCreateDrawer, setShowCreateDrawer] = useState(false)
  const [selectedOpportunityId, setSelectedOpportunityId] = useState<number | null>(null)
  const [filters, setFilters] = useState<Record<string, string>>({})
  const { data, isLoading } = useOpportunities({
    stage: filters.stageFilter || undefined,
  })

  const filtered = useMemo(() => {
    let result = data ?? []
    const search = filters.search ?? ''
    if (search) {
      const q = search.toLowerCase()
      result = result.filter((o) => o.name.toLowerCase().includes(q))
    }
    return result
  }, [data, filters])

  const handleRowClick = useCallback((id: number) => {
    setSelectedOpportunityId(id)
  }, [])

  const handleCloseDrawer = useCallback(() => {
    setSelectedOpportunityId(null)
  }, [])

  const columns: Column<OpportunityRead>[] = [
    {
      key: 'name',
      header: 'Name',
      sortable: true,
      render: (o) => (
        <button
          className="text-primary hover:underline font-medium text-left"
          onClick={() => handleRowClick(o.id)}
        >
          {o.name}
        </button>
      ),
    },
    {
      key: 'current_stage',
      header: 'Stage',
      sortable: true,
      render: (o) => (
        <Badge variant={STAGE_VARIANTS[o.current_stage]} size="sm">
          {STAGE_LABELS[o.current_stage]}
        </Badge>
      ),
    },
    {
      key: 'value',
      header: 'Value',
      render: (o) => (o.value != null ? `${o.currency ?? 'MXN'} ${o.value.toLocaleString()}` : '—'),
    },
    { key: 'expected_close_date', header: 'Expected Close', render: (o) => o.expected_close_date ? new Date(o.expected_close_date).toLocaleDateString() : '—' },
  ]

  return (
    <div>
      <PageHeader
        title="Opportunities"
        description="Track sales opportunities"
        actions={
          <Button onClick={() => setShowCreateDrawer(true)}>New Opportunity</Button>
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
        <DataTable<OpportunityRead>
          columns={columns}
          data={filtered}
          keyExtractor={(o) => String(o.id)}
          loading={isLoading}
          sortable
          emptyTitle="No opportunities"
          emptyDescription="Create your first opportunity"
        />
      </div>

      <OpportunityCreateDrawer
        open={showCreateDrawer}
        onClose={() => setShowCreateDrawer(false)}
      />

      <OpportunityDetailDrawer
        opportunityId={selectedOpportunityId}
        onClose={handleCloseDrawer}
      />
    </div>
  )
}

Component.displayName = 'OpportunityListPage'
