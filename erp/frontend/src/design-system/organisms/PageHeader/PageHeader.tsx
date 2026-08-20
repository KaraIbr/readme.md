import type { ReactNode } from 'react'

export interface PageHeaderProps {
  title: string
  description?: ReactNode
  actions?: ReactNode
  viewToggle?: ReactNode
  accent?: boolean
  className?: string
}

export function PageHeader({
  title,
  description,
  actions,
  viewToggle,
  accent = true,
  className = '',
}: PageHeaderProps) {
  return (
    <div className={`px-6 pt-6 pb-4 ${className}`}>
      {accent && (
        <div className="h-1 w-16 bg-primary-gradient rounded-full mb-4" />
      )}
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <h1 className="text-h3 text-text">{title}</h1>
          {description && (
            <p className="text-body text-text-secondary mt-1">{description}</p>
          )}
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          {viewToggle}
          {actions}
        </div>
      </div>
    </div>
  )
}
