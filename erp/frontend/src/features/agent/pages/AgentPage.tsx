import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { AgentChat } from '../components/AgentChat'

export function Component() {
  return (
    <div className="flex flex-col h-full">
      <PageHeader title="Agent" description="CRM assistant powered by AI" />
      <AgentChat />
    </div>
  )
}

Component.displayName = 'AgentPage'
