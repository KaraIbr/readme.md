import { useState, useMemo, useCallback } from 'react'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { DataTable } from '@organisms/DataTable/DataTable'
import { Button } from '@atoms/Button/Button'
import { Badge } from '@atoms/Badge/Badge'
import { AdvancedFilter } from '@organisms/AdvancedFilter/AdvancedFilter'
import type { FilterField } from '@organisms/AdvancedFilter/AdvancedFilter'
import { useActivities } from '../queries/useActivities'
import { ACTIVITY_LABELS, ACTIVITY_VARIANTS, ACTIVITY_TYPES } from '../types'
import type { ActivityRead } from '../types'
import type { Column } from '@organisms/DataTable/DataTable'
import { ActivityCreateDrawer } from '../components/ActivityCreateDrawer'
import { ActivityDetailDrawer } from '../components/ActivityDetailDrawer'

const filterFields: FilterField[] = [
  { key: 'search', label: 'Search', type: 'text', placeholder: 'Search by title...' },
  { key: 'typeFilter', label: 'Type', type: 'select', options: ACTIVITY_TYPES.map((t) => ({ label: ACTIVITY_LABELS[t], value: t })) },
  { key: 'statusFilter', label: 'Status', type: 'select', options: [{ label: 'Pending', value: 'pending' }, { label: 'Done', value: 'done' }] },
]

export function Component() {
  const [showCreateDrawer, setShowCreateDrawer] = useState(false)
  const [selectedActivityId, setSelectedActivityId] = useState<number | null>(null)
  const [filters, setFilters] = useState<Record<string, string>>({})
  const { data: activities, isLoading } = useActivities({
    activity_type: filters.typeFilter || undefined,
  })

  const filtered = useMemo(() => {
    let result = activities ?? []
    const search = filters.search ?? ''
    const statusFilter = filters.statusFilter ?? ''
    if (search) {
      const q = search.toLowerCase()
      result = result.filter((a) => a.title.toLowerCase().includes(q))
    }
    if (statusFilter === 'pending') {
      result = result.filter((a) => !a.completed_at)
    } else if (statusFilter === 'done') {
      result = result.filter((a) => a.completed_at)
    }
    return result
  }, [activities, filters])

  const handleRowClick = useCallback((id: number) => {
    setSelectedActivityId(id)
  }, [])

  const handleCloseDrawer = useCallback(() => {
    setSelectedActivityId(null)
  }, [])

  const columns: Column<ActivityRead>[] = [
    {
      key: 'activity_type',
      header: 'Type',
      sortable: true,
      render: (a) => (
        <Badge variant={ACTIVITY_VARIANTS[a.activity_type]} size="sm">
          {ACTIVITY_LABELS[a.activity_type]}
        </Badge>
      ),
    },
    {
      key: 'title',
      header: 'Title',
      sortable: true,
      render: (a) => (
        <button
          className="text-primary hover:underline font-medium text-left"
          onClick={() => handleRowClick(a.id)}
        >
          {a.title}
        </button>
      ),
    },
    { key: 'description', header: 'Description' },
    {
      key: 'completed_at',
      header: 'Status',
      render: (a) => (
        <Badge variant={a.completed_at ? 'success' : 'default'} size="sm">
          {a.completed_at ? 'Done' : 'Pending'}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (a) => new Date(a.created_at).toLocaleDateString(),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Activities"
        description="Track calls, emails, meetings and notes"
        actions={
          <Button onClick={() => setShowCreateDrawer(true)}>New Activity</Button>
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
        <DataTable<ActivityRead>
          columns={columns}
          data={filtered}
          keyExtractor={(a) => String(a.id)}
          loading={isLoading}
          sortable
          emptyTitle="No activities"
          emptyDescription="Create your first activity to get started"
        />
      </div>

      <ActivityCreateDrawer
        open={showCreateDrawer}
        onClose={() => setShowCreateDrawer(false)}
      />

      <ActivityDetailDrawer
        activityId={selectedActivityId}
        onClose={handleCloseDrawer}
      />
    </div>
  )
}

Component.displayName = 'ActivityListPage'
