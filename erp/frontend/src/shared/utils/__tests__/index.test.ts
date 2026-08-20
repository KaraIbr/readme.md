import { describe, it, expect } from 'vitest'
import { cn, formatCurrency, formatDate, pluralize, truncate } from '../index'

describe('cn', () => {
  it('joins truthy class names', () => {
    expect(cn('a', 'b', 'c')).toBe('a b c')
  })

  it('filters out falsy values', () => {
    expect(cn('a', false, undefined, null, 'b')).toBe('a b')
  })

  it('returns empty string when nothing is truthy', () => {
    expect(cn(false, undefined)).toBe('')
  })
})

describe('formatCurrency', () => {
  it('formats BRL values in pt-BR locale', () => {
    const result = formatCurrency(1234.5)
    expect(result).toContain('R$')
    expect(result).toContain('1.234,50')
  })

  it('supports a custom currency', () => {
    const result = formatCurrency(100, 'USD')
    expect(result).toContain('US$')
  })
})

describe('formatDate', () => {
  it('formats a string date using pt-BR locale with custom options', () => {
    const input = '2026-01-15T12:00:00Z'
    const options: Intl.DateTimeFormatOptions = {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }
    const result = formatDate(input, options)
    const expected = new Date(input).toLocaleDateString('pt-BR', options)
    expect(result).toBe(expected)
  })

  it('accepts a Date instance', () => {
    const result = formatDate(new Date(2026, 0, 15), {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    })
    expect(result).toBe('15/01/2026')
  })
})

describe('pluralize', () => {
  it('returns singular for count of one', () => {
    expect(pluralize(1, 'lead')).toBe('lead')
  })

  it('defaults to appending s for plural', () => {
    expect(pluralize(2, 'lead')).toBe('leads')
  })

  it('uses custom plural when provided', () => {
    expect(pluralize(5, 'person', 'people')).toBe('people')
  })
})

describe('truncate', () => {
  it('returns the string when shorter than the limit', () => {
    expect(truncate('hello', 10)).toBe('hello')
  })

  it('truncates and appends ellipsis when longer than the limit', () => {
    expect(truncate('hello world', 5)).toBe('hello...')
  })
})
