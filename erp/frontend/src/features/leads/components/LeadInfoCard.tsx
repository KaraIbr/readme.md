import { Link, useNavigate } from 'react-router-dom'
import { Badge } from '@atoms/Badge/Badge'
import { Button } from '@atoms/Button/Button'
import { useSetVisitRequirement } from '@features/technical-visits/mutations/useVisitMutations'
import type { LeadRead } from '../types'
import { STAGE_LABELS, STAGE_VARIANTS, INTEREST_LABELS } from '../types'

interface LeadInfoCardProps {
  lead: LeadRead
}

const REQUIREMENT_LABELS: Record<string, string> = {
  UNDETERMINED: 'Undetermined',
  NOT_REQUIRED: 'Not Required',
  REQUIRED: 'Required',
}

const REQUIREMENT_VARIANTS: Record<string, 'default' | 'warning' | 'success'> = {
  UNDETERMINED: 'default',
  NOT_REQUIRED: 'warning',
  REQUIRED: 'success',
}

export function LeadInfoCard({ lead }: LeadInfoCardProps) {
  const navigate = useNavigate()
  const setRequirement = useSetVisitRequirement()

  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Badge variant={STAGE_VARIANTS[lead.current_stage]} size="md">
            {STAGE_LABELS[lead.current_stage]}
          </Badge>
          <Badge variant="info" size="sm">
            {INTEREST_LABELS[lead.interest_type]}
          </Badge>
        </div>
        <Button size="sm" onClick={() => navigate(`/technical-visits/new?leadId=${lead.id}`)}>
          New Visit
        </Button>
      </div>

      <div className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
        <Field label="Contact" value={
          <Link to={`/contacts/${lead.contact_id}`} className="text-primary hover:underline">
            #{lead.contact_id}
          </Link>
        } />
        <Field label="Owner ID" value={lead.owner_id} />
        <Field label="Qualification Score" value={lead.qualification_score ?? '—'} />
        <Field label="Tech Visit Requirement" value={
          <div className="flex items-center gap-2">
            <Badge variant={REQUIREMENT_VARIANTS[lead.technical_visit_requirement]} size="sm">
              {REQUIREMENT_LABELS[lead.technical_visit_requirement]}
            </Badge>
            <div className="flex gap-1">
              {lead.technical_visit_requirement !== 'REQUIRED' && (
                <Button size="sm" variant="secondary" onClick={() => setRequirement.mutate({ leadId: lead.id, requirement: 'REQUIRED' })} disabled={setRequirement.isPending}>
                  Require
                </Button>
              )}
              {lead.technical_visit_requirement !== 'NOT_REQUIRED' && (
                <Button size="sm" variant="secondary" onClick={() => setRequirement.mutate({ leadId: lead.id, requirement: 'NOT_REQUIRED' })} disabled={setRequirement.isPending}>
                  Skip
                </Button>
              )}
            </div>
          </div>
        } />
        <Field label="Created" value={new Date(lead.created_at).toLocaleDateString()} />
        <Field label="Closed" value={lead.closed_at ? new Date(lead.closed_at).toLocaleDateString() : '—'} />
        <Field label="Outcome" value={lead.outcome ?? '—'} />
      </div>

      {lead.notes && (
        <div>
          <p className="text-xs font-medium text-text-secondary mb-1">Notes</p>
          <p className="text-sm text-text whitespace-pre-wrap">{lead.notes}</p>
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
