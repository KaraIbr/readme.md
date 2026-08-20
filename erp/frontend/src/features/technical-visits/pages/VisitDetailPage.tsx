import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Spinner } from '@atoms/Spinner/Spinner'
import { EmptyState } from '@molecules/EmptyState/EmptyState'
import { useVisit } from '../queries/useVisits'
import { useCompleteVisit, useCancelVisit } from '../mutations/useVisitMutations'
import { VisitInfoCard } from '../components/VisitInfoCard'
import { VisitAttachmentsSection } from '../components/VisitAttachmentsSection'

export function Component() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const visitId = Number(id)
  const { data: visit, isLoading, isError } = useVisit(visitId)
  const completeVisit = useCompleteVisit()
  const cancelVisit = useCancelVisit()
  const [showCancelInput, setShowCancelInput] = useState(false)
  const [cancelReason, setCancelReason] = useState('')

  async function handleComplete() {
    await completeVisit.mutateAsync(visitId)
  }

  async function handleCancel() {
    await cancelVisit.mutateAsync({ id: visitId, reason: cancelReason || 'Cancelled' })
    setShowCancelInput(false)
    setCancelReason('')
  }

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Technical Visit" actions={<Button variant="secondary" onClick={() => navigate('/technical-visits')}>Back</Button>} />
        <div className="flex items-center justify-center py-16">
          <Spinner size="lg" />
        </div>
      </div>
    )
  }

  if (isError || !visit) {
    return (
      <div>
        <PageHeader title="Technical Visit" actions={<Button variant="secondary" onClick={() => navigate('/technical-visits')}>Back</Button>} />
        <EmptyState title="Visit not found" description="The visit you're looking for doesn't exist" />
      </div>
    )
  }

  const isActive = visit.status === 'REQUESTED' || visit.status === 'SCHEDULED'

  return (
    <div>
      <PageHeader
        title={`Technical Visit #${visit.id}`}
        description={`Lead #${visit.lead_id}`}
        actions={
          <div className="flex gap-2">
            {isActive && (
              <>
                <Button variant="secondary" onClick={handleComplete} loading={completeVisit.isPending}>
                  Complete
                </Button>
                <Button variant="secondary" onClick={() => setShowCancelInput(true)}>
                  Cancel
                </Button>
              </>
            )}
            <Button variant="secondary" onClick={() => navigate('/technical-visits')}>Back</Button>
          </div>
        }
      />
      <div className="px-6 pb-6 max-w-3xl space-y-6">
        {showCancelInput && (
          <div className="bg-white rounded-xl border border-border p-4 space-y-3">
            <h3 className="text-sm font-semibold text-text">Cancel Visit</h3>
            <textarea
              className="w-full h-20 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
              placeholder="Reason for cancellation (optional)"
              value={cancelReason}
              onChange={(e) => setCancelReason(e.target.value)}
            />
            <div className="flex gap-2">
              <Button variant="secondary" onClick={handleCancel} loading={cancelVisit.isPending}>Confirm Cancel</Button>
              <Button variant="secondary" onClick={() => { setShowCancelInput(false); setCancelReason('') }}>Back</Button>
            </div>
          </div>
        )}
        <VisitInfoCard visit={visit} />
        <VisitAttachmentsSection visitId={visit.id} />
      </div>
    </div>
  )
}

Component.displayName = 'VisitDetailPage'
