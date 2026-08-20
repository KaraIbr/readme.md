import { forwardRef, useId } from 'react'
import type { InputHTMLAttributes, ReactNode } from 'react'

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: ReactNode
  indeterminate?: boolean
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ label, indeterminate = false, disabled, className = '', id, ...props }, ref) => {
    const generatedId = useId()
    const checkboxId = id ?? generatedId

    return (
      <label
        htmlFor={checkboxId}
        className={`
          inline-flex items-center gap-3 cursor-pointer
          ${disabled ? 'cursor-not-allowed opacity-50' : ''}
          ${className}
        `.trim()}
      >
        <div className="relative size-5 flex-shrink-0">
          <input
            ref={ref}
            id={checkboxId}
            type="checkbox"
            disabled={disabled}
            className="peer absolute inset-0 opacity-0 cursor-pointer"
            {...props}
          />
          <div
            className={`
              size-5 rounded-md border-2 flex items-center justify-center
              transition-all duration-150 ease-in-out
              peer-focus-visible:ring-2 peer-focus-visible:ring-primary/30
              peer-checked:bg-primary peer-checked:border-primary
              ${indeterminate ? 'bg-primary border-primary' : 'border-border bg-white'}
              ${disabled ? 'bg-neutral-50 border-neutral-200' : 'hover:border-primary'}
            `.trim()}
          >
            {indeterminate ? (
              <svg width="10" height="2" viewBox="0 0 10 2" fill="none">
                <rect width="10" height="2" rx="1" fill="white" />
              </svg>
            ) : (
              <svg
                width="12"
                height="10"
                viewBox="0 0 12 10"
                fill="none"
                className="opacity-0 peer-checked:opacity-100 transition-opacity duration-150"
              >
                <path
                  d="M1 5L4.5 8.5L11 1.5"
                  stroke="white"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </div>
        </div>
        {label && (
          <span className="text-base text-text select-none">{label}</span>
        )}
      </label>
    )
  },
)

Checkbox.displayName = 'Checkbox'
