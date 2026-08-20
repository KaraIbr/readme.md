import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { ContactForm, usePromoters, useCreateContact } from '@features/contacts'
import type { ContactCreateFormData } from '@features/contacts/schemas/contact.schema'

export function Component() {
  const navigate = useNavigate()
  const { data: promoters } = usePromoters()
  const createContact = useCreateContact()

  async function onSubmit(data: ContactCreateFormData) {
    await createContact.mutateAsync(data)
    navigate('/admin/contacts')
  }

  return (
    <div>
      <PageHeader title="New Contact" description="Create a new contact or company (admin)" />
      <div className="px-6 pb-6 max-w-2xl">
        <div className="bg-white rounded-xl border border-border p-6">
          <ContactForm
            promoters={promoters ?? []}
            onSubmit={onSubmit}
            isSubmitting={createContact.isPending}
          />
        </div>
      </div>
    </div>
  )
}

Component.displayName = 'AdminContactCreatePage'
