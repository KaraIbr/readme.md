import { useRef, useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { useCreateActivity } from '../mutations/useActivityMutations'
import { ActivityForm, type ActivityFormHandle } from './ActivityForm'
import type { ActivityCreateFormData } from '../schemas/activity.schema'

interface ActivityCreateDrawerProps {
  open: boolean
  onClose: () => void
}

export function ActivityCreateDrawer({ open, onClose }: ActivityCreateDrawerProps) {
  const createMutation = useCreateActivity()
  const formRef = useRef<ActivityFormHandle>(null)

  const handleSave = useCallback(async () => {
    await formRef.current?.submitForm()
  }, [])

  const handleFormSubmit = useCallback(
    async (data: ActivityCreateFormData) => {
      await createMutation.mutateAsync(data)
      onClose()
    },
    [createMutation, onClose],
  )

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="New Activity"
      subtitle="Log a call, email, meeting or note"
      editable
      actionLabel="Create Activity"
      cancelLabel="Cancel"
      onAction={handleSave}
      actionLoading={createMutation.isPending}
      actionDisabled={createMutation.isPending}
    >
      <ActivityForm
        ref={formRef}
        onSubmit={handleFormSubmit}
        isSubmitting={createMutation.isPending}
        hideSubmit
      />
    </Drawer>
  )
}
