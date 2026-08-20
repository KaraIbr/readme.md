import { useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Badge } from '@atoms/Badge/Badge'
import { Spinner } from '@atoms/Spinner/Spinner'
import { SectionHeading } from '@atoms/SectionHeading/SectionHeading'
import { useTask } from '../queries/useTasks'
import { useDeleteTask, useChangeTaskStatus } from '../mutations/useTaskMutations'
import { TASK_STATUS_LABELS, TASK_STATUS_VARIANTS, TASK_PRIORITY_LABELS, TASK_PRIORITY_VARIANTS } from '../types'
import type { TaskStatus } from '../types'

const NEXT_STATUS: Record<TaskStatus, TaskStatus | null> = {
  TODO: 'IN_PROGRESS',
  IN_PROGRESS: 'DONE',
  DONE: null,
  CANCELLED: null,
}

interface TaskDetailDrawerProps {
  taskId: number | null
  onClose: () => void
}

export function TaskDetailDrawer({ taskId, onClose }: TaskDetailDrawerProps) {
  const { data: task, isLoading } = useTask(taskId ?? 0)
  const statusMutation = useChangeTaskStatus()
  const deleteMutation = useDeleteTask()

  const handleProgress = useCallback(async () => {
    if (!taskId || !task) return
    const next = NEXT_STATUS[task.status]
    if (next) {
      await statusMutation.mutateAsync({ id: taskId, status: next })
      onClose()
    }
  }, [taskId, task, statusMutation, onClose])

  const handleDelete = useCallback(async () => {
    if (!taskId) return
    if (confirm('Delete this task?')) {
      await deleteMutation.mutateAsync(taskId)
      onClose()
    }
  }, [taskId, deleteMutation, onClose])

  return (
    <Drawer
      open={taskId !== null}
      onClose={onClose}
      title={task?.title ?? 'Task'}
      subtitle={task ? `Created ${new Date(task.created_at).toLocaleDateString()}` : 'Loading...'}
      editable={false}
    >
      {isLoading || !task ? (
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
                <Badge variant={TASK_STATUS_VARIANTS[task.status]} size="sm">
                  {TASK_STATUS_LABELS[task.status]}
                </Badge>
              </div>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Priority</span>
              <div className="mt-1">
                <Badge variant={TASK_PRIORITY_VARIANTS[task.priority]} size="sm">
                  {TASK_PRIORITY_LABELS[task.priority]}
                </Badge>
              </div>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Due Date</span>
              <p className="text-small text-text mt-1">{task.due_date ? new Date(task.due_date).toLocaleDateString() : '-'}</p>
            </div>
            <div>
              <span className="text-caption text-text-tertiary">Completed</span>
              <p className="text-small text-text mt-1">{task.completed_at ? new Date(task.completed_at).toLocaleDateString() : '-'}</p>
            </div>
          </div>

          {task.description && (
            <>
              <SectionHeading>Description</SectionHeading>
              <p className="text-body text-text-secondary whitespace-pre-wrap">{task.description}</p>
            </>
          )}

          <div className="flex gap-2 pt-2">
            {NEXT_STATUS[task.status] && (
              <button
                type="button"
                onClick={handleProgress}
                className="flex-1 px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-hover transition-colors"
              >
                {NEXT_STATUS[task.status] === 'IN_PROGRESS' ? 'Start Task' : 'Complete Task'}
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
