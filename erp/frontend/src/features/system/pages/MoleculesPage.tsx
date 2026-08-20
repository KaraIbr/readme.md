import { useState } from 'react'
import { SearchInput } from '@molecules/SearchInput/SearchInput'
import { StatusBadge } from '@molecules/StatusBadge/StatusBadge'
import { FormField } from '@molecules/FormField/FormField'
import { EmptyState } from '@molecules/EmptyState/EmptyState'
import { Input } from '@atoms/Input/Input'
import { Button } from '@atoms/Button/Button'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-10">
      <h2 className="text-h4 text-text mb-5">{title}</h2>
      <div className="p-6 rounded-lg border border-border bg-white">
        {children}
      </div>
    </div>
  )
}

export function Component() {
  const [search, setSearch] = useState('')

  return (
    <div>
      <h1 className="text-h2 text-text mb-8">Molecules</h1>

      <Section title="SearchInput">
        <div className="max-w-sm">
          <SearchInput
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onClear={() => setSearch('')}
            placeholder="Search leads, contacts..."
          />
        </div>
      </Section>

      <Section title="StatusBadge">
        <div className="flex items-center gap-3 flex-wrap">
          <StatusBadge status="active" />
          <StatusBadge status="pending" />
          <StatusBadge status="completed" />
          <StatusBadge status="cancelled" />
          <StatusBadge status="draft" />
        </div>
      </Section>

      <Section title="FormField">
        <div className="space-y-5 max-w-sm">
          <FormField label="Full Name" required>
            <Input placeholder="Enter your name" />
          </FormField>
          <FormField label="Email" error="Invalid email address">
            <Input placeholder="Enter your email" error />
          </FormField>
          <FormField label="Description" hint="Provide a brief description">
            <Input placeholder="Optional description" />
          </FormField>
        </div>
      </Section>

      <Section title="EmptyState">
        <EmptyState
          title="No leads found"
          description="There are no leads matching your filters. Try adjusting your search criteria."
          action={<Button variant="primary">Create Lead</Button>}
        />
      </Section>
    </div>
  )
}

Component.displayName = 'MoleculesPage'
