import { Badge } from '@atoms/Badge/Badge'
import type { TechnicalVisitRead } from '../types'
import { STATUS_LABELS, STATUS_VARIANTS } from '../types'

const statusBorderColors: Record<string, string> = {
  REQUESTED: 'border-l-warning',
  SCHEDULED: 'border-l-info',
  COMPLETED: 'border-l-success',
  CANCELLED: 'border-l-danger',
}

interface VisitCardProps {
  visit: TechnicalVisitRead
  onClick?: (id: number) => void
  className?: string
}

export function VisitCard({ visit, onClick, className = '' }: VisitCardProps) {
  const Component = onClick ? 'button' : 'div'

  return (
    <Component
      type={onClick ? 'button' : undefined}
      onClick={onClick ? () => onClick(visit.id) : undefined}
      className={`
        w-full text-left p-4 rounded-xl border border-border border-l-[3px] ${statusBorderColors[visit.status] ?? 'border-l-neutral-300'}
        bg-white shadow-subtle
        ${onClick ? 'hover:shadow-elevated hover:bg-neutral-25 transition-all duration-200 cursor-pointer' : ''}
        ${className}
      `.trim()}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-semibold text-text">Visit #{visit.id}</span>
            <Badge variant={STATUS_VARIANTS[visit.status]} size="sm">{STATUS_LABELS[visit.status]}</Badge>
          </div>
          {visit.receiver_name && (
            <div className="flex items-center gap-1.5 mt-1.5">
              <svg className="w-3 h-3 text-text-tertiary shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
              <span className="text-xs text-text-secondary truncate">{visit.receiver_name}</span>
            </div>
          )}
          {visit.scheduled_at && (
            <div className="flex items-center gap-1.5 mt-1">
              <svg className="w-3 h-3 text-text-tertiary shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
              </svg>
              <span className="text-xs text-text-tertiary">
                {new Date(visit.scheduled_at).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          )}
        </div>
      </div>
      {visit.notes && (
        <p className="text-xs text-text-tertiary mt-2 line-clamp-2 leading-relaxed">{visit.notes}</p>
      )}
    </Component>
  )
}
