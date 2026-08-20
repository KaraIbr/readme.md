import { forwardRef } from 'react'
import { Spinner } from '../Spinner/Spinner'
import type { ButtonHTMLAttributes, ReactNode } from 'react'

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'glass'
type ButtonSize = 'sm' | 'md' | 'lg'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  loading?: boolean
  icon?: ReactNode
  iconPosition?: 'left' | 'right'
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    'bg-primary text-white hover:bg-primary-hover active:bg-primary-hover shadow-subtle',
  secondary:
    'bg-white text-text border border-border hover:bg-neutral-50 active:bg-neutral-100 shadow-subtle',
  ghost:
    'bg-transparent text-text-secondary hover:bg-neutral-100 active:bg-neutral-200',
  danger:
    'bg-danger text-white hover:bg-danger-hover active:bg-danger-hover shadow-subtle',
  glass:
    'glass text-text hover:bg-white/90 active:bg-white/80 shadow-subtle',
}

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'h-8 px-4 text-sm gap-1.5',
  md: 'h-10 px-5 text-base gap-2',
  lg: 'h-12 px-6 text-md gap-2',
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      disabled,
      icon,
      iconPosition = 'left',
      children,
      className = '',
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || loading

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={`
          inline-flex items-center justify-center rounded-lg font-medium
          transition-all duration-150 ease-in-out
          focus:outline-none focus:ring-2 focus:ring-primary/30
          disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${className}
        `.trim()}
        {...props}
      >
        {loading ? (
          <Spinner size="sm" />
        ) : icon && iconPosition === 'left' ? (
          <span className="flex-shrink-0 size-4 group-hover:translate-x-0.5 transition-transform">{icon}</span>
        ) : null}
        {children && <span>{children}</span>}
        {!loading && icon && iconPosition === 'right' ? (
          <span className="flex-shrink-0 size-4 group-hover:translate-x-0.5 transition-transform">{icon}</span>
        ) : null}
      </button>
    )
  },
)

Button.displayName = 'Button'
