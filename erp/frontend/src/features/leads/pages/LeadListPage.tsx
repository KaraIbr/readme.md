import { useState, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { DataTable } from '@organisms/DataTable/DataTable'
import { Button } from '@atoms/Button/Button'
import { Badge } from '@atoms/Badge/Badge'
import { AdvancedFilter } from '@organisms/AdvancedFilter/AdvancedFilter'
import type { FilterField } from '@organisms/AdvancedFilter/AdvancedFilter'
import { LeadBoard } from '@features/pipeline/components/LeadBoard'
import { useLeadList } from '../queries/useLeads'
import { STAGE_LABELS, STAGE_VARIANTS, INTEREST_LABELS, LEAD_STAGES, LEAD_INTEREST_TYPES } from '../types'
import type { LeadRead } from '../types'
import type { Column } from '@organisms/DataTable/DataTable'
import { LeadDetailDrawer } from '../components/LeadDetailDrawer'

const filterFields: FilterField[] = [
  { key: 'search', label: 'Search', type: 'text', placeholder: 'Search by title...' },
  { key: 'stageFilter', label: 'Stage', type: 'select', options: LEAD_STAGES.map((s) => ({ label: STAGE_LABELS[s], value: s })) },
  { key: 'interestFilter', label: 'Interest', type: 'select', options: LEAD_INTEREST_TYPES.map((t) => ({ label: INTEREST_LABELS[t], value: t })) },
]

type ViewMode = 'table' | 'kanban'

export function Component() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [selectedLeadId, setSelectedLeadId] = useState<number | null>(null)
  const [viewMode, setViewMode] = useState<ViewMode>('table')
  const { data, isLoading } = useLeadList({ stage: filters.stageFilter ? (filters.stageFilter as LeadRead['current_stage']) : undefined })

  const filtered = useMemo(() => {
    let result = data?.items ?? []
    const search = filters.search ?? ''
    const interestFilter = filters.interestFilter ?? ''
    if (search) {
      result = result.filter(l => l.title.toLowerCase().includes(search.toLowerCase()))
    }
    if (interestFilter) {
      result = result.filter(l => l.interest_type === interestFilter)
    }
    return result
  }, [data, filters])

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  const handleClearFilters = () => {
    setFilters({})
  }

  const handleRowClick = useCallback((id: number) => {
    setSelectedLeadId(id)
  }, [])

  const handleCloseDrawer = useCallback(() => {
    setSelectedLeadId(null)
  }, [])

  const columns: Column<LeadRead>[] = [
    {
      key: 'title',
      header: 'Name',
      render: (l) => (
        <button className="text-primary hover:underline font-medium text-left" onClick={() => handleRowClick(l.id)}>
          {l.title}
        </button>
      ),
    },
    {
      key: 'interest_type',
      header: 'Interest',
      render: (l) => <span className="text-sm">{INTEREST_LABELS[l.interest_type]}</span>,
    },
    {
      key: 'current_stage',
      header: 'Stage',
      render: (l) => (
        <Badge variant={STAGE_VARIANTS[l.current_stage]} size="sm">
          {STAGE_LABELS[l.current_stage]}
        </Badge>
      ),
    },
    {
      key: 'contact_id',
      header: 'Technician',
      render: (l) => (
        <button className="text-primary hover:underline text-sm" onClick={() => navigate(`/contacts/${l.contact_id}`)}>
          #{l.contact_id}
        </button>
      ),
    },
    {
      key: 'qualification_score',
      header: 'Score',
      render: (l) => <span>{l.qualification_score ?? '—'}</span>,
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (l) => new Date(l.created_at).toLocaleDateString(),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Leads"
        description="Manage sales leads and opportunities"
        actions={
          <div className="flex items-center gap-3">
            <div className="flex bg-neutral-100 rounded-lg p-0.5">
              <button
                type="button"
                onClick={() => setViewMode('table')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${viewMode === 'table' ? 'bg-white shadow-sm text-text' : 'text-text-tertiary hover:text-text'}`}
              >
                Table
              </button>
              <button
                type="button"
                onClick={() => setViewMode('kanban')}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${viewMode === 'kanban' ? 'bg-white shadow-sm text-text' : 'text-text-tertiary hover:text-text'}`}
              >
                Kanban
              </button>
            </div>
            <Button onClick={() => navigate('/leads/new')}>New Lead</Button>
          </div>
        }
      />
      <div className="px-6 pb-6 space-y-4">
        {viewMode === 'table' ? (
          <>
            <div className="bg-white rounded-xl border border-border p-4">
              <AdvancedFilter
                fields={filterFields}
                values={filters}
                onChange={handleFilterChange}
                onClear={handleClearFilters}
              />
            </div>
            <DataTable<LeadRead>
              columns={columns}
              data={filtered}
              keyExtractor={(l) => String(l.id)}
              loading={isLoading}
              emptyTitle="No leads found"
              emptyDescription="Create your lead"
            />
          </>
        ) : (
          <LeadBoard />
        )}
      </div>

      <LeadDetailDrawer
        leadId={selectedLeadId}
        onClose={handleCloseDrawer}
      />
    </div>
  )
}

Component.displayName = 'LeadListPage'
