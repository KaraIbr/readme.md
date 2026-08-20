import { useState, useMemo, useCallback } from 'react'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { DataTable } from '@organisms/DataTable/DataTable'
import { CardGrid } from '@molecules/CardGrid/CardGrid'
import { Card } from '@atoms/Card/Card'
import { Button } from '@atoms/Button/Button'
import { AdvancedFilter } from '@organisms/AdvancedFilter/AdvancedFilter'
import type { FilterField } from '@organisms/AdvancedFilter/AdvancedFilter'
import { useCompanies } from '../queries/useCompanies'
import type { CompanyRead } from '../types'
import type { Column } from '@organisms/DataTable/DataTable'
import { CompanyDetailDrawer } from '../components/CompanyDetailDrawer'
import { CompanyCreateDrawer } from '../components/CompanyCreateDrawer'

const filterFields: FilterField[] = [
  { key: 'search', label: 'Search', type: 'text', placeholder: 'Search by name or city...' },
  { key: 'industry', label: 'Industry', type: 'text', placeholder: 'Filter by industry...' },
]

type ViewMode = 'grid' | 'table'

export function Component() {
  const [viewMode, setViewMode] = useState<ViewMode>('grid')
  const [showCreateDrawer, setShowCreateDrawer] = useState(false)
  const [filters, setFilters] = useState<Record<string, string>>({})
  const [selectedCompanyId, setSelectedCompanyId] = useState<number | null>(null)
  const { data, isLoading } = useCompanies()

  const filtered = useMemo(() => {
    let result = data ?? []
    const search = filters.search ?? ''
    const industry = filters.industry ?? ''
    if (search) {
      const q = search.toLowerCase()
      result = result.filter(c =>
        c.name.toLowerCase().includes(q) ||
        (c.city ?? '').toLowerCase().includes(q)
      )
    }
    if (industry) {
      result = result.filter(c => (c.industry ?? '').toLowerCase().includes(industry.toLowerCase()))
    }
    return result
  }, [data, filters])

  const handleRowClick = useCallback((id: number) => {
    setSelectedCompanyId(id)
  }, [])

  const handleCloseDrawer = useCallback(() => {
    setSelectedCompanyId(null)
  }, [])

  const columns: Column<CompanyRead>[] = [
    {
      key: 'name',
      header: 'Company Name',
      sortable: true,
      render: (c) => (
        <button
          className="text-primary hover:underline font-medium text-left"
          onClick={() => handleRowClick(c.id)}
        >
          {c.name}
        </button>
      ),
    },
    { key: 'industry', header: 'Industry', sortable: true },
    { key: 'city', header: 'City', sortable: true },
    { key: 'state', header: 'State' },
    { key: 'address_line', header: 'Address' },
    { key: 'postal_code', header: 'Postal Code' },
  ]

  return (
    <div>
      <PageHeader
        title="Companies"
        description="Manage company contacts"
        accent
        viewToggle={
          <div className="flex bg-neutral-100 rounded-lg p-0.5">
            <button
              type="button"
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${viewMode === 'grid' ? 'bg-white shadow-sm text-text' : 'text-text-tertiary hover:text-text'}`}
            >
              Grid
            </button>
            <button
              type="button"
              onClick={() => setViewMode('table')}
              className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors ${viewMode === 'table' ? 'bg-white shadow-sm text-text' : 'text-text-tertiary hover:text-text'}`}
            >
              Table
            </button>
          </div>
        }
        actions={
          <Button onClick={() => setShowCreateDrawer(true)}>New Company</Button>
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

        {viewMode === 'grid' ? (
          <CardGrid<CompanyRead>
            items={filtered}
            keyExtractor={(c) => String(c.id)}
            loading={isLoading}
            emptyTitle="No companies found"
            emptyDescription="Create your first company to get started"
            renderCard={(company) => (
              <Card
                variant="interactive"
                onClick={() => handleRowClick(company.id)}
              >
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-h6 text-text">{company.name}</h3>
                </div>
                {company.industry && (
                  <p className="text-small text-text-secondary">{company.industry}</p>
                )}
                <div className="mt-3 flex items-center gap-3 text-caption text-text-tertiary">
                  {company.city && <span>{company.city}</span>}
                  {company.state && <span>{company.state}</span>}
                </div>
              </Card>
            )}
          />
        ) : (
          <DataTable<CompanyRead>
            columns={columns}
            data={filtered}
            keyExtractor={(c) => String(c.id)}
            loading={isLoading}
            sortable
            emptyTitle="No companies found"
            emptyDescription="Create your first company to get started"
          />
        )}
      </div>

      <CompanyCreateDrawer
        open={showCreateDrawer}
        onClose={() => setShowCreateDrawer(false)}
      />

      <CompanyDetailDrawer
        companyId={selectedCompanyId}
        onClose={handleCloseDrawer}
      />
    </div>
  )
}

Component.displayName = 'CompanyListPage'
