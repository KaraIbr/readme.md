import type { ReactNode } from 'react'

export type BadgeVariant = 'default' | 'success' | 'warning' | 'danger' | 'info'
export type BadgeSize = 'sm' | 'md'

export interface BadgeProps {
  variant?: BadgeVariant
  size?: BadgeSize
  children?: ReactNode
  pulse?: boolean
  dot?: boolean
  className?: string
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-neutral-100 text-text-secondary',
  success: 'bg-primary-soft text-primary',
  warning: 'bg-warning-soft text-warning',
  danger: 'bg-danger-soft text-danger',
  info: 'bg-info-soft text-info',
}

const sizeStyles: Record<BadgeSize, string> = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-2.5 py-1 text-sm',
}

export function Badge({
  variant = 'default',
  size = 'md',
  children,
  pulse = false,
  dot = false,
  className = '',
}: BadgeProps) {
  const dotColors: Record<BadgeVariant, string> = {
    default: 'bg-text-tertiary',
    success: 'bg-success',
    warning: 'bg-warning',
    danger: 'bg-danger',
    info: 'bg-info',
  }

  if (dot) {
    return (
      <span
        className={`status-dot ${dotColors[variant]} ${pulse ? 'animate-pulse-dot' : ''} ${className}`}
      />
    )
  }

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 font-medium rounded-full
        ${variantStyles[variant]}
        ${sizeStyles[size]}
        ${className}
      `.trim()}
    >
      {pulse && (
        <span className={`status-dot ${dotColors[variant]} animate-pulse-dot`} />
      )}
      {children}
    </span>
  )
}
