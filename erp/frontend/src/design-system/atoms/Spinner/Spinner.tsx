export type SpinnerSize = 'sm' | 'md' | 'lg'

export interface SpinnerProps {
  size?: SpinnerSize
  variant?: 'default' | 'gradient' | 'overlay'
  className?: string
}

const sizeMap: Record<SpinnerSize, string> = {
  sm: 'size-4 border-2',
  md: 'size-5 border-2',
  lg: 'size-8 border-[3px]',
}

export function Spinner({ size = 'md', variant = 'default', className = '' }: SpinnerProps) {
  if (variant === 'overlay') {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-backdrop">
        <div
          className={`animate-spin rounded-full border-white/30 border-t-white ${sizeMap[size]} ${className}`}
          role="status"
          aria-label="Loading"
        />
      </div>
    )
  }

  if (variant === 'gradient') {
    return (
      <div
        className={`
          animate-spin rounded-full
          border-2 border-transparent
          border-t-primary border-r-primary
          ${sizeMap[size]}
          ${className}
        `.trim()}
        role="status"
        aria-label="Loading"
      />
    )
  }

  return (
    <div
      className={`
        animate-spin rounded-full border-primary/20 border-t-primary
        ${sizeMap[size]}
        ${className}
      `.trim()}
      role="status"
      aria-label="Loading"
    />
  )
}
