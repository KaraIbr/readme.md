import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useForm, type Resolver } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'
import { FormField } from '@molecules/FormField/FormField'
import { useCreateVisit } from '../mutations/useVisitMutations'
import { visitCreateSchema, type VisitCreateFormData } from '../schemas/visit.schema'
import { useLeadList } from '@features/leads/queries/useLeads'

export function Component() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const createVisit = useCreateVisit()
  const { data: leadsData } = useLeadList()
  const preselectedLeadId = searchParams.get('leadId') ? Number(searchParams.get('leadId')) : undefined
  const [assigneeNames, setAssigneeNames] = useState<string[]>([''])

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<VisitCreateFormData>({
    resolver: zodResolver(visitCreateSchema) as unknown as Resolver<VisitCreateFormData>,
    defaultValues: {
      lead_id: preselectedLeadId,
      scheduled_at: undefined,
      receiver_name: undefined,
      receiver_phone: undefined,
      notes: undefined,
      assignees: [],
    },
  })

  function addAssignee() {
    setAssigneeNames([...assigneeNames, ''])
  }

  function removeAssignee(index: number) {
    setAssigneeNames(assigneeNames.filter((_, i) => i !== index))
  }

  function updateAssignee(index: number, value: string) {
    const updated = [...assigneeNames]
    updated[index] = value
    setAssigneeNames(updated)
  }

  async function onSubmit(data: VisitCreateFormData) {
    const { lead_id, scheduled_at, receiver_name, receiver_phone, notes } = data
    const assignees = assigneeNames.filter(n => n.trim().length > 0).map(name => ({ name }))
    const result = await createVisit.mutateAsync({
      leadId: lead_id,
      body: {
        scheduled_at: scheduled_at || null,
        receiver_name: receiver_name || null,
        receiver_phone: receiver_phone || null,
        notes: notes || null,
        assignees,
      },
    })
    navigate(`/technical-visits/${result.id}`)
  }

  return (
    <div>
      <PageHeader title="New Technical Visit" description="Schedule a new site visit" />
      <div className="px-6 pb-6 max-w-3xl">
        <div className="bg-white rounded-xl border border-border p-6">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField label="Lead" required error={errors.lead_id?.message}>
                <select
                  className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                  {...register('lead_id', { valueAsNumber: true })}
                >
                  <option value="">Select lead...</option>
                  {(leadsData?.items ?? []).map((l) => (
                    <option key={l.id} value={l.id}>{l.title} (#{l.id})</option>
                  ))}
                </select>
              </FormField>
              <FormField label="Scheduled At" error={errors.scheduled_at?.message}>
                <Input type="datetime-local" {...register('scheduled_at')} />
              </FormField>
              <FormField label="Receiver Name" error={errors.receiver_name?.message}>
                <Input placeholder="Receiver name" {...register('receiver_name')} />
              </FormField>
              <FormField label="Receiver Phone" error={errors.receiver_phone?.message}>
                <Input placeholder="Receiver phone" {...register('receiver_phone')} />
              </FormField>
              <FormField label="Notes" className="md:col-span-2" error={errors.notes?.message}>
                <textarea
                  className="w-full h-24 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
                  placeholder="Optional notes..."
                  {...register('notes')}
                />
              </FormField>
            </div>

            <div className="border-t border-border pt-4">
              <h3 className="text-sm font-semibold text-text mb-2">Assignees</h3>
              {assigneeNames.map((name, i) => (
                <div key={i} className="flex items-center gap-2 mb-2">
                  <Input
                    placeholder="Assignee name"
                    value={name}
                    onChange={(e) => updateAssignee(i, e.target.value)}
                  />
                  {assigneeNames.length > 1 && (
                    <Button type="button" variant="secondary" onClick={() => removeAssignee(i)}>
                      Remove
                    </Button>
                  )}
                </div>
              ))}
              <Button type="button" variant="secondary" onClick={addAssignee}>
                Add Assignee
              </Button>
            </div>

            <div className="flex justify-center gap-3 pt-4">
              <Button type="button" variant="secondary" onClick={() => navigate('/technical-visits')}>Cancel</Button>
              <Button type="submit" loading={isSubmitting || createVisit.isPending}>Create Visit</Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  )
}

Component.displayName = 'VisitCreatePage'
