import type { ReactNode } from 'react'

export interface TopbarProps {
  left?: ReactNode
  center?: ReactNode
  right?: ReactNode
  className?: string
}

export function Topbar({ left, center, right, className = '' }: TopbarProps) {
  return (
    <header
      className={`
        h-16 px-6 glass border-b border-border/50 flex items-center justify-between
        ${className}
      `.trim()}
    >
      <div className="flex items-center gap-4">{left}</div>
      <div className="flex-1 flex justify-center">{center}</div>
      <div className="flex items-center gap-3">{right}</div>
    </header>
  )
}
