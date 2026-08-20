import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { DataTable } from '@organisms/DataTable/DataTable'
import { Button } from '@atoms/Button/Button'
import { Badge } from '@atoms/Badge/Badge'
import { AdvancedFilter } from '@organisms/AdvancedFilter/AdvancedFilter'
import type { FilterField } from '@organisms/AdvancedFilter/AdvancedFilter'
import { useContacts } from '@features/contacts'
import { useDeleteContact } from '@features/contacts/mutations/useDeleteContact'
import type { ContactRead } from '@features/contacts/types'

const filterFields: FilterField[] = [
  { key: 'search', label: 'Search', type: 'text', placeholder: 'Search by name, email, or city...' },
  { key: 'typeFilter', label: 'Type', type: 'select', options: [
    { label: 'Individual', value: 'INDIVIDUAL' },
    { label: 'Company', value: 'COMPANY' },
  ]},
]

function ConfirmDeleteDialog({ contact, onConfirm, onCancel, loading }: { contact: ContactRead; onConfirm: () => void; onCancel: () => void; loading: boolean }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/30" onClick={onCancel}>
      <div className="bg-white rounded-xl border border-border p-6 max-w-sm w-full mx-4 shadow-lg" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-h6 text-text mb-2">Delete Contact</h3>
        <p className="text-small text-text-secondary mb-6">
          Are you sure you want to delete <span className="font-medium text-text">{contact.name}</span>? This action cannot be undone.
        </p>
        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={onCancel} disabled={loading}>Cancel</Button>
          <Button variant="danger" onClick={onConfirm} loading={loading}>Delete</Button>
        </div>
      </div>
    </div>
  )
}

export function Component() {
  const navigate = useNavigate()
  const { data, isLoading } = useContacts()
  const deleteContact = useDeleteContact()
  const [confirmDelete, setConfirmDelete] = useState<ContactRead | null>(null)
  const [filters, setFilters] = useState<Record<string, string>>({})

  const filtered = useMemo(() => {
    let result = data?.items ?? []
    const search = filters.search ?? ''
    const typeFilter = filters.typeFilter ?? ''
    if (search) {
      const q = search.toLowerCase()
      result = result.filter(c =>
        c.name.toLowerCase().includes(q) ||
        (c.email ?? '').toLowerCase().includes(q) ||
        (c.city ?? '').toLowerCase().includes(q)
      )
    }
    if (typeFilter) {
      result = result.filter(c => c.type === typeFilter)
    }
    return result
  }, [data, filters])

  const handleFilterChange = (key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value }))
  }

  const handleClearFilters = () => {
    setFilters({})
  }

  async function handleDelete() {
    if (!confirmDelete) return
    await deleteContact.mutateAsync(confirmDelete.id)
    setConfirmDelete(null)
  }

  const columns = [
    {
      key: 'name',
      header: 'Name',
      render: (c: ContactRead) => (
        <button
          type="button"
          onClick={() => navigate(`/admin/contacts/${c.id}`)}
          className="font-medium text-primary hover:underline text-left"
        >
          {c.name}
        </button>
      ),
    },
    {
      key: 'type',
      header: 'Type',
      render: (c: ContactRead) => (
        <Badge variant={c.type === 'INDIVIDUAL' ? 'default' : 'info'} size="sm">
          {c.type}
        </Badge>
      ),
    },
    { key: 'city', header: 'City' },
    { key: 'email', header: 'Email' },
    { key: 'phone', header: 'Phone' },
    {
      key: 'actions',
      header: 'Actions',
      render: (c: ContactRead) => (
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => navigate(`/admin/contacts/${c.id}`)}
            className="text-sm text-primary hover:underline"
          >
            Edit
          </button>
          <span className="text-text-tertiary">|</span>
          <button
            type="button"
            onClick={() => setConfirmDelete(c)}
            className="text-sm text-danger hover:underline"
          >
            Delete
          </button>
        </div>
      ),
    },
  ]

  return (
    <div>
      <PageHeader
        title="Manage Contacts"
        description="View and manage all contacts in the system"
        actions={
          <Button onClick={() => navigate('/admin/contacts/new')}>New Contact</Button>
        }
      />
      <div className="px-6 pb-6 space-y-4">
        <div className="bg-white rounded-xl border border-border p-4">
          <AdvancedFilter
            fields={filterFields}
            values={filters}
            onChange={handleFilterChange}
            onClear={handleClearFilters}
          />
        </div>
        <DataTable<ContactRead>
          columns={columns}
          data={filtered}
          keyExtractor={(c) => String(c.id)}
          loading={isLoading}
          emptyTitle="No contacts found"
          emptyDescription="Create your first contact to get started"
        />
      </div>

      {confirmDelete && (
        <ConfirmDeleteDialog
          contact={confirmDelete}
          onConfirm={handleDelete}
          onCancel={() => setConfirmDelete(null)}
          loading={deleteContact.isPending}
        />
      )}
    </div>
  )
}

Component.displayName = 'AdminContactListPage'
