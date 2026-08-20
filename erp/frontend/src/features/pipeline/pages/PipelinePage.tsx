import { useState } from 'react'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { LeadBoard } from '../components/LeadBoard'
import { ProposalBoard } from '../components/ProposalBoard'

export function Component() {
  const [tab, setTab] = useState<'leads' | 'proposals'>('leads')

  return (
    <div>
      <PageHeader title="Pipeline" description="Lead and Proposal stage management" />
      <div className="px-6 pb-6">
        <div className="flex gap-4 mb-6 border-b border-border">
          <button
            type="button"
            onClick={() => setTab('leads')}
            className={`pb-3 text-sm font-medium transition-colors border-b-2 -mb-px ${
              tab === 'leads' ? 'text-primary border-primary' : 'text-text-secondary border-transparent hover:text-text'
            }`}
          >
            Leads
          </button>
          <button
            type="button"
            onClick={() => setTab('proposals')}
            className={`pb-3 text-sm font-medium transition-colors border-b-2 -mb-px ${
              tab === 'proposals' ? 'text-primary border-primary' : 'text-text-secondary border-transparent hover:text-text'
            }`}
          >
            Proposals
          </button>
        </div>

        {tab === 'leads' ? <LeadBoard /> : <ProposalBoard />}
      </div>
    </div>
  )
}

Component.displayName = 'PipelinePage'
