import { useNavigate } from 'react-router-dom'
import { useForm, type SubmitHandler } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'
import { useCreateOpportunity } from '../mutations/useOpportunityMutations'
import { opportunityCreateSchema, type OpportunityCreateFormData } from '../schemas/opportunity.schema'

export function Component() {
  const navigate = useNavigate()
  const createMutation = useCreateOpportunity()

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<z.input<typeof opportunityCreateSchema>, unknown, OpportunityCreateFormData>({
    resolver: zodResolver(opportunityCreateSchema),
  })

  const onSubmit: SubmitHandler<OpportunityCreateFormData> = async (data) => {
    const opp = await createMutation.mutateAsync(data)
    navigate(`/opportunities/${opp.id}`)
  }

  return (
    <div>
      <PageHeader title="New Opportunity" description="Create a new sales opportunity" />
      <div className="px-6 pb-6 max-w-3xl">
        <form onSubmit={handleSubmit(onSubmit)} className="bg-white rounded-xl border border-border p-6 space-y-4">
          <Input label="Name" error={errors.name?.message} {...register('name')} />
          <Input label="Contact ID" type="number" error={errors.contact_id?.message} {...register('contact_id')} />
          <Input label="Lead ID" type="number" error={errors.lead_id?.message} {...register('lead_id')} />
          <Input label="Value" type="number" step="0.01" error={errors.value?.message} {...register('value')} />
          <Input label="Currency" placeholder="MXN" error={errors.currency?.message} {...register('currency')} />
          <Input label="Expected Close Date" type="date" error={errors.expected_close_date?.message} {...register('expected_close_date')} />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Notes</label>
            <textarea
              {...register('notes')}
              rows={4}
              className="w-full border border-border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div className="flex justify-end">
            <Button type="submit" disabled={createMutation.isPending}>Create Opportunity</Button>
          </div>
        </form>
      </div>
    </div>
  )
}

Component.displayName = 'OpportunityCreatePage'
