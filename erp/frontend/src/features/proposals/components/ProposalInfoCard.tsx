import { Link } from 'react-router-dom'
import { Badge } from '@atoms/Badge/Badge'
import type { ProposalRead } from '../types'
import { STAGE_LABELS, STAGE_VARIANTS, SYSTEM_TYPE_LABELS } from '../types'
import { MissingFieldsCard } from './MissingFieldsCard'

interface ProposalInfoCardProps {
  proposal: ProposalRead
}

export function ProposalInfoCard({ proposal }: ProposalInfoCardProps) {
  const addr = proposal.installation_address

  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-4">
      <div className="flex items-center gap-3">
        <Badge variant={STAGE_VARIANTS[proposal.current_stage]} size="md">
          {STAGE_LABELS[proposal.current_stage]}
        </Badge>
        {proposal.system_type && (
          <Badge variant="info" size="sm">
            {SYSTEM_TYPE_LABELS[proposal.system_type]}
          </Badge>
        )}
        {proposal.is_complete ? (
          <Badge variant="success" size="sm">Complete</Badge>
        ) : (
          <Badge variant="warning" size="sm">Incomplete</Badge>
        )}
      </div>

      <div className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
        <Field label="Lead" value={
          <div className="flex items-center gap-2">
            <Link to={`/leads/${proposal.lead_id}`} className="text-primary hover:underline font-medium">
              {proposal.lead_name ?? `#${proposal.lead_id}`}
            </Link>
            {proposal.lead_stage && (
              <Badge variant="info" size="sm">{proposal.lead_stage}</Badge>
            )}
          </div>
        } />
        <Field label="Version" value={proposal.version ?? '—'} />
        <Field label="System Type" value={proposal.system_type ? SYSTEM_TYPE_LABELS[proposal.system_type] : '—'} />
        <Field label="Tariff" value={proposal.tariff ?? '—'} />
        <Field label="Contracted Demand" value={proposal.contracted_demand ?? '—'} />
        <Field label="Total Price" value={proposal.total_price != null ? `${proposal.currency ?? ''} ${proposal.total_price}` : '—'} />
        <Field label="Annual Savings" value={proposal.annual_savings != null ? `${proposal.currency ?? ''} ${proposal.annual_savings}` : '—'} />
        <Field label="Estimated Cost" value={proposal.estimated_cost != null ? `${proposal.currency ?? ''} ${proposal.estimated_cost}` : '—'} />
        <Field label="Expected Profit" value={proposal.expected_profit != null ? `${proposal.currency ?? ''} ${proposal.expected_profit}` : '—'} />
        <Field label="Submitted At" value={proposal.submitted_at ? new Date(proposal.submitted_at).toLocaleDateString() : '—'} />
        <Field label="Valid Until" value={proposal.valid_until ? new Date(proposal.valid_until).toLocaleDateString() : '—'} />
        <Field label="Created" value={new Date(proposal.created_at).toLocaleDateString()} />
        <Field label="Created By" value={proposal.created_by} />
        <Field label="Loss Reason" value={proposal.loss_reason ?? '—'} />
      </div>

      <MissingFieldsCard missingFields={proposal.missing_required_fields} />

      <div className="border-t border-border pt-4">
        <p className="text-xs font-medium text-text-secondary mb-2">Installation Address</p>
        <p className="text-sm text-text">
          {[addr?.address_line, addr?.city, addr?.state, addr?.postal_code].filter(Boolean).join(', ') || 'No address'}
        </p>
      </div>
    </div>
  )
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs font-medium text-text-secondary">{label}</p>
      <p className="text-sm text-text mt-0.5 break-words">{value}</p>
    </div>
  )
}
