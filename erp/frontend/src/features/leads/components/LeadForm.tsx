import { forwardRef, useImperativeHandle } from 'react'
import { useForm } from 'react-hook-form'
import { FormField } from '@molecules/FormField/FormField'
import { LEAD_INTEREST_TYPES, INTEREST_LABELS } from '../types'
import type { LeadInterestType } from '../types'

export interface LeadFormData {
  title: string
  interest_type: LeadInterestType
  qualification_score: number | null
  notes: string | null
}

export interface LeadFormHandle {
  submitForm: () => Promise<void>
}

interface LeadFormProps {
  defaultValues?: Partial<LeadFormData>
  onSubmit: (data: LeadFormData) => Promise<void>
  isSubmitting?: boolean
  readOnly?: boolean
  hideSubmit?: boolean
}

export const LeadForm = forwardRef<LeadFormHandle, LeadFormProps>(
  ({ defaultValues, onSubmit, isSubmitting = false, readOnly = false, hideSubmit = false }, ref) => {
    const { register, handleSubmit, formState: { errors } } = useForm<LeadFormData>({
      defaultValues: {
        title: '',
        interest_type: 'Photovoltaic',
        qualification_score: null,
        notes: null,
        ...defaultValues,
      },
    })

    useImperativeHandle(ref, () => ({
      submitForm: () => handleSubmit(onSubmit)(),
    }))

    return (
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <FormField label="Title" error={errors.title?.message}>
          <input
            type="text"
            {...register('title', { required: 'Title is required' })}
            readOnly={readOnly}
            disabled={readOnly}
            className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white disabled:bg-neutral-50 disabled:text-text-tertiary read-only:bg-neutral-50 read-only:text-text-tertiary"
          />
        </FormField>

        <FormField label="Interest Type" error={errors.interest_type?.message}>
          <select
            {...register('interest_type', { required: 'Interest type is required' })}
            disabled={readOnly}
            className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white disabled:bg-neutral-50 disabled:text-text-tertiary"
          >
            {LEAD_INTEREST_TYPES.map((t) => (
              <option key={t} value={t}>{INTEREST_LABELS[t]}</option>
            ))}
          </select>
        </FormField>

        <FormField label="Qualification Score (0-100)" error={errors.qualification_score?.message}>
          <input
            type="number"
            {...register('qualification_score', {
              setValueAs: (v) => (v === '' || v == null ? null : Number(v)),
              min: { value: 0, message: 'Min 0' },
              max: { value: 100, message: 'Max 100' },
            })}
            readOnly={readOnly}
            disabled={readOnly}
            className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white disabled:bg-neutral-50 disabled:text-text-tertiary read-only:bg-neutral-50 read-only:text-text-tertiary"
          />
        </FormField>

        <FormField label="Notes">
          <textarea
            {...register('notes')}
            readOnly={readOnly}
            disabled={readOnly}
            rows={4}
            className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-white disabled:bg-neutral-50 disabled:text-text-tertiary read-only:bg-neutral-50 read-only:text-text-tertiary resize-none"
          />
        </FormField>

        {!hideSubmit && !readOnly && (
          <div className="flex justify-end pt-2">
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary-dark transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Saving...' : 'Save'}
            </button>
          </div>
        )}
      </form>
    )
  },
)

LeadForm.displayName = 'LeadForm'
