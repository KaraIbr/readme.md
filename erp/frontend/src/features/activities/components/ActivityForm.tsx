import { forwardRef, useImperativeHandle, useMemo } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { activityCreateSchema, type ActivityCreateFormData } from '../schemas/activity.schema'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'
import { FormField } from '@molecules/FormField/FormField'
import { ResourceSelect } from '@molecules/ResourceSelect/ResourceSelect'
import type { ResourceOption } from '@molecules/ResourceSelect/ResourceSelect'
import { ACTIVITY_TYPES, ACTIVITY_LABELS } from '../types'
import { useContacts } from '@features/contacts'
import { useLeadList } from '@features/leads'
import { useUsers } from '@features/admin'

interface ActivityFormProps {
  onSubmit: (data: ActivityCreateFormData) => void
  isSubmitting?: boolean
  defaultValues?: Partial<ActivityCreateFormData>
  hideSubmit?: boolean
}

export interface ActivityFormHandle {
  submitForm: () => Promise<void>
}

export const ActivityForm = forwardRef<ActivityFormHandle, ActivityFormProps>(
  ({ onSubmit, isSubmitting, defaultValues, hideSubmit = false }, ref) => {
    const {
      register,
      handleSubmit,
      setValue,
      watch,
      formState: { errors },
    } = useForm<z.input<typeof activityCreateSchema>, unknown, ActivityCreateFormData>({
      resolver: zodResolver(activityCreateSchema),
      defaultValues: defaultValues ?? { activity_type: 'NOTE' },
    })

    const contactId = watch('contact_id') as number | undefined
    const leadId = watch('lead_id') as number | undefined
    const assignedTo = watch('assigned_to') as number | undefined

    const { data: contactsPage } = useContacts()
    const { data: leadsData } = useLeadList()
    const { data: users } = useUsers()

    const contactOptions: ResourceOption[] = useMemo(
      () =>
        (contactsPage?.items ?? []).map((c) => ({
          id: c.id,
          label: c.name,
          subtitle: c.email ?? undefined,
        })),
      [contactsPage],
    )

    const leadOptions: ResourceOption[] = useMemo(
      () =>
        (leadsData?.items ?? []).map((l) => ({
          id: l.id,
          label: l.title,
          subtitle: l.interest_type ?? undefined,
        })),
      [leadsData],
    )

    const userOptions: ResourceOption[] = useMemo(
      () =>
        (users ?? []).map((u) => ({
          id: u.id,
          label: u.full_name ?? u.email,
          subtitle: u.email,
        })),
      [users],
    )

    useImperativeHandle(ref, () => ({
      submitForm: () => handleSubmit(onSubmit)(),
    }))

    return (
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="bg-white rounded-xl border border-border p-6 space-y-4">
          <h2 className="text-lg font-semibold">Activity Details</h2>

          <FormField label="Type" required error={errors.activity_type?.message}>
            <select
              {...register('activity_type')}
              className="w-full rounded-lg border border-border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            >
              {ACTIVITY_TYPES.map((t) => (
                <option key={t} value={t}>{ACTIVITY_LABELS[t]}</option>
              ))}
            </select>
          </FormField>

          <Input label="Title" error={errors.title?.message} {...register('title')} />

          <FormField label="Description" error={errors.description?.message}>
            <textarea
              {...register('description')}
              rows={4}
              className="w-full rounded-lg border border-border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
            />
          </FormField>

          <ResourceSelect
            label="Contact"
            value={contactId}
            onChange={(v) => setValue('contact_id', v ?? undefined)}
            options={contactOptions}
            placeholder="Search contacts..."
            error={errors.contact_id?.message}
          />

          <ResourceSelect
            label="Lead"
            value={leadId}
            onChange={(v) => setValue('lead_id', v ?? undefined)}
            options={leadOptions}
            placeholder="Search leads..."
            error={errors.lead_id?.message}
          />

          <ResourceSelect
            label="Assigned To"
            value={assignedTo}
            onChange={(v) => setValue('assigned_to', v ?? undefined)}
            options={userOptions}
            placeholder="Search users..."
            error={errors.assigned_to?.message}
          />

          <Input
            label="Scheduled At"
            type="datetime-local"
            error={errors.scheduled_at?.message}
            {...register('scheduled_at')}
          />
        </div>

        {!hideSubmit && (
          <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : 'Create Activity'}
            </Button>
          </div>
        )}
      </form>
    )
  },
)

ActivityForm.displayName = 'ActivityForm'
