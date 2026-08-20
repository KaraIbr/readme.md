import { useRef, useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Spinner } from '@atoms/Spinner/Spinner'
import { SectionHeading } from '@atoms/SectionHeading/SectionHeading'
import { useCompany } from '../queries/useCompanies'
import { useUpdateCompany } from '../mutations/useCompanyMutations'
import { CompanyForm, type CompanyFormHandle } from './CompanyForm'
import { CompanyPersonList } from './CompanyPersonList'
import { useEffectivePermissions } from '@features/permissions/queries/useUserPermissions'
import type { CompanyCreateFormData } from '../schemas/company.schema'

interface CompanyDetailDrawerProps {
  companyId: number | null
  onClose: () => void
}

export function CompanyDetailDrawer({ companyId, onClose }: CompanyDetailDrawerProps) {
  const { data: company, isLoading } = useCompany(companyId ?? 0)
  const updateMutation = useUpdateCompany()
  const { role } = useEffectivePermissions()
  const isAdmin = role === 'ADMIN'
  const formRef = useRef<CompanyFormHandle>(null)

  const handleSave = useCallback(async () => {
    await formRef.current?.submitForm()
  }, [])

  const handleFormSubmit = useCallback(
    async (data: CompanyCreateFormData) => {
      if (!companyId) return
      const { people: _, ...updateData } = data
      await updateMutation.mutateAsync({ id: companyId, data: updateData })
      onClose()
    },
    [companyId, updateMutation, onClose],
  )

  return (
    <Drawer
      open={companyId !== null}
      onClose={onClose}
      title={company?.name ?? 'Company'}
      subtitle={company ? (company.industry ?? 'No industry') : 'Loading...'}
      editable={isAdmin}
      actionLabel="Save"
      cancelLabel="Cancel"
      onAction={handleSave}
      actionLoading={updateMutation.isPending}
      actionDisabled={updateMutation.isPending}
    >
      {isLoading || !company ? (
        <div className="flex items-center justify-center h-64">
          <Spinner />
        </div>
      ) : (
        <div className="space-y-2">
          <SectionHeading>Company Information</SectionHeading>
          <CompanyForm
            ref={formRef}
            defaultValues={{
              name: company.name,
              promoter_id: company.promoter_id ?? undefined,
              industry: company.industry ?? undefined,
              address_line: company.address_line ?? undefined,
              city: company.city ?? undefined,
              state: company.state ?? undefined,
              postal_code: company.postal_code ?? undefined,
            }}
            onSubmit={handleFormSubmit}
            isSubmitting={updateMutation.isPending}
            readOnly={!isAdmin}
            hidePeople
            hideSubmit
          />

          <SectionHeading>Contact People</SectionHeading>
          <CompanyPersonList companyId={company.id} readOnly={!isAdmin} />
        </div>
      )}
    </Drawer>
  )
}
