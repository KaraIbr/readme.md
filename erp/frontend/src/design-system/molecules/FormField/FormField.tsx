import type { ReactNode } from 'react'

export interface FormFieldProps {
  label?: string
  error?: string
  hint?: string
  required?: boolean
  children: ReactNode
  className?: string
}

export function FormField({
  label,
  error,
  hint,
  required = false,
  children,
  className = '',
}: FormFieldProps) {
  return (
    <div className={`flex flex-col gap-1.5 ${className}`}>
      {label && (
        <label className="text-sm font-medium text-text">
          {label}
          {required && <span className="text-danger ml-0.5">*</span>}
        </label>
      )}
      {children}
      {error && (
        <p className="text-xs text-danger mt-0.5">{error}</p>
      )}
      {hint && !error && (
        <p className="text-xs text-text-tertiary mt-0.5">{hint}</p>
      )}
    </div>
  )
}
