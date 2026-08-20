import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Badge } from '@atoms/Badge/Badge'
import { Spinner } from '@atoms/Spinner/Spinner'
import { useOpportunity } from '../queries/useOpportunities'
import { useDeleteOpportunity, useMoveOpportunityStage, useCloseOpportunity } from '../mutations/useOpportunityMutations'
import { STAGE_LABELS, STAGE_VARIANTS, FORWARD_STAGES } from '../types'
import type { OpportunityStage } from '../types'

export function Component() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const opportunityId = Number(id)
  const { data: opp, isLoading } = useOpportunity(opportunityId)
  const deleteMutation = useDeleteOpportunity()
  const moveStageMutation = useMoveOpportunityStage()
  const closeMutation = useCloseOpportunity()
  const [closeOutcome, setCloseOutcome] = useState<'WON' | 'LOST'>('WON')
  const [closeNotes, setCloseNotes] = useState('')
  const [showCloseForm, setShowCloseForm] = useState(false)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64"><Spinner /></div>
    )
  }

  if (!opp) {
    return <div className="px-6 py-12 text-center text-gray-500">Opportunity not found</div>
  }

  const isTerminal = opp.current_stage === 'CLOSED_WON' || opp.current_stage === 'CLOSED_LOST'
  const nextStages = FORWARD_STAGES[opp.current_stage]

  const handleDelete = async () => {
    if (!confirm('Delete this opportunity?')) return
    await deleteMutation.mutateAsync(opportunityId)
    navigate('/opportunities')
  }

  const handleStageMove = async (stage: OpportunityStage) => {
    await moveStageMutation.mutateAsync({
      id: opportunityId,
      stage: { stage },
    })
  }

  const handleClose = async () => {
    await closeMutation.mutateAsync({
      id: opportunityId,
      data: { outcome: closeOutcome, notes: closeNotes || null },
    })
    setShowCloseForm(false)
  }

  return (
    <div>
      <PageHeader
        title={opp.name}
        description={
          <Badge variant={STAGE_VARIANTS[opp.current_stage]} size="sm">
            {STAGE_LABELS[opp.current_stage]}
          </Badge>
        }
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => navigate('/opportunities')}>Back</Button>
            {!isTerminal && (
              <>
                {nextStages.filter(s => s !== 'CLOSED_WON' && s !== 'CLOSED_LOST').map((s) => (
                  <Button key={s} variant="secondary" onClick={() => handleStageMove(s)}>
                    Move to {STAGE_LABELS[s]}
                  </Button>
                ))}
                <Button onClick={() => setShowCloseForm(true)}>Close</Button>
              </>
            )}
            <Button variant="danger" onClick={handleDelete}>Delete</Button>
          </div>
        }
      />
      <div className="px-6 pb-6 max-w-3xl space-y-6">
        <div className="bg-white rounded-xl border border-border p-6 space-y-3">
          <h2 className="text-lg font-semibold">Details</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div><span className="text-gray-500">Value:</span><p>{opp.value != null ? `${opp.currency ?? 'MXN'} ${opp.value.toLocaleString()}` : '—'}</p></div>
            <div><span className="text-gray-500">Contact ID:</span><p>{opp.contact_id}</p></div>
            <div><span className="text-gray-500">Lead ID:</span><p>{opp.lead_id ?? '—'}</p></div>
            <div><span className="text-gray-500">Expected Close:</span><p>{opp.expected_close_date ? new Date(opp.expected_close_date).toLocaleDateString() : '—'}</p></div>
            <div><span className="text-gray-500">Stage:</span><p>{STAGE_LABELS[opp.current_stage]}</p></div>
            <div><span className="text-gray-500">Notes:</span><p className="whitespace-pre-wrap">{opp.notes ?? '—'}</p></div>
          </div>
        </div>

        {showCloseForm && (
          <div className="bg-white rounded-xl border border-border p-6 space-y-4">
            <h2 className="text-lg font-semibold">Close Opportunity</h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Outcome</label>
              <select
                value={closeOutcome}
                onChange={(e) => setCloseOutcome(e.target.value as 'WON' | 'LOST')}
                className="w-full border border-border rounded-lg px-3 py-2 text-sm"
              >
                <option value="WON">Won</option>
                <option value="LOST">Lost</option>
              </select>
            </div>
            {closeOutcome === 'LOST' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Loss Reason</label>
                <textarea
                  value={closeNotes}
                  onChange={(e) => setCloseNotes(e.target.value)}
                  rows={3}
                  className="w-full border border-border rounded-lg px-3 py-2 text-sm"
                  placeholder="Why was this opportunity lost?"
                />
              </div>
            )}
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => setShowCloseForm(false)}>Cancel</Button>
              <Button onClick={handleClose} disabled={closeMutation.isPending}>Confirm Close</Button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

Component.displayName = 'OpportunityDetailPage'
