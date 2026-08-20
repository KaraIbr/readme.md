import { useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Input } from '@atoms/Input/Input'
import { FormField } from '@molecules/FormField/FormField'
import { useCreateOpportunity } from '../mutations/useOpportunityMutations'
import { opportunityCreateSchema, type OpportunityCreateFormData } from '../schemas/opportunity.schema'

interface OpportunityCreateDrawerProps {
  open: boolean
  onClose: () => void
}

export function OpportunityCreateDrawer({ open, onClose }: OpportunityCreateDrawerProps) {
  const createMutation = useCreateOpportunity()
  const { register, handleSubmit, reset, formState: { errors } } = useForm<z.input<typeof opportunityCreateSchema>, unknown, OpportunityCreateFormData>({
    resolver: zodResolver(opportunityCreateSchema),
    defaultValues: {
      name: '',
      value: undefined,
      currency: 'MXN',
      expected_close_date: '',
      notes: '',
    },
  })

  const onSubmit = useCallback(async (data: OpportunityCreateFormData) => {
    await createMutation.mutateAsync(data)
    reset()
    onClose()
  }, [createMutation, reset, onClose])

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="New Opportunity"
      subtitle="Create a new sales opportunity"
      editable
      actionLabel="Create"
      cancelLabel="Cancel"
      onAction={handleSubmit(onSubmit)}
      actionLoading={createMutation.isPending}
      actionDisabled={createMutation.isPending}
    >
      <div className="space-y-4">
        <Input label="Name" required error={errors.name?.message} {...register('name')} />
        <Input label="Contact ID" type="number" required error={errors.contact_id?.message} {...register('contact_id', { valueAsNumber: true })} />
        <Input label="Value" type="number" error={errors.value?.message} {...register('value', { valueAsNumber: true })} />
        <FormField label="Currency" error={errors.currency?.message}>
          <select className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('currency')}>
            <option value="MXN">MXN</option>
            <option value="USD">USD</option>
          </select>
        </FormField>
        <Input label="Expected Close Date" type="date" error={errors.expected_close_date?.message} {...register('expected_close_date')} />
        <FormField label="Notes" error={errors.notes?.message}>
          <textarea className="w-full h-24 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none" {...register('notes')} />
        </FormField>
      </div>
    </Drawer>
  )
}
