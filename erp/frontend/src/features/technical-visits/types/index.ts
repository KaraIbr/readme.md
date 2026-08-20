export const VISIT_STATUSES = ['REQUESTED', 'SCHEDULED', 'COMPLETED', 'CANCELLED'] as const
export type VisitStatus = (typeof VISIT_STATUSES)[number]

export const ACTIVE_VISIT_STATUSES = ['REQUESTED', 'SCHEDULED'] as const
export const ATTACHMENT_KINDS = ['DOCUMENT', 'PHOTO', 'OTHER'] as const
export type AttachmentKind = (typeof ATTACHMENT_KINDS)[number]

export interface TechnicalVisitRead {
  id: number
  lead_id: number
  status: VisitStatus
  scheduled_at: string | null
  receiver_name: string | null
  receiver_phone: string | null
  notes: string | null
  created_by: number
  created_at: string
  updated_at: string
  completed_at: string | null
  cancelled_at: string | null
  cancellation_reason: string | null
  assignees: TechnicalVisitAssigneeRead[]
}

export interface TechnicalVisitAssigneeRead {
  id: number
  visit_id: number
  name: string
  user_id: number | null
  created_at: string
}

export interface TechnicalVisitAttachmentRead {
  id: number
  visit_id: number
  title: string
  file_kind: AttachmentKind
  original_filename: string
  content_type: string | null
  size_bytes: number
  uploaded_by: number
  uploaded_at: string
}

export interface VisitAssigneeInput {
  name: string
  user_id?: number | null
}

export interface VisitCreate {
  lead_id: number
  scheduled_at?: string | null
  receiver_name?: string | null
  receiver_phone?: string | null
  notes?: string | null
  assignees?: VisitAssigneeInput[]
}

export interface VisitUpdate {
  scheduled_at?: string | null
  receiver_name?: string | null
  receiver_phone?: string | null
  notes?: string | null
}

export interface VisitFilters {
  lead_id?: number
  status?: VisitStatus
  limit?: number
  offset?: number
}

export const STATUS_LABELS: Record<VisitStatus, string> = {
  REQUESTED: 'Requested',
  SCHEDULED: 'Scheduled',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
}

export const STATUS_VARIANTS: Record<VisitStatus, 'default' | 'warning' | 'info' | 'success' | 'danger'> = {
  REQUESTED: 'default',
  SCHEDULED: 'info',
  COMPLETED: 'success',
  CANCELLED: 'danger',
}

export const ATTACHMENT_KIND_LABELS: Record<AttachmentKind, string> = {
  DOCUMENT: 'Document',
  PHOTO: 'Photo',
  OTHER: 'Other',
}
