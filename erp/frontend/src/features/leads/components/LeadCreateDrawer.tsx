import { useCallback } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Input } from '@atoms/Input/Input'
import { FormField } from '@molecules/FormField/FormField'
import { useCreateLead } from '../mutations/useLeadMutations'
import { leadCreateSchema, type LeadCreateFormData } from '../schemas/lead.schema'
import { LEAD_INTEREST_TYPES, INTEREST_LABELS } from '../types'

interface LeadCreateDrawerProps {
  open: boolean
  onClose: () => void
}

export function LeadCreateDrawer({ open, onClose }: LeadCreateDrawerProps) {
  const createLead = useCreateLead()
  const { register, handleSubmit, reset, formState: { errors } } = useForm<LeadCreateFormData>({
    resolver: zodResolver(leadCreateSchema),
    defaultValues: {
      title: '',
      interest_type: undefined,
      qualification_score: undefined,
      notes: undefined,
    },
  })

  const onSubmit = useCallback(async (data: LeadCreateFormData) => {
    await createLead.mutateAsync(data)
    reset()
    onClose()
  }, [createLead, reset, onClose])

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="New Lead"
      subtitle="Create a new sales lead"
      editable
      actionLabel="Create Lead"
      cancelLabel="Cancel"
      onAction={handleSubmit(onSubmit)}
      actionLoading={createLead.isPending}
      actionDisabled={createLead.isPending}
    >
      <div className="space-y-4">
        <Input label="Title" required error={errors.title?.message} {...register('title')} />
        <Input label="Contact ID" type="number" required error={errors.contact_id?.message} {...register('contact_id', { valueAsNumber: true })} />
        <FormField label="Interest Type" required error={errors.interest_type?.message}>
          <select className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('interest_type')}>
            <option value="">Select interest...</option>
            {LEAD_INTEREST_TYPES.map((t) => (
              <option key={t} value={t}>{INTEREST_LABELS[t]}</option>
            ))}
          </select>
        </FormField>
        <Input label="Score (0-100)" type="number" min={0} max={100} error={errors.qualification_score?.message} {...register('qualification_score', { valueAsNumber: true })} />
        <FormField label="Notes" error={errors.notes?.message}>
          <textarea className="w-full h-24 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none" {...register('notes')} />
        </FormField>
      </div>
    </Drawer>
  )
}
