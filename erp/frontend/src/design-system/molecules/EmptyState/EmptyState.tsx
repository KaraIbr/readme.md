import type { ReactNode } from 'react'

export interface EmptyStateProps {
  icon?: ReactNode
  title: string
  description?: string
  action?: ReactNode
  variant?: 'default' | 'ghost'
  className?: string
}

export function EmptyState({
  icon,
  title,
  description,
  action,
  variant = 'default',
  className = '',
}: EmptyStateProps) {
  return (
    <div
      className={`
        flex flex-col items-center justify-center py-16 px-8 text-center
        ${variant === 'ghost' ? 'bg-transparent' : 'bg-white rounded-xl border border-dashed border-neutral-200'}
        ${className}
      `.trim()}
    >
      {icon ? (
        <div className="mb-5 text-text-tertiary [&_svg]:size-12">{icon}</div>
      ) : (
        <div className="mb-5 text-text-tertiary">
          <svg className="size-12 mx-auto" viewBox="0 0 48 48" fill="none">
            <rect x="8" y="12" width="32" height="28" rx="4" stroke="currentColor" strokeWidth="2" strokeDasharray="4 3" />
            <line x1="16" y1="22" x2="32" y2="22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <line x1="16" y1="28" x2="28" y2="28" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <line x1="16" y1="34" x2="24" y2="34" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
          </svg>
        </div>
      )}
      <h3 className="text-h5 text-text mb-1.5">{title}</h3>
      {description && (
        <p className="text-body text-text-secondary max-w-sm">{description}</p>
      )}
      {action && <div className="mt-5">{action}</div>}
    </div>
  )
}
