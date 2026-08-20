import { forwardRef, useState } from 'react'
import type { InputHTMLAttributes, ReactNode } from 'react'

type InputSize = 'sm' | 'md' | 'lg'

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  inputSize?: InputSize
  label?: string
  error?: string | boolean
  leftElement?: ReactNode
  rightElement?: ReactNode
}

const sizeStyles: Record<InputSize, string> = {
  sm: 'h-8 px-3 text-sm',
  md: 'h-10 px-3.5 text-sm',
  lg: 'h-12 px-4 text-base',
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  (
    {
      inputSize = 'md',
      label,
      error,
      leftElement,
      rightElement,
      className = '',
      ...props
    },
    ref,
  ) => {
    const [focused, setFocused] = useState(false)

    return (
      <div className="w-full">
        {label && (
          <label className="block text-sm font-medium text-text-secondary mb-1.5">
            {label}
          </label>
        )}
        <div
          className={`
            relative flex items-center rounded-lg border bg-white w-full
            transition-all duration-150
            ${error
              ? 'border-danger animate-shake'
              : focused
                ? 'border-primary ring-2 ring-primary/20'
                : 'border-border hover:border-neutral-300'
            }
          `.trim()}
        >
          {leftElement && (
            <span className="flex-shrink-0 pl-3 text-text-tertiary">{leftElement}</span>
          )}
          <input
            ref={ref}
            onFocus={(e) => { setFocused(true); props.onFocus?.(e) }}
            onBlur={(e) => { setFocused(false); props.onBlur?.(e) }}
            className={`
              w-full bg-transparent text-text placeholder:text-text-tertiary
              focus:outline-none
              ${sizeStyles[inputSize]}
              ${leftElement ? 'pl-2' : ''}
              ${rightElement ? 'pr-2' : ''}
              ${className}
            `.trim()}
            {...props}
          />
          {rightElement && (
            <span className="flex-shrink-0 pr-3 text-text-tertiary">{rightElement}</span>
          )}
        </div>
        {error && (
          <p className="mt-1 text-xs text-danger">{error}</p>
        )}
      </div>
    )
  },
)

Input.displayName = 'Input'
