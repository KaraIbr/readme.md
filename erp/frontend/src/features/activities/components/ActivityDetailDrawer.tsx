import { useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Badge } from '@atoms/Badge/Badge'
import { Spinner } from '@atoms/Spinner/Spinner'
import { SectionHeading } from '@atoms/SectionHeading/SectionHeading'
import { useActivity } from '../queries/useActivities'
import { useDeleteActivity, useCompleteActivity } from '../mutations/useActivityMutations'
import { ACTIVITY_LABELS, ACTIVITY_VARIANTS } from '../types'

interface ActivityDetailDrawerProps {
  activityId: number | null
  onClose: () => void
}

export function ActivityDetailDrawer({ activityId, onClose }: ActivityDetailDrawerProps) {
  const { data: activity, isLoading } = useActivity(activityId ?? 0)
  const completeMutation = useCompleteActivity()
  const deleteMutation = useDeleteActivity()

  const handleComplete = useCallback(async () => {
    if (!activityId) return
    await completeMutation.mutateAsync(activityId)
    onClose()
  }, [activityId, completeMutation, onClose])

  const handleDelete = useCallback(async () => {
    if (!activityId) return
    if (confirm('Delete this activity?')) {
      await deleteMutation.mutateAsync(activityId)
      onClose()
    }
  }, [activityId, deleteMutation, onClose])

  return (
    <Drawer
      open={activityId !== null}
      onClose={onClose}
      title={activity?.title ?? 'Activity'}
      subtitle={activity ? new Date(activity.created_at).toLocaleDateString() : 'Loading...'}
      editable={false}
    >
      {isLoading || !activity ? (
        <div className="flex items-center justify-center h-64">
          <Spinner />
        </div>
      ) : (
        <div className="space-y-6">
          <SectionHeading>Details</SectionHeading>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-caption text-text-tertiary">Type</span>
              <div className="mt-1">
                <Badge variant={ACTIVITY_VARIANTS[activity.activity_type]} size="sm">
                  {ACTIVITY_LABELS[activity.activity_type]}
                </Badge>
              </div>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Status</span>
              <div className="mt-1">
                <Badge variant={activity.completed_at ? 'success' : 'default'} size="sm">
                  {activity.completed_at ? 'Done' : 'Pending'}
                </Badge>
              </div>
            </div>
            {activity.scheduled_at && (
              <div>
                <span className="text-caption text-text-tertiary">Scheduled</span>
                <p className="text-small text-text mt-1">{new Date(activity.scheduled_at).toLocaleString()}</p>
              </div>
            )}
            {activity.completed_at && (
              <div>
                <span className="text-caption text-text-tertiary">Completed</span>
                <p className="text-small text-text mt-1">{new Date(activity.completed_at).toLocaleString()}</p>
              </div>
            )}
          </div>

          {activity.description && (
            <>
              <SectionHeading>Description</SectionHeading>
              <p className="text-body text-text-secondary whitespace-pre-wrap">{activity.description}</p>
            </>
          )}

          <div className="flex gap-2 pt-2">
            {!activity.completed_at && (
              <button
                type="button"
                onClick={handleComplete}
                className="flex-1 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors"
              >
                Mark Complete
              </button>
            )}
            <button
              type="button"
              onClick={handleDelete}
              className="px-4 py-2 text-sm font-medium text-danger hover:bg-danger-soft rounded-lg transition-colors"
            >
              Delete
            </button>
          </div>
        </div>
      )}
    </Drawer>
  )
}
