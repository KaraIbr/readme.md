import { useState, useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Badge } from '@atoms/Badge/Badge'
import { Spinner } from '@atoms/Spinner/Spinner'
import { SectionHeading } from '@atoms/SectionHeading/SectionHeading'
import { Button } from '@atoms/Button/Button'
import { useVisit } from '../queries/useVisits'
import { useCompleteVisit, useCancelVisit } from '../mutations/useVisitMutations'
import { STATUS_LABELS, STATUS_VARIANTS } from '../types'
import { VisitAttachmentsSection } from './VisitAttachmentsSection'

interface VisitDetailDrawerProps {
  visitId: number | null
  onClose: () => void
}

export function VisitDetailDrawer({ visitId, onClose }: VisitDetailDrawerProps) {
  const { data: visit, isLoading } = useVisit(visitId ?? 0)
  const completeVisit = useCompleteVisit()
  const cancelVisit = useCancelVisit()
  const [showCancelInput, setShowCancelInput] = useState(false)
  const [cancelReason, setCancelReason] = useState('')

  const handleComplete = useCallback(async () => {
    if (!visitId) return
    await completeVisit.mutateAsync(visitId)
    onClose()
  }, [visitId, completeVisit, onClose])

  const handleCancel = useCallback(async () => {
    if (!visitId) return
    await cancelVisit.mutateAsync({ id: visitId, reason: cancelReason || 'Cancelled' })
    onClose()
  }, [visitId, cancelVisit, cancelReason, onClose])

  const isActive = visit && (visit.status === 'REQUESTED' || visit.status === 'SCHEDULED')

  return (
    <Drawer
      open={visitId !== null}
      onClose={onClose}
      title={visit ? `Technical Visit #${visit.id}` : 'Technical Visit'}
      subtitle={visit ? `Lead #${visit.lead_id}` : 'Loading...'}
      editable={false}
    >
      {isLoading || !visit ? (
        <div className="flex items-center justify-center h-64">
          <Spinner />
        </div>
      ) : (
        <div className="space-y-6">
          <SectionHeading>Details</SectionHeading>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-caption text-text-tertiary">Status</span>
              <div className="mt-1">
                <Badge variant={STATUS_VARIANTS[visit.status]} size="sm">
                  {STATUS_LABELS[visit.status]}
                </Badge>
              </div>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Lead</span>
              <p className="text-small text-text mt-1">#{visit.lead_id}</p>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Scheduled At</span>
              <p className="text-small text-text mt-1">
                {visit.scheduled_at ? new Date(visit.scheduled_at).toLocaleString() : '\u2014'}
              </p>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Completed At</span>
              <p className="text-small text-text mt-1">
                {visit.completed_at ? new Date(visit.completed_at).toLocaleString() : '\u2014'}
              </p>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Receiver</span>
              <p className="text-small text-text mt-1">{visit.receiver_name ?? '\u2014'}</p>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Phone</span>
              <p className="text-small text-text mt-1">{visit.receiver_phone ?? '\u2014'}</p>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Created By</span>
              <p className="text-small text-text mt-1">{visit.created_by}</p>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Created At</span>
              <p className="text-small text-text mt-1">{new Date(visit.created_at).toLocaleDateString()}</p>
            </div>
          </div>

          {visit.notes && (
            <>
              <SectionHeading>Notes</SectionHeading>
              <p className="text-body text-text-secondary whitespace-pre-wrap">{visit.notes}</p>
            </>
          )}

          {visit.assignees.length > 0 && (
            <>
              <SectionHeading>Assignees</SectionHeading>
              <div className="space-y-1">
                {visit.assignees.map((a) => (
                  <div key={a.id} className="text-sm text-text flex items-center gap-2">
                    <span className="size-1.5 rounded-full bg-primary" />
                    {a.name}{a.user_id ? ` (user #${a.user_id})` : ''}
                  </div>
                ))}
              </div>
            </>
          )}

          {visit.cancellation_reason && (
            <>
              <SectionHeading>Cancellation Reason</SectionHeading>
              <p className="text-body text-text-secondary">{visit.cancellation_reason}</p>
            </>
          )}

          <SectionHeading>Attachments</SectionHeading>
          <VisitAttachmentsSection visitId={visit.id} />

          {showCancelInput && (
            <div className="bg-neutral-50 rounded-xl border border-border p-4 space-y-3">
              <h3 className="text-sm font-semibold text-text">Cancel Visit</h3>
              <textarea
                className="w-full h-20 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
                placeholder="Reason for cancellation (optional)"
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
              />
              <div className="flex gap-2">
                <Button size="sm" onClick={handleCancel} loading={cancelVisit.isPending}>Confirm Cancel</Button>
                <Button variant="secondary" size="sm" onClick={() => { setShowCancelInput(false); setCancelReason('') }}>Back</Button>
              </div>
            </div>
          )}

          <div className="flex gap-2 pt-2">
            {isActive && (
              <>
                <button
                  type="button"
                  onClick={handleComplete}
                  className="flex-1 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors"
                >
                  Complete Visit
                </button>
                <button
                  type="button"
                  onClick={() => setShowCancelInput(true)}
                  className="px-4 py-2 text-sm font-medium text-danger hover:bg-danger-soft rounded-lg transition-colors"
                >
                  Cancel
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </Drawer>
  )
}
