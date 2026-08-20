import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { useCreateActivity } from '../mutations/useActivityMutations'
import { ActivityForm } from '../components/ActivityForm'
import type { ActivityCreateFormData } from '../schemas/activity.schema'

export function Component() {
  const navigate = useNavigate()
  const createMutation = useCreateActivity()

  const handleSubmit = async (data: ActivityCreateFormData) => {
    await createMutation.mutateAsync(data)
    navigate('/activities')
  }

  return (
    <div>
      <PageHeader
        title="New Activity"
        description="Log a call, email, meeting or note"
      />
      <div className="px-6 pb-6 max-w-3xl">
        <ActivityForm onSubmit={handleSubmit} isSubmitting={createMutation.isPending} />
      </div>
    </div>
  )
}

Component.displayName = 'ActivityCreatePage'
