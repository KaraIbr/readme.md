import { useParams, useNavigate } from 'react-router-dom'
import { useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Spinner } from '@atoms/Spinner/Spinner'
import { EmptyState } from '@molecules/EmptyState/EmptyState'
import { useProposal } from '../queries/useProposals'
import { queryKeys } from '@lib/query-keys'
import { ProposalInfoCard } from '../components/ProposalInfoCard'
import { ProposalStageSection } from '../components/ProposalStageSection'
import { ProposalPVDetails } from '../components/ProposalPVDetails'
import { ProposalBESSDetails } from '../components/ProposalBESSDetails'
import { ProposalDocumentsSection } from '../components/ProposalDocumentsSection'
import { ProposalCommercialPdfsSection } from '../components/ProposalCommercialPdfsSection'

export function Component() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const proposalId = Number(id)
  const { data: proposal, isLoading, isError } = useProposal(proposalId)

  function handleUpdated() {
    queryClient.invalidateQueries({ queryKey: queryKeys.proposals.detail(proposalId) })
  }

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Proposal" actions={<Button variant="secondary" onClick={() => navigate('/proposals')}>Back</Button>} />
        <div className="flex items-center justify-center py-16">
          <Spinner size="lg" />
        </div>
      </div>
    )
  }

  if (isError || !proposal) {
    return (
      <div>
        <PageHeader title="Proposal" actions={<Button variant="secondary" onClick={() => navigate('/proposals')}>Back</Button>} />
        <EmptyState title="Proposal not found" description="The proposal you're looking for doesn't exist" />
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title={proposal.name}
        description={`Proposal #${proposal.id}`}
        actions={
          <Button variant="secondary" onClick={() => navigate('/proposals')}>Back</Button>
        }
      />
      <div className="px-6 pb-6 max-w-4xl space-y-6">
        <ProposalInfoCard proposal={proposal} />
        <ProposalStageSection proposal={proposal} onUpdated={handleUpdated} />
        {proposal.pv_system && <ProposalPVDetails pv={proposal.pv_system} />}
        {proposal.bess_system && <ProposalBESSDetails bess={proposal.bess_system} />}
        <ProposalDocumentsSection proposalId={proposal.id} />
        <ProposalCommercialPdfsSection proposalId={proposal.id} />
      </div>
    </div>
  )
}

Component.displayName = 'ProposalDetailPage'
