import { useMemo } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Badge } from '@atoms/Badge/Badge'
import { Spinner } from '@atoms/Spinner/Spinner'
import { useActivity } from '../queries/useActivities'
import { useDeleteActivity, useCompleteActivity } from '../mutations/useActivityMutations'
import { ACTIVITY_LABELS, ACTIVITY_VARIANTS } from '../types'
import { useContacts } from '@features/contacts'
import { useLeadList } from '@features/leads'
import { useUsers } from '@features/admin'

export function Component() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const activityId = Number(id)
  const { data: activity, isLoading } = useActivity(activityId)
  const deleteMutation = useDeleteActivity()
  const completeMutation = useCompleteActivity()

  const { data: contactsPage } = useContacts()
  const { data: leadsData } = useLeadList()
  const { data: users } = useUsers()

  const contactName = useMemo(() => {
    if (!activity?.contact_id) return null
    const contact = (contactsPage?.items ?? []).find((c) => c.id === activity.contact_id)
    return contact?.name ?? `Contact #${activity.contact_id}`
  }, [activity, contactsPage])

  const leadName = useMemo(() => {
    if (!activity?.lead_id) return null
    const lead = (leadsData?.items ?? []).find((l) => l.id === activity.lead_id)
    return lead?.title ?? `Lead #${activity.lead_id}`
  }, [activity, leadsData])

  const assignedToName = useMemo(() => {
    if (!activity?.assigned_to) return null
    const user = (users ?? []).find((u) => u.id === activity.assigned_to)
    return user ? (user.full_name ?? user.email) : `User #${activity.assigned_to}`
  }, [activity, users])

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this activity?')) return
    await deleteMutation.mutateAsync(activityId)
    navigate('/activities')
  }

  const handleComplete = async () => {
    await completeMutation.mutateAsync(activityId)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    )
  }

  if (!activity) {
    return (
      <div className="px-6 py-12 text-center text-gray-500">Activity not found</div>
    )
  }

  return (
    <div>
      <PageHeader
        title={activity.title}
        description={
          <Badge variant={ACTIVITY_VARIANTS[activity.activity_type]} size="sm">
            {ACTIVITY_LABELS[activity.activity_type]}
          </Badge>
        }
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => navigate('/activities')}>Back</Button>
            {!activity.completed_at && (
              <Button onClick={handleComplete} disabled={completeMutation.isPending}>
                Mark Complete
              </Button>
            )}
            <Button variant="danger" onClick={handleDelete} disabled={deleteMutation.isPending}>
              Delete
            </Button>
          </div>
        }
      />
      <div className="px-6 pb-6 max-w-3xl space-y-6">
        <div className="bg-white rounded-xl border border-border p-6 space-y-3">
          <h2 className="text-lg font-semibold">Details</h2>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Description:</span>
              <p className="whitespace-pre-wrap">{activity.description ?? '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Contact:</span>
              <p>{contactName ?? '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Lead:</span>
              <p>{leadName ?? '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Assigned To:</span>
              <p>{assignedToName ?? '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Scheduled:</span>
              <p>{activity.scheduled_at ? new Date(activity.scheduled_at).toLocaleString() : '—'}</p>
            </div>
            <div>
              <span className="text-gray-500">Status:</span>
              <p>{activity.completed_at ? 'Completed' : 'Pending'}</p>
            </div>
            <div>
              <span className="text-gray-500">Created:</span>
              <p>{new Date(activity.created_at).toLocaleString()}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

Component.displayName = 'ActivityDetailPage'
