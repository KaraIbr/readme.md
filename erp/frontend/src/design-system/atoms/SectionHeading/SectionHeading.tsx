import type { ReactNode } from 'react'

interface SectionHeadingProps {
  children: ReactNode
  className?: string
}

export function SectionHeading({ children, className = '' }: SectionHeadingProps) {
  return (
    <div className={`flex items-center gap-3 pt-6 pb-4 first:pt-0 ${className}`}>
      <h3 className="text-sm font-semibold text-text uppercase tracking-wider">{children}</h3>
      <div className="flex-1 h-px bg-border-light" />
    </div>
  )
}
