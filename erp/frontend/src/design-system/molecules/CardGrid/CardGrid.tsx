import type { ReactNode } from 'react'
import { EmptyState } from '../../molecules/EmptyState/EmptyState'
import { Skeleton } from '../../atoms/Skeleton/Skeleton'

export interface CardGridProps<T> {
  items: T[]
  renderCard: (item: T, index: number) => ReactNode
  keyExtractor: (item: T) => string
  loading?: boolean
  emptyTitle?: string
  emptyDescription?: string
  minWidth?: string
  className?: string
}

export function CardGrid<T>({
  items,
  renderCard,
  keyExtractor,
  loading = false,
  emptyTitle = 'No data',
  emptyDescription,
  minWidth = '320px',
  className = '',
}: CardGridProps<T>) {
  if (loading) {
    return (
      <div
        className={`grid gap-4 ${className}`}
        style={{ gridTemplateColumns: `repeat(auto-fill, minmax(${minWidth}, 1fr))` }}
      >
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} variant="card" />
        ))}
      </div>
    )
  }

  if (items.length === 0) {
    return <EmptyState title={emptyTitle} description={emptyDescription} />
  }

  return (
    <div
      className={`grid gap-4 ${className}`}
      style={{ gridTemplateColumns: `repeat(auto-fill, minmax(${minWidth}, 1fr))` }}
    >
      {items.map((item, index) => (
        <div key={keyExtractor(item)} className="animate-slide-up" style={{ animationDelay: `${index * 50}ms` }}>
          {renderCard(item, index)}
        </div>
      ))}
    </div>
  )
}
