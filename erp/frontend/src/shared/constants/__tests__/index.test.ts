import { describe, it, expect } from 'vitest'
import { APP_NAME, PAGINATION, DATE_FORMAT } from '../index'

describe('shared constants', () => {
  it('exposes the app name', () => {
    expect(APP_NAME).toBe('VERP CRM')
  })

  it('exposes pagination defaults', () => {
    expect(PAGINATION.defaultPageSize).toBe(20)
    expect(PAGINATION.pageSizeOptions).toEqual([10, 20, 50, 100])
  })

  it('exposes date formats', () => {
    expect(DATE_FORMAT.display).toBe('MMM d, yyyy')
    expect(DATE_FORMAT.api).toBe("yyyy-MM-dd'T'HH:mm:ss.SSS'Z'")
    expect(DATE_FORMAT.short).toBe('MM/dd/yyyy')
  })
})
