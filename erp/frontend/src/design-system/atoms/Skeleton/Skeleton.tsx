export type SkeletonVariant = 'text' | 'card' | 'table-row' | 'avatar' | 'custom'

export interface SkeletonProps {
  variant?: SkeletonVariant
  lines?: number
  className?: string
}

const base = 'animate-shimmer rounded-lg bg-gradient-to-r from-neutral-100 via-neutral-200 to-neutral-100'

const variantStyles: Record<SkeletonVariant, string> = {
  'text': 'h-4 w-full',
  'card': 'h-48 w-full rounded-xl',
  'table-row': 'h-12 w-full',
  'avatar': 'size-10 rounded-full',
  'custom': '',
}

export function Skeleton({ variant = 'text', lines = 1, className = '' }: SkeletonProps) {
  if (variant === 'text') {
    return (
      <div className="space-y-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className={`${base} ${variantStyles.text}`}
            style={{ width: i === lines - 1 && lines > 1 ? '60%' : '100%' }}
          />
        ))}
      </div>
    )
  }

  return (
    <div
      className={`
        ${base}
        ${variantStyles[variant]}
        ${className}
      `.trim()}
    />
  )
}
