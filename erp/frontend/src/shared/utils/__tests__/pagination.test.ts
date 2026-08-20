import { describe, it, expect } from 'vitest'
import { wrapPaginated } from '../pagination'

describe('wrapPaginated', () => {
  it('wraps an empty list', () => {
    expect(wrapPaginated([])).toEqual({
      items: [],
      total: 0,
      limit: 0,
      offset: 0,
    })
  })

  it('wraps a non-empty list deriving total and limit from length', () => {
    const items = [{ id: 1 }, { id: 2 }, { id: 3 }]
    expect(wrapPaginated(items)).toEqual({
      items,
      total: 3,
      limit: 3,
      offset: 0,
    })
  })
})
