import { Badge } from '../../atoms/Badge/Badge'
import type { BadgeVariant } from '../../atoms/Badge/Badge'

export type StatusType = 'active' | 'pending' | 'completed' | 'cancelled' | 'draft'

export interface StatusBadgeProps {
  status: StatusType
  className?: string
}

const statusConfig: Record<StatusType, { label: string; variant: BadgeVariant }> = {
  active:    { label: 'Active',    variant: 'success' },
  pending:   { label: 'Pending',   variant: 'warning' },
  completed: { label: 'Completed', variant: 'info' },
  cancelled: { label: 'Cancelled', variant: 'danger' },
  draft:     { label: 'Draft',     variant: 'default' },
}

export function StatusBadge({ status, className = '' }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <Badge variant={config.variant} size="sm" className={className}>
      <span className="flex items-center gap-1.5">
        <span className={`size-1.5 rounded-full ${dotColors[config.variant]}`} />
        {config.label}
      </span>
    </Badge>
  )
}

const dotColors: Record<BadgeVariant, string> = {
  default: 'bg-text-tertiary',
  success: 'bg-primary',
  warning: 'bg-warning',
  danger: 'bg-danger',
  info: 'bg-info',
}
