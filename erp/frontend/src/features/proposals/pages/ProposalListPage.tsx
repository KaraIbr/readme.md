import { useState, useMemo, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { DataTable } from '@organisms/DataTable/DataTable'
import { Button } from '@atoms/Button/Button'
import { Badge } from '@atoms/Badge/Badge'
import { AdvancedFilter } from '@organisms/AdvancedFilter/AdvancedFilter'
import type { FilterField } from '@organisms/AdvancedFilter/AdvancedFilter'
import { useProposalList } from '../queries/useProposals'
import { STAGE_LABELS, STAGE_VARIANTS, SYSTEM_TYPE_LABELS, PROPOSAL_STAGES, PROPOSAL_SYSTEM_TYPES } from '../types'
import type { ProposalRead } from '../types'
import type { Column } from '@organisms/DataTable/DataTable'
import { ProposalDetailDrawer } from '../components/ProposalDetailDrawer'

function formatCurrency(value: number | null): string {
  if (value == null) return '—'
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value)
}

const filterFields: FilterField[] = [
  { key: 'search', label: 'Search', type: 'text', placeholder: 'Search by name...' },
  { key: 'stageFilter', label: 'Stage', type: 'select', options: PROPOSAL_STAGES.map((s) => ({ label: STAGE_LABELS[s], value: s })) },
  { key: 'systemFilter', label: 'System', type: 'select', options: PROPOSAL_SYSTEM_TYPES.map((t) => ({ label: SYSTEM_TYPE_LABELS[t], value: t })) },
]

export function Component() {
  const navigate = useNavigate()
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [selectedProposalId, setSelectedProposalId] = useState<number | null>(null)
  const { data, isLoading } = useProposalList({ stage: filters.stageFilter ? (filters.stageFilter as ProposalRead['current_stage']) : undefined })

  const filtered = useMemo(() => {
    let result = data?.items ?? []
    const search = filters.search ?? ''
    const systemFilter = filters.systemFilter ?? ''
    if (search) {
      result = result.filter(p => p.name.toLowerCase().includes(search.toLowerCase()))
    }
    if (systemFilter) {
      result = result.filter(p => p.system_type === systemFilter)
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
    setSelectedProposalId(id)
  }, [])

  const handleCloseDrawer = useCallback(() => {
    setSelectedProposalId(null)
  }, [])

  const columns: Column<ProposalRead>[] = [
    {
      key: 'name',
      header: 'Name',
      render: (p) => (
        <button className="text-primary hover:underline font-medium text-left" onClick={() => handleRowClick(p.id)}>
          {p.name}
        </button>
      ),
    },
    {
      key: 'current_stage',
      header: 'Stage',
      render: (p) => (
        <Badge variant={STAGE_VARIANTS[p.current_stage]} size="sm">
          {STAGE_LABELS[p.current_stage]}
        </Badge>
      ),
    },
    {
      key: 'system_type',
      header: 'System',
      render: (p) => p.system_type ? <span>{SYSTEM_TYPE_LABELS[p.system_type]}</span> : <span className="text-text-tertiary">—</span>,
    },
    {
      key: 'total_price',
      header: 'Total Price',
      align: 'right',
      render: (p) => <span className="font-medium">{formatCurrency(p.total_price)}</span>,
    },
    {
      key: 'lead_name',
      header: 'Lead',
      render: (p) => (
        <button className="text-primary hover:underline text-sm text-left" onClick={() => navigate(`/leads/${p.lead_id}`)}>
          {p.lead_name ?? `#${p.lead_id}`}
        </button>
      ),
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (p) => new Date(p.created_at).toLocaleDateString(),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Proposals"
        description="Manage commercial proposals"
        actions={
          <Button onClick={() => navigate('/proposals/new')}>New Proposal</Button>
        }
      />
      <div className="px-6 pb-6 space-y-4">
        <div className="bg-white rounded-xl border border-border p-4">
          <AdvancedFilter
            fields={filterFields}
            values={filters}
            onChange={handleFilterChange}
            onClear={handleClearFilters}
          />
        </div>
        <DataTable<ProposalRead>
          columns={columns}
          data={filtered}
          keyExtractor={(p) => String(p.id)}
          loading={isLoading}
          emptyTitle="No proposals found"
          emptyDescription="Create your first proposal to get started"
        />
      </div>

      <ProposalDetailDrawer
        proposalId={selectedProposalId}
        onClose={handleCloseDrawer}
      />
    </div>
  )
}

Component.displayName = 'ProposalListPage'
