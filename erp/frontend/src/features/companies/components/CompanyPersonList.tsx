import { useState } from 'react'
import { Button } from '@atoms/Button/Button'
import { DataTable } from '@organisms/DataTable/DataTable'
import type { Column } from '@organisms/DataTable/DataTable'
import { useCompanyPeople } from '../queries/useCompanies'
import { useCreateCompanyPerson, useDeleteCompanyPerson } from '../mutations/useCompanyMutations'
import type { CompanyPerson, CompanyPersonCreate } from '../types'

interface CompanyPersonListProps {
  companyId: number
  readOnly?: boolean
}

export function CompanyPersonList({ companyId, readOnly = false }: CompanyPersonListProps) {
  const { data: people, isLoading } = useCompanyPeople(companyId)
  const createMutation = useCreateCompanyPerson(companyId)
  const deleteMutation = useDeleteCompanyPerson(companyId)
  const [showForm, setShowForm] = useState(false)
  const [newPerson, setNewPerson] = useState<CompanyPersonCreate>({
    name: '',
    phone: '',
    email: '',
    position: '',
  })

  const handleAdd = async () => {
    if (!newPerson.name || !newPerson.phone || !newPerson.position) return
    await createMutation.mutateAsync(newPerson)
    setNewPerson({ name: '', phone: '', email: '', position: '' })
    setShowForm(false)
  }

  const columns: Column<CompanyPerson>[] = [
    { key: 'name', header: 'Name' },
    { key: 'phone', header: 'Phone' },
    { key: 'email', header: 'Email' },
    { key: 'position', header: 'Position' },
    ...(!readOnly
      ? [
          {
            key: 'actions' as const,
            header: '' as const,
            render: (p: CompanyPerson) => (
              <button
                className="text-red-600 hover:text-red-800 text-sm"
                onClick={() => deleteMutation.mutate(p.id)}
              >
                Delete
              </button>
            ),
          },
        ]
      : []),
  ]

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-md font-semibold">Contact People</h3>
        {!readOnly && (
          <Button size="sm" variant="secondary" onClick={() => setShowForm(!showForm)}>
            {showForm ? 'Cancel' : 'Add Person'}
          </Button>
        )}
      </div>

      {showForm && !readOnly && (
        <div className="border border-border rounded-lg p-4 space-y-3 bg-gray-50">
          <div className="grid grid-cols-2 gap-4">
            <input
              placeholder="Name"
              value={newPerson.name}
              onChange={(e) => setNewPerson((p) => ({ ...p, name: e.target.value }))}
              className="border border-border rounded-lg px-3 py-2 text-sm"
            />
            <input
              placeholder="Phone"
              value={newPerson.phone}
              onChange={(e) => setNewPerson((p) => ({ ...p, phone: e.target.value }))}
              className="border border-border rounded-lg px-3 py-2 text-sm"
            />
            <input
              placeholder="Email"
              value={newPerson.email ?? ''}
              onChange={(e) => setNewPerson((p) => ({ ...p, email: e.target.value }))}
              className="border border-border rounded-lg px-3 py-2 text-sm"
            />
            <input
              placeholder="Position"
              value={newPerson.position}
              onChange={(e) => setNewPerson((p) => ({ ...p, position: e.target.value }))}
              className="border border-border rounded-lg px-3 py-2 text-sm"
            />
          </div>
          <div className="flex justify-end">
            <Button size="sm" onClick={handleAdd} disabled={createMutation.isPending}>
              Save Person
            </Button>
          </div>
        </div>
      )}

      <DataTable<CompanyPerson>
        columns={columns}
        data={people ?? []}
        keyExtractor={(p) => String(p.id)}
        loading={isLoading}
        emptyTitle="No contact people"
        emptyDescription="Add a contact person for this company"
      />
    </div>
  )
}
