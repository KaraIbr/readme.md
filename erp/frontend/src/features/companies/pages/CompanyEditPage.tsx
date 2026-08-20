import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { useParams } from 'react-router-dom'

export function Component() {
  const { id } = useParams<{ id: string }>()
  return (
    <div>
      <PageHeader title={`Edit Company #${id}`} description="Update company information" />
      <p style={{ padding: '2rem', color: '#6b7280' }}>Coming soon</p>
    </div>
  )
}
