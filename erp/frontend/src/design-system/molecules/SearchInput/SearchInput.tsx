import { forwardRef } from 'react'
import { Input } from '../../atoms/Input/Input'
import type { InputProps } from '../../atoms/Input/Input'

interface SearchInputProps extends Omit<InputProps, 'leftElement' | 'rightElement'> {
  onClear?: () => void
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
  ({ onClear, value, ...props }, ref) => {
    return (
      <Input
        ref={ref}
        value={value}
        placeholder="Search..."
        leftElement={
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <circle cx="7" cy="7" r="5.5" stroke="currentColor" strokeWidth="1.5" />
            <path d="M11 11L14.5 14.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
          </svg>
        }
        rightElement={
          value && onClear ? (
            <button
              type="button"
              onClick={onClear}
              className="text-text-tertiary hover:text-text transition-colors"
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
              </svg>
            </button>
          ) : undefined
        }
        {...props}
      />
    )
  },
)

SearchInput.displayName = 'SearchInput'
