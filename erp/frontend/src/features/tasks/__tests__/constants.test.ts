import { describe, it, expect } from 'vitest'
import {
  TASK_STATUSES,
  TASK_PRIORITIES,
  TASK_STATUS_LABELS,
  TASK_STATUS_VARIANTS,
  TASK_PRIORITY_LABELS,
  TASK_PRIORITY_VARIANTS,
} from '../types'

describe('task type constants', () => {
  it('defines statuses and priorities', () => {
    expect(TASK_STATUSES).toEqual(['TODO', 'IN_PROGRESS', 'DONE', 'CANCELLED'])
    expect(TASK_PRIORITIES).toEqual(['LOW', 'MEDIUM', 'HIGH', 'URGENT'])
  })

  it('maps statuses to labels and variants', () => {
    expect(TASK_STATUS_LABELS.TODO).toBe('To Do')
    expect(TASK_STATUS_LABELS.IN_PROGRESS).toBe('In Progress')
    expect(TASK_STATUS_VARIANTS.DONE).toBe('success')
    expect(TASK_STATUS_VARIANTS.CANCELLED).toBe('danger')
  })

  it('maps priorities to labels and variants', () => {
    expect(TASK_PRIORITY_LABELS.URGENT).toBe('Urgent')
    expect(TASK_PRIORITY_VARIANTS.HIGH).toBe('warning')
    expect(TASK_PRIORITY_VARIANTS.URGENT).toBe('danger')
  })
})
