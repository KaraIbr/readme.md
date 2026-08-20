import { useState, useEffect, useRef, useMemo } from 'react'
import { SearchInput } from '../../molecules/SearchInput/SearchInput'
import { Button } from '../../atoms/Button/Button'

export interface FilterField {
  key: string
  label: string
  type: 'text' | 'select' | 'multi' | 'date'
  placeholder?: string
  options?: { label: string; value: string }[]
}

interface AdvancedFilterProps {
  fields: FilterField[]
  values: Record<string, string>
  onChange: (key: string, value: string) => void
  onClear: () => void
  debounceMs?: number
}

const selectClass = 'h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 min-w-[160px] transition-shadow'
const dateClass = 'h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 transition-shadow'

function ActiveFilterChip({ label, value, onRemove }: { label: string; value: string; onRemove: () => void }) {
  if (!value) return null
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary-soft text-primary text-xs font-medium animate-scale-in">
      {label}: {value}
      <button type="button" onClick={onRemove} className="hover:text-primary/70 transition-colors">
        <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
        </svg>
      </button>
    </span>
  )
}

function MultiSelect({
  options,
  value,
  onChange,
  placeholder,
}: {
  options: { label: string; value: string }[]
  value: string
  onChange: (val: string) => void
  placeholder?: string
}) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const selected = value ? value.split(',') : []

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const toggle = (val: string) => {
    const next = selected.includes(val) ? selected.filter((s) => s !== val) : [...selected, val]
    onChange(next.join(','))
  }

  return (
    <div ref={ref} className="relative min-w-[160px]">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className={`${selectClass} w-full flex items-center justify-between gap-2`}
      >
        <span className={selected.length === 0 ? 'text-text-tertiary' : 'text-text'}>
          {selected.length > 0 ? `${selected.length} selected` : (placeholder ?? 'Select...')}
        </span>
        <svg className={`w-3.5 h-3.5 text-text-tertiary transition-transform ${open ? 'rotate-180' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="6 9 12 15 18 9" />
        </svg>
      </button>
      {open && (
        <div className="absolute top-full mt-1 left-0 right-0 bg-white border border-border rounded-lg shadow-elevated z-20 py-1 max-h-48 overflow-y-auto">
          {options.map((opt) => {
            const isSelected = selected.includes(opt.value)
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => toggle(opt.value)}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-sm hover:bg-neutral-50 transition-colors"
              >
                <span className={`size-4 rounded border-2 flex items-center justify-center transition-colors ${
                  isSelected ? 'bg-primary border-primary' : 'border-neutral-300'
                }`}>
                  {isSelected && (
                    <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                  )}
                </span>
                <span>{opt.label}</span>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

export function AdvancedFilter({
  fields,
  values,
  onChange,
  onClear,
  debounceMs = 300,
}: AdvancedFilterProps) {
  const activeCount = Object.values(values).filter(Boolean).length
  const debounceTimers = useRef<Record<string, ReturnType<typeof setTimeout>>>({})

  const debouncedOnChange = (key: string, value: string) => {
    if (debounceTimers.current[key]) {
      clearTimeout(debounceTimers.current[key])
    }
    debounceTimers.current[key] = setTimeout(() => {
      onChange(key, value)
    }, debounceMs)
  }

  useEffect(() => {
    const timers = debounceTimers.current
    return () => {
      Object.values(timers).forEach(clearTimeout)
    }
  }, [])

  const textFields = useMemo(() => fields.filter((f) => f.type === 'text'), [fields])
  const otherFields = useMemo(() => fields.filter((f) => f.type !== 'text'), [fields])

  return (
    <div className="space-y-3">
      {activeCount > 0 && (
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-xs font-medium text-text-tertiary">Active filters:</span>
          {fields.map((field) => {
            const v = values[field.key]
            if (!v) return null
            const opt = field.options?.find((o) => o.value === v)
            return (
              <ActiveFilterChip
                key={field.key}
                label={field.label}
                value={opt?.label ?? v}
                onRemove={() => onChange(field.key, '')}
              />
            )
          })}
          <Button variant="ghost" size="sm" onClick={onClear}>
            Clear all
          </Button>
        </div>
      )}
      <div className="flex items-center gap-3 flex-wrap">
        {textFields.map((field) => (
          <div key={field.key} className="min-w-[200px] flex-1 max-w-xs">
            <SearchInput
              value={values[field.key] ?? ''}
              onChange={(e) => {
                const v = e.target.value
                debouncedOnChange(field.key, v)
                if (!v) onChange(field.key, '')
              }}
              onClear={() => onChange(field.key, '')}
              placeholder={field.placeholder ?? `Search ${field.label.toLowerCase()}...`}
            />
          </div>
        ))}
        {otherFields.map((field) => {
          if (field.type === 'select') {
            return (
              <select
                key={field.key}
                className={selectClass}
                value={values[field.key] ?? ''}
                onChange={(e) => onChange(field.key, e.target.value)}
              >
                <option value="">{field.placeholder ?? `All ${field.label}`}</option>
                {field.options?.map((opt) => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            )
          }
          if (field.type === 'multi') {
            return (
              <MultiSelect
                key={field.key}
                options={field.options ?? []}
                value={values[field.key] ?? ''}
                onChange={(val) => onChange(field.key, val)}
                placeholder={field.placeholder}
              />
            )
          }
          if (field.type === 'date') {
            return (
              <input
                key={field.key}
                type="date"
                className={dateClass}
                value={values[field.key] ?? ''}
                onChange={(e) => onChange(field.key, e.target.value)}
                placeholder={field.placeholder}
              />
            )
          }
          return null
        })}
      </div>
    </div>
  )
}
