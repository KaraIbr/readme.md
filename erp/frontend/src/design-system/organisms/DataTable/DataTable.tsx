import { useState, useMemo } from 'react'
import type { ReactNode } from 'react'
import { Skeleton } from '../../atoms/Skeleton/Skeleton'
import { EmptyState } from '../../molecules/EmptyState/EmptyState'

export interface Column<T> {
  key: string
  header: string
  render?: (item: T) => ReactNode
  width?: string
  align?: 'left' | 'center' | 'right'
  sortable?: boolean
  sortKey?: string
}

export interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  keyExtractor: (item: T) => string
  loading?: boolean
  emptyTitle?: string
  emptyDescription?: string
  sortable?: boolean
  onRowClick?: (item: T) => void
  pageSize?: number
  className?: string
}

type SortDir = 'asc' | 'desc'

function SortIcon({ dir, active }: { dir: SortDir; active: boolean }) {
  return (
    <span className={`inline-flex flex-col leading-none ml-1 -mt-0.5 ${active ? 'text-primary' : 'text-neutral-300'}`}>
      <svg width="8" height="5" viewBox="0 0 8 5" fill="currentColor" className={dir === 'asc' && active ? 'opacity-100' : 'opacity-40'}>
        <path d="M4 0L8 5H0z" />
      </svg>
      <svg width="8" height="5" viewBox="0 0 8 5" fill="currentColor" className={dir === 'desc' && active ? 'opacity-100' : 'opacity-40'}>
        <path d="M4 5L0 0h8z" />
      </svg>
    </span>
  )
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  loading = false,
  emptyTitle = 'No data',
  emptyDescription,
  sortable: globallySortable = false,
  onRowClick,
  pageSize = 25,
  className = '',
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<string | null>(null)
  const [sortDir, setSortDir] = useState<SortDir>('asc')
  const [page, setPage] = useState(0)

  const handleSort = (col: Column<T>) => {
    if (!globallySortable && !col.sortable) return
    const key = col.sortKey ?? col.key
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  const sorted = useMemo(() => {
    if (!sortKey) return data
    return [...data].sort((a, b) => {
      const aVal = (a as Record<string, unknown>)[sortKey]
      const bVal = (b as Record<string, unknown>)[sortKey]
      if (aVal == null) return 1
      if (bVal == null) return -1
      const cmp = String(aVal).localeCompare(String(bVal))
      return sortDir === 'asc' ? cmp : -cmp
    })
  }, [data, sortKey, sortDir])

  const totalPages = Math.max(1, Math.ceil(sorted.length / pageSize))
  const paged = sorted.slice(page * pageSize, (page + 1) * pageSize)

  if (loading) {
    return (
      <div className={`rounded-xl border border-border overflow-hidden ${className}`}>
        <div className="divide-y divide-border-light">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="px-5 py-3.5">
              <Skeleton variant="text" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (data.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />
  }

  return (
    <div className={`rounded-xl border border-border overflow-hidden bg-white ${className}`}>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="bg-surface-secondary">
              {columns.map((col) => {
                const canSort = globallySortable || col.sortable
                const isActive = sortKey === (col.sortKey ?? col.key)
                return (
                  <th
                    key={col.key}
                    className={`
                      px-5 py-3.5 text-sm font-medium text-text-secondary
                      ${col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'}
                      ${canSort ? 'cursor-pointer select-none hover:text-text transition-colors' : ''}
                      sticky top-0 bg-surface-secondary z-10
                    `.trim()}
                    style={col.width ? { width: col.width } : undefined}
                    onClick={() => canSort && handleSort(col)}
                  >
                    <span className="inline-flex items-center gap-0.5">
                      {col.header}
                      {canSort && <SortIcon dir={sortDir} active={isActive} />}
                    </span>
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {paged.map((item) => (
              <tr
                key={keyExtractor(item)}
                className={`
                  border-t border-border-light
                  transition-all duration-150
                  ${onRowClick ? 'cursor-pointer hover:bg-neutral-50 hover:shadow-sm' : 'hover:bg-neutral-25'}
                `.trim()}
                onClick={() => onRowClick?.(item)}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    className={`
                      px-5 py-3.5 text-sm text-text
                      ${col.align === 'right' ? 'text-right' : col.align === 'center' ? 'text-center' : 'text-left'}
                    `.trim()}
                  >
                    {col.render ? col.render(item) : String((item as Record<string, unknown>)[col.key] ?? '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {sorted.length > pageSize && (
        <div className="flex items-center justify-between px-5 py-3 border-t border-border bg-surface-secondary">
          <span className="text-xs text-text-tertiary">
            Showing {page * pageSize + 1}–{Math.min((page + 1) * pageSize, sorted.length)} of {sorted.length}
          </span>
          <div className="flex items-center gap-1.5">
            <button
              type="button"
              disabled={page === 0}
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              className="px-3 py-1.5 text-xs font-medium rounded-md text-text-secondary hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Prev
            </button>
            {Array.from({ length: Math.min(totalPages, 5) }).map((_, i) => {
              const start = Math.max(0, Math.min(page - 2, totalPages - 5))
              const p = start + i
              if (p >= totalPages) return null
              return (
                <button
                  key={p}
                  type="button"
                  onClick={() => setPage(p)}
                  className={`px-2.5 py-1.5 text-xs font-medium rounded-md transition-colors ${
                    p === page
                      ? 'bg-primary text-white'
                      : 'text-text-secondary hover:bg-neutral-100'
                  }`}
                >
                  {p + 1}
                </button>
              )
            })}
            <button
              type="button"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              className="px-3 py-1.5 text-xs font-medium rounded-md text-text-secondary hover:bg-neutral-100 disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
