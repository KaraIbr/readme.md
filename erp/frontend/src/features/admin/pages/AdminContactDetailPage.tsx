import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Badge } from '@atoms/Badge/Badge'
import { Spinner } from '@atoms/Spinner/Spinner'
import { EmptyState } from '@molecules/EmptyState/EmptyState'
import {
  useContact,
  useCompanyPeople,
  useUpdateContact,
  useDeleteContact,
  usePromoters,
  ContactForm,
} from '@features/contacts'
import type { ContactCreateFormData } from '@features/contacts/schemas/contact.schema'

export function Component() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const contactId = Number(id)
  const { data: contact, isLoading, error } = useContact(contactId)
  const { data: people } = useCompanyPeople(contactId)
  const { data: promoters } = usePromoters()
  const updateContact = useUpdateContact(contactId)
  const deleteContact = useDeleteContact()
  const [editing, setEditing] = useState(false)

  async function handleUpdate(data: ContactCreateFormData) {
    await updateContact.mutateAsync(data)
    setEditing(false)
  }

  async function handleDelete() {
    if (window.confirm('Are you sure you want to delete this contact?')) {
      await deleteContact.mutateAsync(contactId)
      navigate('/admin/contacts')
    }
  }

  if (isLoading) {
    return <div className="flex justify-center py-16"><Spinner size="lg" /></div>
  }

  if (error || !contact) {
    return <EmptyState title="Contact not found" description="The contact you're looking for doesn't exist" />
  }

  if (editing) {
    return (
      <div>
        <PageHeader
          title={`Edit: ${contact.name}`}
          description="Update contact information"
          actions={
            <Button variant="secondary" onClick={() => setEditing(false)}>Cancel</Button>
          }
        />
        <div className="px-6 pb-6 max-w-2xl">
          <div className="bg-white rounded-xl border border-border p-6">
            <ContactForm
              initialData={contact}
              promoters={promoters ?? []}
              onSubmit={handleUpdate}
              isSubmitting={updateContact.isPending}
            />
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title={contact.name}
        description={`${contact.type} contact`}
        actions={
          <div className="flex gap-2">
            <Button variant="secondary" onClick={() => navigate('/admin/contacts')}>Back</Button>
            <Button variant="primary" onClick={() => setEditing(true)}>Edit</Button>
            <Button variant="danger" onClick={handleDelete} loading={deleteContact.isPending}>Delete</Button>
          </div>
        }
      />
      <div className="px-6 pb-6 max-w-2xl space-y-6">
        <div className="bg-white rounded-xl border border-border p-6 space-y-4">
          <Badge variant={contact.type === 'INDIVIDUAL' ? 'default' : 'info'} size="sm">
            {contact.type}
          </Badge>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-caption text-text-tertiary">Name</p>
              <p className="text-body-medium text-text">{contact.name}</p>
            </div>
            {contact.phone && (
              <div>
                <p className="text-caption text-text-tertiary">Phone</p>
                <p className="text-body-medium text-text">{contact.phone}</p>
              </div>
            )}
            {contact.email && (
              <div>
                <p className="text-caption text-text-tertiary">Email</p>
                <p className="text-body-medium text-text">{contact.email}</p>
              </div>
            )}
            {contact.industry && (
              <div>
                <p className="text-caption text-text-tertiary">Industry</p>
                <p className="text-body-medium text-text">{contact.industry}</p>
              </div>
            )}
            {contact.city && (
              <div>
                <p className="text-caption text-text-tertiary">City</p>
                <p className="text-body-medium text-text">{contact.city}</p>
              </div>
            )}
          </div>
        </div>

        {contact.type === 'COMPANY' && people && people.length > 0 && (
          <div className="bg-white rounded-xl border border-border p-6">
            <h3 className="text-h6 text-text mb-4">Company People</h3>
            <div className="space-y-3">
              {people.map((person) => (
                <div key={person.id} className="flex items-center justify-between py-2 border-b border-border-light last:border-0">
                  <div>
                    <p className="text-body-medium text-text">{person.name}</p>
                    <p className="text-small text-text-tertiary">{person.position}</p>
                  </div>
                  <div className="text-right text-small text-text-secondary">
                    <p>{person.phone}</p>
                    {person.email && <p>{person.email}</p>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

Component.displayName = 'AdminContactDetailPage'
