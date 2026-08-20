import { useNavigate } from 'react-router-dom'
import { useForm, type SubmitHandler } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'
import { FormField } from '@molecules/FormField/FormField'
import { useCreateLead } from '../mutations/useLeadMutations'
import { leadCreateSchema, type LeadCreateFormData } from '../schemas/lead.schema'
import { LEAD_INTEREST_TYPES, INTEREST_LABELS } from '../types'

export function Component() {
  const navigate = useNavigate()
  const createLead = useCreateLead()
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<LeadCreateFormData>({
    resolver: zodResolver(leadCreateSchema),
    defaultValues: {
      title: '',
      interest_type: undefined,
      qualification_score: undefined,
      notes: undefined,
    },
  })

  const onSubmit: SubmitHandler<LeadCreateFormData> = async (data) => {
    const result = await createLead.mutateAsync(data)
    navigate(`/leads/${result.id}`)
  }

  return (
    <div>
      <PageHeader title="New Lead" description="Create a new sales lead" />
      <div className="px-6 pb-6 max-w-3xl">
        <div className="bg-white rounded-xl border border-border p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField label="Title" required error={errors.title?.message}>
                <Input placeholder="Lead title" {...register('title')} />
              </FormField>
              <FormField label="Contact ID" required error={errors.contact_id?.message}>
                <Input type="number" placeholder="Contact ID" {...register('contact_id', { valueAsNumber: true })} />
              </FormField>
              <FormField label="Interest Type" required error={errors.interest_type?.message}>
                <select
                  className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                  {...register('interest_type')}
                >
                  <option value="">Select interest...</option>
                  {LEAD_INTEREST_TYPES.map((t) => (
                    <option key={t} value={t}>{INTEREST_LABELS[t]}</option>
                  ))}
                </select>
              </FormField>
              <FormField label="Qualification Score (0-100)" error={errors.qualification_score?.message}>
                <Input type="number" min={0} max={100} placeholder="Score" {...register('qualification_score', { valueAsNumber: true })} />
              </FormField>
              <FormField label="Notes" className="md:col-span-2" error={errors.notes?.message}>
                <textarea
                  className="w-full h-24 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
                  placeholder="Optional notes..."
                  {...register('notes')}
                />
              </FormField>
            </div>
            <div className="flex justify-center gap-3 pt-4">
              <Button type="button" variant="secondary" onClick={() => navigate('/leads')}>Cancel</Button>
              <Button type="submit" loading={isSubmitting || createLead.isPending}>Create Lead</Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

Component.displayName = 'LeadCreatePage'
