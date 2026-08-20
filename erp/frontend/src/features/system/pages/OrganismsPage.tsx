import { useState } from 'react'
import { DataTable } from '@organisms/DataTable/DataTable'
import { FilterBar } from '@organisms/FilterBar/FilterBar'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'
import { Badge } from '@atoms/Badge/Badge'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-10">
      <h2 className="text-h4 text-text mb-5">{title}</h2>
      {children}
    </div>
  )
}

interface SampleData {
  id: string
  name: string
  email: string
  role: string
  status: string
}

const sampleData: SampleData[] = [
  { id: '1', name: 'Alice Silva', email: 'alice@example.com', role: 'Admin', status: 'Active' },
  { id: '2', name: 'Bob Santos', email: 'bob@example.com', role: 'Editor', status: 'Active' },
  { id: '3', name: 'Carol Oliveira', email: 'carol@example.com', role: 'Viewer', status: 'Inactive' },
  { id: '4', name: 'David Lima', email: 'david@example.com', role: 'Editor', status: 'Active' },
  { id: '5', name: 'Eva Costa', email: 'eva@example.com', role: 'Admin', status: 'Active' },
]

export function Component() {
  const [search, setSearch] = useState('')

  const columns = [
    { key: 'name', header: 'Name' },
    { key: 'email', header: 'Email' },
    { key: 'role', header: 'Role' },
    {
      key: 'status',
      header: 'Status',
      render: (item: SampleData) => (
        <Badge variant={item.status === 'Active' ? 'success' : 'default'} size="sm">
          {item.status}
        </Badge>
      ),
    },
  ]

  return (
    <div>
      <h1 className="text-h2 text-text mb-8">Organisms</h1>

      <Section title="PageHeader">
        <PageHeader
          title="Leads"
          description="Manage and track your sales leads"
          actions={
            <>
              <Button variant="secondary">Export</Button>
              <Button variant="primary">Create Lead</Button>
            </>
          }
        />
      </Section>

      <Section title="FilterBar">
        <FilterBar>
          <Input
            placeholder="Search..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            inputSize="sm"
            className="w-64"
          />
        </FilterBar>
      </Section>

      <Section title="DataTable">
        <DataTable
          columns={columns}
          data={sampleData}
          keyExtractor={(item) => item.id}
        />
      </Section>

      <Section title="DataTable (Empty)">
        <DataTable
          columns={columns}
          data={[]}
          keyExtractor={(item) => item.id}
          emptyTitle="No results"
          emptyDescription="No data matches your current filters."
        />
      </Section>

      <Section title="DataTable (Loading)">
        <DataTable
          columns={columns}
          data={[]}
          keyExtractor={(item) => item.id}
          loading
        />
      </Section>
    </div>
  )
}

Component.displayName = 'OrganismsPage'
