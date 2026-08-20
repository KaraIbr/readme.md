import type { ReactNode } from 'react'

interface FilterBarProps {
  children: ReactNode
  className?: string
}

export function FilterBar({ children, className = '' }: FilterBarProps) {
  return (
    <div
      className={`
        flex items-center gap-3 flex-wrap px-6 py-4 bg-white border-b border-border
        ${className}
      `.trim()}
    >
      {children}
    </div>
  )
}
