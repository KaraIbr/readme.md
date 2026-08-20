import type { ReactNode, HTMLAttributes } from 'react'

type CardVariant = 'elevated' | 'bordered' | 'glass' | 'interactive'

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  variant?: CardVariant
  padding?: 'none' | 'sm' | 'md' | 'lg'
  header?: ReactNode
  footer?: ReactNode
  children: ReactNode
}

const variantStyles: Record<CardVariant, string> = {
  elevated:
    'bg-white shadow-elevation-1',
  bordered:
    'bg-white border border-border',
  glass:
    'glass shadow-elevation-1',
  interactive:
    'bg-white border border-border hover:shadow-elevation-2 hover:-translate-y-0.5 cursor-pointer transition-all duration-200',
}

const paddingStyles: Record<string, string> = {
  none: '',
  sm: 'p-4',
  md: 'p-5',
  lg: 'p-6',
}

export function Card({
  variant = 'bordered',
  padding = 'md',
  header,
  footer,
  children,
  className = '',
  ...props
}: CardProps) {
  return (
    <div
      className={`
        rounded-xl
        ${variantStyles[variant]}
        ${className}
      `.trim()}
      {...props}
    >
      {header && (
        <div className="px-5 py-4 border-b border-border-light">
          {header}
        </div>
      )}
      {children && (
        <div className={paddingStyles[padding]}>
          {children}
        </div>
      )}
      {footer && (
        <div className="px-5 py-4 border-t border-border-light">
          {footer}
        </div>
      )}
    </div>
  )
}
