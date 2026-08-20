import { useState } from 'react'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'
import { Checkbox } from '@atoms/Checkbox/Checkbox'
import { Badge } from '@atoms/Badge/Badge'
import { Avatar } from '@atoms/Avatar/Avatar'
import { Spinner } from '@atoms/Spinner/Spinner'

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

function Row({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 flex-wrap mb-3 last:mb-0">
      {children}
    </div>
  )
}

export function Component() {
  const [inputValue, setInputValue] = useState('')
  const [checked, setChecked] = useState(false)

  return (
    <div>
      <h1 className="text-h2 text-text mb-8">Atoms</h1>

      <Section title="Button">
        <Row>
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger">Danger</Button>
        </Row>
        <Row>
          <Button size="sm">Small</Button>
          <Button size="md">Medium</Button>
          <Button size="lg">Large</Button>
        </Row>
        <Row>
          <Button loading>Loading</Button>
          <Button disabled>Disabled</Button>
        </Row>
        <Row>
          <Button variant="primary">Left Icon</Button>
          <Button variant="secondary">Right Icon</Button>
        </Row>
      </Section>

      <Section title="Input">
        <div className="space-y-4 max-w-sm">
          <Input placeholder="Default input" />
          <Input inputSize="sm" placeholder="Small input" />
          <Input inputSize="lg" placeholder="Large input" />
          <Input placeholder="With error" error />
          <Input placeholder="Disabled" disabled />
          <Input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="With clear"
          />
        </div>
      </Section>

      <Section title="Checkbox">
        <div className="space-y-3">
          <Checkbox
            label="Unchecked"
            checked={checked}
            onChange={(e) => setChecked(e.target.checked)}
          />
          <Checkbox
            label="Checked"
            checked={true}
            onChange={() => {}}
          />
          <Checkbox
            label="Disabled"
            disabled
          />
          <Checkbox
            label="Disabled checked"
            disabled
            checked
            onChange={() => {}}
          />
        </div>
      </Section>

      <Section title="Badge">
        <Row>
          <Badge variant="default">Default</Badge>
          <Badge variant="success">Success</Badge>
          <Badge variant="warning">Warning</Badge>
          <Badge variant="danger">Danger</Badge>
          <Badge variant="info">Info</Badge>
        </Row>
        <Row>
          <Badge size="sm">Small</Badge>
          <Badge size="md">Medium</Badge>
        </Row>
      </Section>

      <Section title="Avatar">
        <Row>
          <Avatar size="sm" initials="JD" />
          <Avatar size="md" initials="JD" />
          <Avatar size="lg" initials="JD" />
        </Row>
      </Section>

      <Section title="Spinner">
        <Row>
          <Spinner size="sm" />
          <Spinner size="md" />
          <Spinner size="lg" />
        </Row>
      </Section>
    </div>
  )
}

Component.displayName = 'AtomsPage'
