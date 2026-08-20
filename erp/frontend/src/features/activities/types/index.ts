import type { BadgeVariant } from '@atoms/Badge/Badge'

export type ActivityType = 'CALL' | 'EMAIL' | 'MEETING' | 'NOTE'

export interface ActivityRead {
  id: number
  activity_type: ActivityType
  title: string
  description: string | null
  contact_id: number | null
  lead_id: number | null
  assigned_to: number | null
  scheduled_at: string | null
  completed_at: string | null
  created_by: number
  created_at: string
  updated_at: string
}

export interface ActivityCreate {
  activity_type: ActivityType
  title: string
  description?: string | null
  contact_id?: number | null
  lead_id?: number | null
  assigned_to?: number | null
  scheduled_at?: string | null
}

export interface ActivityUpdate {
  activity_type?: ActivityType
  title?: string
  description?: string | null
  assigned_to?: number | null
  scheduled_at?: string | null
}

export const ACTIVITY_TYPES: ActivityType[] = ['CALL', 'EMAIL', 'MEETING', 'NOTE']

export const ACTIVITY_LABELS: Record<ActivityType, string> = {
  CALL: 'Call',
  EMAIL: 'Email',
  MEETING: 'Meeting',
  NOTE: 'Note',
}

export const ACTIVITY_VARIANTS: Record<ActivityType, BadgeVariant> = {
  CALL: 'warning',
  EMAIL: 'info',
  MEETING: 'info',
  NOTE: 'default',
}
