import { useRef, useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { useCreateCompany } from '../mutations/useCompanyMutations'
import { CompanyForm, type CompanyFormHandle } from './CompanyForm'
import type { CompanyCreateFormData } from '../schemas/company.schema'

interface CompanyCreateDrawerProps {
  open: boolean
  onClose: () => void
}

export function CompanyCreateDrawer({ open, onClose }: CompanyCreateDrawerProps) {
  const createMutation = useCreateCompany()
  const formRef = useRef<CompanyFormHandle>(null)

  const handleSave = useCallback(async () => {
    await formRef.current?.submitForm()
  }, [])

  const handleFormSubmit = useCallback(
    async (data: CompanyCreateFormData) => {
      await createMutation.mutateAsync(data)
      onClose()
    },
    [createMutation, onClose],
  )

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="New Company"
      subtitle="Create a new company contact"
      editable
      actionLabel="Create Company"
      cancelLabel="Cancel"
      onAction={handleSave}
      actionLoading={createMutation.isPending}
      actionDisabled={createMutation.isPending}
    >
      <CompanyForm
        ref={formRef}
        onSubmit={handleFormSubmit}
        isSubmitting={createMutation.isPending}
        hideSubmit
      />
    </Drawer>
  )
}
