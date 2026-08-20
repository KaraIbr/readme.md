import { useState, useCallback } from 'react'
import { useForm, type SubmitHandler } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Input } from '@atoms/Input/Input'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { useCreateVisit } from '../mutations/useVisitMutations'
import { visitCreateSchema, type VisitCreateFormData } from '../schemas/visit.schema'
import { useLeadList } from '../../leads/queries/useLeads'

interface VisitCreateDrawerProps {
  open: boolean
  onClose: () => void
}

export function VisitCreateDrawer({ open, onClose }: VisitCreateDrawerProps) {
  const createVisit = useCreateVisit()
  const { data: leadsData } = useLeadList()
  const [assigneeNames, setAssigneeNames] = useState<string[]>([''])

  const { register, handleSubmit, reset, formState: { errors } } = useForm<z.input<typeof visitCreateSchema>, unknown, VisitCreateFormData>({
    resolver: zodResolver(visitCreateSchema),
    defaultValues: {
      lead_id: undefined,
      scheduled_at: undefined,
      receiver_name: undefined,
      receiver_phone: undefined,
      notes: undefined,
      assignees: [],
    },
  })

  const onSubmit = useCallback<SubmitHandler<VisitCreateFormData>>(async (data) => {
    const assignees = assigneeNames.filter((n) => n.trim().length > 0).map((name) => ({ name }))
    await createVisit.mutateAsync({
      leadId: data.lead_id,
      body: {
        scheduled_at: data.scheduled_at || null,
        receiver_name: data.receiver_name || null,
        receiver_phone: data.receiver_phone || null,
        notes: data.notes || null,
        assignees,
      },
    })
    reset()
    setAssigneeNames([''])
    onClose()
  }, [createVisit, assigneeNames, reset, onClose])

  const addAssignee = useCallback(() => {
    setAssigneeNames((prev) => [...prev, ''])
  }, [])

  const removeAssignee = useCallback((index: number) => {
    setAssigneeNames((prev) => prev.filter((_, i) => i !== index))
  }, [])

  const updateAssignee = useCallback((index: number, value: string) => {
    setAssigneeNames((prev) => {
      const updated = [...prev]
      updated[index] = value
      return updated
    })
  }, [])

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="New Technical Visit"
      subtitle="Schedule a new site visit"
      editable
      actionLabel="Create Visit"
      cancelLabel="Cancel"
      onAction={handleSubmit(onSubmit)}
      actionLoading={createVisit.isPending}
      actionDisabled={createVisit.isPending}
    >
      <div className="space-y-4">
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

        <FormField label="Notes" error={errors.notes?.message}>
          <textarea
            className="w-full h-24 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
            placeholder="Optional notes..."
            {...register('notes')}
          />
        </FormField>

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
      </div>
    </Drawer>
  )
}
