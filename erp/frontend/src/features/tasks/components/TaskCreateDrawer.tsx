import { useRef, useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { useCreateTask } from '../mutations/useTaskMutations'
import { TaskForm, type TaskFormHandle } from './TaskForm'
import type { TaskCreateFormData } from '../schemas/task.schema'

interface TaskCreateDrawerProps {
  open: boolean
  onClose: () => void
}

export function TaskCreateDrawer({ open, onClose }: TaskCreateDrawerProps) {
  const createMutation = useCreateTask()
  const formRef = useRef<TaskFormHandle>(null)

  const handleSave = useCallback(async () => {
    await formRef.current?.submitForm()
  }, [])

  const handleFormSubmit = useCallback(
    async (data: TaskCreateFormData) => {
      await createMutation.mutateAsync(data)
      onClose()
    },
    [createMutation, onClose],
  )

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="New Task"
      subtitle="Create a new task"
      editable
      actionLabel="Create Task"
      cancelLabel="Cancel"
      onAction={handleSave}
      actionLoading={createMutation.isPending}
      actionDisabled={createMutation.isPending}
    >
      <TaskForm
        ref={formRef}
        onSubmit={handleFormSubmit}
        isSubmitting={createMutation.isPending}
        hideSubmit
      />
    </Drawer>
  )
}
