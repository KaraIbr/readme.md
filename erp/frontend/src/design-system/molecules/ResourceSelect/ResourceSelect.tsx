import { useState, useRef, useEffect, useMemo, useCallback } from 'react'
import { FormField } from '../FormField/FormField'

export interface ResourceOption {
  id: number
  label: string
  subtitle?: string
}

interface ResourceSelectProps {
  value: number | null | undefined
  onChange: (value: number | null) => void
  options: ResourceOption[]
  label: string
  error?: string
  placeholder?: string
  loading?: boolean
  clearable?: boolean
}

export function ResourceSelect({
  value,
  onChange,
  options,
  label,
  error,
  placeholder = 'Search...',
  loading = false,
  clearable = true,
}: ResourceSelectProps) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const selected = useMemo(
    () => options.find((o) => o.id === value) ?? null,
    [options, value],
  )

  const filtered = useMemo(() => {
    if (!query.trim()) return options
    const q = query.toLowerCase()
    return options.filter(
      (o) =>
        o.label.toLowerCase().includes(q) ||
        (o.subtitle && o.subtitle.toLowerCase().includes(q)),
    )
  }, [options, query])

  const handleSelect = useCallback(
    (option: ResourceOption) => {
      onChange(option.id)
      setQuery('')
      setOpen(false)
    },
    [onChange],
  )

  const handleClear = useCallback(() => {
    onChange(null)
    setQuery('')
    inputRef.current?.focus()
  }, [onChange])

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false)
        setQuery('')
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <FormField label={label} error={error}>
      <div ref={containerRef} className="relative">
        {selected && !open ? (
          <div
            onClick={() => {
              setOpen(true)
              inputRef.current?.focus()
            }}
            className="flex items-center justify-between w-full rounded-lg border border-border bg-white px-3 py-2 text-sm cursor-pointer hover:border-neutral-300 transition-colors"
          >
            <div className="flex items-center gap-2 min-w-0">
              <span className="font-medium truncate">{selected.label}</span>
              {selected.subtitle && (
                <span className="text-text-tertiary text-xs truncate shrink-0">
                  {selected.subtitle}
                </span>
              )}
            </div>
            {clearable && (
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  handleClear()
                }}
                className="text-text-tertiary hover:text-text shrink-0 ml-2"
              >
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M1 1L13 13M13 1L1 13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </button>
            )}
          </div>
        ) : (
          <div className="relative">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setOpen(true)}
              placeholder={selected ? selected.label : placeholder}
              className="w-full rounded-lg border border-border bg-white px-3 py-2 text-sm placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            />
            {loading && (
              <div className="absolute right-3 top-1/2 -translate-y-1/2">
                <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>
        )}

        {open && (
          <div className="absolute z-50 mt-1 w-full bg-white border border-border rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {filtered.length === 0 ? (
              <div className="px-3 py-2 text-sm text-text-tertiary">
                {loading ? 'Loading...' : 'No results found'}
              </div>
            ) : (
              filtered.map((option) => (
                <button
                  key={option.id}
                  type="button"
                  onClick={() => handleSelect(option)}
                  className={`w-full text-left px-3 py-2 text-sm hover:bg-neutral-50 transition-colors flex items-center justify-between gap-2 ${
                    option.id === value ? 'bg-primary/5 font-medium' : ''
                  }`}
                >
                  <span className="truncate">{option.label}</span>
                  {option.subtitle && (
                    <span className="text-text-tertiary text-xs shrink-0">
                      {option.subtitle}
                    </span>
                  )}
                </button>
              ))
            )}
          </div>
        )}
      </div>
    </FormField>
  )
}
