import { useState, useRef, useEffect } from 'react'

interface UserOverflowMenuProps {
  onEdit: () => void
  onDeactivate: () => void
  onDelete: () => void
  isActive: boolean
}

function DotsIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="3" r="1.5" fill="currentColor" />
      <circle cx="8" cy="8" r="1.5" fill="currentColor" />
      <circle cx="8" cy="13" r="1.5" fill="currentColor" />
    </svg>
  )
}

export function UserOverflowMenu({ onEdit, onDeactivate, onDelete, isActive }: UserOverflowMenuProps) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!open) return
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [open])

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="size-8 flex items-center justify-center rounded-lg text-text-tertiary hover:bg-neutral-100 hover:text-text transition-colors"
        aria-label="More actions"
      >
        <DotsIcon />
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-1 w-44 bg-white rounded-xl border border-border shadow-lg z-40 py-1">
          <button
            type="button"
            onClick={() => { onEdit(); setOpen(false) }}
            className="w-full text-left px-4 py-2.5 text-sm text-text hover:bg-neutral-50 flex items-center gap-2.5"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="text-text-tertiary">
              <path d="M10.5 1.5L12.5 3.5L4 12H2V10L10.5 1.5Z" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Edit
          </button>
          <button
            type="button"
            onClick={() => { onDeactivate(); setOpen(false) }}
            className="w-full text-left px-4 py-2.5 text-sm hover:bg-neutral-50 flex items-center gap-2.5"
          >
            {isActive ? (
              <>
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="text-warning">
                  <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.2" />
                  <path d="M7 4.5V7.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
                  <circle cx="7" cy="9.5" r="0.5" fill="currentColor" />
                </svg>
                <span className="text-warning">Deactivate</span>
              </>
            ) : (
              <>
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="text-success">
                  <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.2" />
                  <path d="M5 7L6.5 8.5L9 5.5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <span className="text-success">Activate</span>
              </>
            )}
          </button>
          <div className="my-1 border-t border-border" />
          <button
            type="button"
            onClick={() => { onDelete(); setOpen(false) }}
            className="w-full text-left px-4 py-2.5 text-sm text-danger hover:bg-danger-soft flex items-center gap-2.5"
          >
            <svg width="14" height="14" viewBox="0 0 14 14" fill="none" className="text-danger">
              <path d="M2 4H12M5 4V2.5C5 2.2 5.2 2 5.5 2H8.5C8.8 2 9 2.2 9 2.5V4M11 4V11.5C11 11.8 10.8 12 10.5 12H3.5C3.2 12 3 11.8 3 11.5V4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Delete
          </button>
        </div>
      )}
    </div>
  )
}
