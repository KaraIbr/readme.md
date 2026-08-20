import { useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Badge } from '@atoms/Badge/Badge'
import { Button } from '@atoms/Button/Button'
import { Spinner } from '@atoms/Spinner/Spinner'
import { SectionHeading } from '@atoms/SectionHeading/SectionHeading'
import { useOpportunity } from '../queries/useOpportunities'
import { useMoveOpportunityStage, useCloseOpportunity, useDeleteOpportunity } from '../mutations/useOpportunityMutations'
import { STAGE_LABELS, STAGE_VARIANTS, FORWARD_STAGES } from '../types'
import type { OpportunityStage } from '../types'

interface OpportunityDetailDrawerProps {
  opportunityId: number | null
  onClose: () => void
}

export function OpportunityDetailDrawer({ opportunityId, onClose }: OpportunityDetailDrawerProps) {
  const { data: opportunity, isLoading } = useOpportunity(opportunityId ?? 0)
  const stageMutation = useMoveOpportunityStage()
  const closeMutation = useCloseOpportunity()
  const deleteMutation = useDeleteOpportunity()

  const handleStageMove = useCallback(async (stage: OpportunityStage) => {
    if (!opportunityId) return
    await stageMutation.mutateAsync({ id: opportunityId, stage: { stage } })
  }, [opportunityId, stageMutation])

  const handleClose = useCallback(async (outcome: 'WON' | 'LOST') => {
    if (!opportunityId) return
    await closeMutation.mutateAsync({ id: opportunityId, data: { outcome } })
  }, [opportunityId, closeMutation])

  const handleDelete = useCallback(async () => {
    if (!opportunityId) return
    if (confirm('Delete this opportunity?')) {
      await deleteMutation.mutateAsync(opportunityId)
      onClose()
    }
  }, [opportunityId, deleteMutation, onClose])

  return (
    <Drawer
      open={opportunityId !== null}
      onClose={onClose}
      title={opportunity?.name ?? 'Opportunity'}
      subtitle={opportunity ? `Created ${new Date(opportunity.created_at).toLocaleDateString()}` : 'Loading...'}
      editable={false}
    >
      {isLoading || !opportunity ? (
        <div className="flex items-center justify-center h-64">
          <Spinner />
        </div>
      ) : (
        <div className="space-y-6">
          <SectionHeading>Details</SectionHeading>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-caption text-text-tertiary">Stage</span>
              <div className="mt-1">
                <Badge variant={STAGE_VARIANTS[opportunity.current_stage]} size="sm">
                  {STAGE_LABELS[opportunity.current_stage]}
                </Badge>
              </div>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Value</span>
              <p className="text-small text-text mt-1">{opportunity.value != null ? `${opportunity.currency ?? 'MXN'} ${opportunity.value.toLocaleString()}` : '—'}</p>
            </div>
            {opportunity.expected_close_date && (
              <div>
                <span className="text-caption text-text-tertiary">Expected Close</span>
                <p className="text-small text-text mt-1">{new Date(opportunity.expected_close_date).toLocaleDateString()}</p>
              </div>
            )}
            {opportunity.closed_at && (
              <div>
                <span className="text-caption text-text-tertiary">Closed</span>
                <p className="text-small text-text mt-1">{new Date(opportunity.closed_at).toLocaleDateString()}</p>
              </div>
            )}
          </div>

          {opportunity.notes && (
            <>
              <SectionHeading>Notes</SectionHeading>
              <p className="text-body text-text-secondary whitespace-pre-wrap">{opportunity.notes}</p>
            </>
          )}

          {FORWARD_STAGES[opportunity.current_stage].length > 0 && (
            <>
              <SectionHeading>Advance Stage</SectionHeading>
              <div className="flex gap-2 flex-wrap">
                {FORWARD_STAGES[opportunity.current_stage].map((stage) => (
                  <Button
                    key={stage}
                    size="sm"
                    onClick={() => handleStageMove(stage)}
                    loading={stageMutation.isPending}
                  >
                    Move to {STAGE_LABELS[stage]}
                  </Button>
                ))}
              </div>
            </>
          )}

          {opportunity.current_stage === 'NEGOTIATION' && (
            <>
              <SectionHeading>Close Opportunity</SectionHeading>
              <div className="flex gap-2">
                <Button variant="primary" size="sm" onClick={() => handleClose('WON')} loading={closeMutation.isPending}>
                  Won
                </Button>
                <Button variant="danger" size="sm" onClick={() => handleClose('LOST')} loading={closeMutation.isPending}>
                  Lost
                </Button>
              </div>
            </>
          )}

          <div className="pt-2">
            <button
              type="button"
              onClick={handleDelete}
              className="text-sm text-danger hover:text-danger-hover transition-colors"
            >
              Delete opportunity
            </button>
          </div>
        </div>
      )}
    </Drawer>
  )
}
