import { Link } from 'react-router-dom'
import { Badge } from '@atoms/Badge/Badge'
import type { TechnicalVisitRead } from '../types'
import { STATUS_LABELS, STATUS_VARIANTS } from '../types'

interface VisitInfoCardProps {
  visit: TechnicalVisitRead
}

export function VisitInfoCard({ visit }: VisitInfoCardProps) {
  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-4">
      <div className="flex items-center gap-3">
        <Badge variant={STATUS_VARIANTS[visit.status]} size="md">
          {STATUS_LABELS[visit.status]}
        </Badge>
      </div>

      <div className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
        <Field label="Lead" value={
          <Link to={`/leads/${visit.lead_id}`} className="text-primary hover:underline">#{visit.lead_id}</Link>
        } />
        <Field label="Status" value={STATUS_LABELS[visit.status]} />
        <Field label="Scheduled At" value={visit.scheduled_at ? new Date(visit.scheduled_at).toLocaleString() : '—'} />
        <Field label="Receiver" value={visit.receiver_name ?? '—'} />
        <Field label="Phone" value={visit.receiver_phone ?? '—'} />
        <Field label="Created By" value={visit.created_by} />
        <Field label="Created At" value={new Date(visit.created_at).toLocaleDateString()} />
        <Field label="Updated At" value={new Date(visit.updated_at).toLocaleDateString()} />
        <Field label="Completed At" value={visit.completed_at ? new Date(visit.completed_at).toLocaleString() : '—'} />
        <Field label="Cancelled At" value={visit.cancelled_at ? new Date(visit.cancelled_at).toLocaleString() : '—'} />
        <Field label="Cancel Reason" value={visit.cancellation_reason ?? '—'} />
      </div>

      {visit.notes && (
        <div>
          <p className="text-xs font-medium text-text-secondary mb-1">Notes</p>
          <p className="text-sm text-text whitespace-pre-wrap">{visit.notes}</p>
        </div>
      )}

      {visit.assignees.length > 0 && (
        <div>
          <p className="text-xs font-medium text-text-secondary mb-2">Assignees</p>
          <div className="space-y-1">
            {visit.assignees.map((a) => (
              <div key={a.id} className="text-sm text-text flex items-center gap-2">
                <span className="size-1.5 rounded-full bg-primary" />
                {a.name}{a.user_id ? ` (user #${a.user_id})` : ''}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs font-medium text-text-secondary">{label}</p>
      <p className="text-sm text-text mt-0.5">{value}</p>
    </div>
  )
}
