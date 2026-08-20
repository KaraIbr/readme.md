import { forwardRef, useImperativeHandle, useMemo } from 'react'
import { useForm, Controller, type Resolver } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { companyCreateSchema, companyDetailSchema, type CompanyCreateFormData } from '../schemas/company.schema'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'
import { ResourceSelect } from '@molecules/ResourceSelect/ResourceSelect'
import { usePromoters } from '@features/contacts/queries/useContacts'
import type { ResourceOption } from '@molecules/ResourceSelect/ResourceSelect'

interface CompanyFormProps {
  onSubmit: (data: CompanyCreateFormData) => void
  isSubmitting?: boolean
  defaultValues?: Partial<CompanyCreateFormData>
  readOnly?: boolean
  hidePeople?: boolean
  hideSubmit?: boolean
}

export interface CompanyFormHandle {
  submitForm: () => Promise<void>
}

export const CompanyForm = forwardRef<CompanyFormHandle, CompanyFormProps>(
  ({ onSubmit, isSubmitting, defaultValues, readOnly = false, hidePeople = false, hideSubmit = false }, ref) => {
    const resolver = useMemo(
      () =>
        (hidePeople ? zodResolver(companyDetailSchema) : zodResolver(companyCreateSchema)) as Resolver<CompanyCreateFormData>,
      [hidePeople],
    )

    const {
      register,
      control,
      handleSubmit,
      formState: { errors },
    } = useForm<CompanyCreateFormData>({
      resolver,
      defaultValues: defaultValues ?? { name: '', people: [{ name: '', phone: '', email: '', position: '' }] },
    })

    const { data: promoters = [], isLoading: promotersLoading } = usePromoters()
    const promoterOptions: ResourceOption[] = useMemo(
      () => promoters.map((p) => ({ id: p.id, label: p.name, subtitle: p.phone })),
      [promoters],
    )

    const promoterName = useMemo(
      () => promoters.find((p) => p.id === defaultValues?.promoter_id)?.name,
      [promoters, defaultValues?.promoter_id],
    )

    useImperativeHandle(ref, () => ({
      submitForm: () => handleSubmit(onSubmit)(),
    }))

    if (readOnly) {
      return (
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-border p-6 space-y-4">
            <h2 className="text-lg font-semibold">Company Information</h2>
            <div className="grid grid-cols-2 gap-x-6 gap-y-4 text-sm">
              <div>
                <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">Company Name</span>
                <p className="mt-1 text-text font-medium">{defaultValues?.name ?? '—'}</p>
              </div>
              <div>
                <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">Promoter</span>
                <p className="mt-1 text-text">{promoterName ?? '—'}</p>
              </div>
              <div>
                <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">Industry</span>
                <p className="mt-1 text-text">{defaultValues?.industry ?? '—'}</p>
              </div>
              <div>
                <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">Address</span>
                <p className="mt-1 text-text">{defaultValues?.address_line ?? '—'}</p>
              </div>
              <div>
                <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">City</span>
                <p className="mt-1 text-text">{defaultValues?.city ?? '—'}</p>
              </div>
              <div>
                <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">State</span>
                <p className="mt-1 text-text">{defaultValues?.state ?? '—'}</p>
              </div>
              <div>
                <span className="text-xs font-medium text-text-secondary uppercase tracking-wider">Postal Code</span>
                <p className="mt-1 text-text">{defaultValues?.postal_code ?? '—'}</p>
              </div>
            </div>
          </div>
        </div>
      )
    }

    return (
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        <div className="bg-white rounded-xl border border-border p-6 space-y-4">
          <h2 className="text-lg font-semibold">Company Information</h2>

          <Input label="Company Name" error={errors.name?.message} {...register('name')} />
          <Controller
            name="promoter_id"
            control={control}
            render={({ field }) => (
              <ResourceSelect
                label="Promoter"
                value={field.value ?? undefined}
                onChange={(val) => field.onChange(val ?? undefined)}
                options={promoterOptions}
                error={errors.promoter_id?.message}
                placeholder="Search promoter..."
                loading={promotersLoading}
                clearable
              />
            )}
          />
          <Input label="Industry" error={errors.industry?.message} {...register('industry')} />
          <Input label="Address Line" error={errors.address_line?.message} {...register('address_line')} />

          <div className="grid grid-cols-3 gap-4">
            <Input label="City" error={errors.city?.message} {...register('city')} />
            <Input label="State" error={errors.state?.message} {...register('state')} />
            <Input label="Postal Code" error={errors.postal_code?.message} {...register('postal_code')} />
          </div>
        </div>

        {!hideSubmit && (
          <div className="flex justify-end">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Saving...' : defaultValues ? 'Save Changes' : 'Create Company'}
            </Button>
          </div>
        )}
      </form>
    )
  },
)

CompanyForm.displayName = 'CompanyForm'
