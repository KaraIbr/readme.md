import { useCallback, useEffect, useRef, useState, type ReactNode } from 'react'
import { createPortal } from 'react-dom'
import { Button } from '@atoms/Button/Button'

export interface DrawerProps {
  open: boolean
  onClose: () => void
  title: string
  subtitle?: string
  children: ReactNode
  editable?: boolean
  cancelLabel?: string
  actionLabel?: string
  onAction?: () => void
  actionLoading?: boolean
  actionDisabled?: boolean
  width?: string
  className?: string
}

function CloseIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
      <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

export function Drawer({
  open,
  onClose,
  title,
  subtitle,
  children,
  editable = false,
  cancelLabel = 'Cancel',
  actionLabel = 'Save',
  onAction,
  actionLoading = false,
  actionDisabled = false,
  width,
  className = '',
}: DrawerProps) {
  const [mounted, setMounted] = useState(false)
  const [visible, setVisible] = useState(false)
  const closeBtnRef = useRef<HTMLButtonElement>(null)
  const panelRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const raf = requestAnimationFrame(() => {
      if (open) {
        setMounted(true)
        requestAnimationFrame(() => setVisible(true))
      } else {
        setVisible(false)
      }
    })
    return () => cancelAnimationFrame(raf)
  }, [open])

  useEffect(() => {
    if (visible) {
      document.body.style.overflow = 'hidden'
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [visible])

  const handleTransitionEnd = useCallback(
    (e: React.TransitionEvent) => {
      if (e.target === panelRef.current && !visible) {
        setMounted(false)
      }
    },
    [visible],
  )

  useEffect(() => {
    if (!mounted) return
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [mounted, onClose])

  useEffect(() => {
    if (visible) closeBtnRef.current?.focus()
  }, [visible])

  if (!mounted) return null

  return createPortal(
    <div className="fixed inset-0 z-50 flex justify-end">
      <div
        className={`absolute inset-0 transition-opacity duration-200 ${visible ? 'opacity-100' : 'opacity-0'}`}
        style={{ backgroundColor: 'rgba(0, 0, 0, 0.4)' }}
        onClick={onClose}
      />
      <div
        ref={panelRef}
        onTransitionEnd={handleTransitionEnd}
        className={`
          relative h-full bg-surface shadow-modal overflow-hidden flex flex-col
          transition-transform duration-200
          ${visible ? 'translate-x-0' : 'translate-x-full'}
          ${width ?? 'w-full sm:max-w-2xl'}
          rounded-l-xl
          ${className}
        `.trim()}
        style={{ transitionTimingFunction: 'cubic-bezier(0.32, 0.72, 0, 1)' }}
      >
        <div className="flex items-start justify-between gap-4 px-6 py-5 border-b border-border min-h-[72px]">
          <div className="min-w-0">
            <h2 className="text-h6 text-text truncate">{title}</h2>
            {subtitle && (
              <p className="text-small text-text-secondary mt-0.5 truncate">{subtitle}</p>
            )}
          </div>
          <button
            ref={closeBtnRef}
            type="button"
            onClick={onClose}
            className="size-8 flex items-center justify-center rounded-lg text-text-tertiary hover:bg-neutral-100 hover:text-text transition-colors shrink-0"
            aria-label="Close"
          >
            <CloseIcon />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-6 [&>*:first-child]:mt-0">
          {children}
        </div>

        {editable && (
          <div className="flex items-center justify-end gap-3 px-6 py-4 border-t border-border bg-surface min-h-[68px]">
            <Button variant="secondary" size="md" onClick={onClose} disabled={actionLoading}>
              {cancelLabel}
            </Button>
            <Button
              variant="primary"
              size="md"
              onClick={onAction}
              loading={actionLoading}
              disabled={actionDisabled}
            >
              {actionLabel}
            </Button>
          </div>
        )}
      </div>
    </div>,
    document.body,
  )
}
