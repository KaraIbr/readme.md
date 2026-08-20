import { useCallback } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Spinner } from '@atoms/Spinner/Spinner'
import { SectionHeading } from '@atoms/SectionHeading/SectionHeading'
import { useProposal } from '../queries/useProposals'
import { queryKeys } from '@lib/query-keys'
import { ProposalInfoCard } from './ProposalInfoCard'
import { ProposalStageSection } from './ProposalStageSection'
import { ProposalPVDetails } from './ProposalPVDetails'
import { ProposalBESSDetails } from './ProposalBESSDetails'
import { ProposalDocumentsSection } from './ProposalDocumentsSection'
import { ProposalCommercialPdfsSection } from './ProposalCommercialPdfsSection'
import { useEffectivePermissions } from '@features/permissions/queries/useUserPermissions'
import { TERMINAL_PROPOSAL_STAGES } from '../types'

interface ProposalDetailDrawerProps {
  proposalId: number | null
  onClose: () => void
}

export function ProposalDetailDrawer({ proposalId, onClose }: ProposalDetailDrawerProps) {
  const { data: proposal, isLoading } = useProposal(proposalId ?? 0)
  const queryClient = useQueryClient()
  const { role } = useEffectivePermissions()
  const isAdmin = role === 'ADMIN'

  const handleUpdated = useCallback(() => {
    if (proposalId) {
      queryClient.invalidateQueries({ queryKey: queryKeys.proposals.detail(proposalId) })
    }
  }, [proposalId, queryClient])

  const isTerminal = proposal
    ? TERMINAL_PROPOSAL_STAGES.includes(proposal.current_stage as typeof TERMINAL_PROPOSAL_STAGES[number])
    : false

  return (
    <Drawer
      open={proposalId !== null}
      onClose={onClose}
      title={proposal?.name ?? 'Proposal'}
      subtitle={proposal ? `Proposal #${proposal.id}` : 'Loading...'}
      width="w-full sm:max-w-3xl"
    >
      {isLoading || !proposal ? (
        <div className="flex items-center justify-center h-64">
          <Spinner />
        </div>
      ) : (
        <div className="space-y-2">
          <SectionHeading>General Information</SectionHeading>
          <ProposalInfoCard proposal={proposal} />

          {isAdmin && !isTerminal && (
            <>
              <SectionHeading>Stage & Outcome</SectionHeading>
              <ProposalStageSection proposal={proposal} onUpdated={handleUpdated} />
            </>
          )}

          {proposal.pv_system && (
            <>
              <SectionHeading>PV System</SectionHeading>
              <ProposalPVDetails pv={proposal.pv_system} />
            </>
          )}

          {proposal.bess_system && (
            <>
              <SectionHeading>BESS System</SectionHeading>
              <ProposalBESSDetails bess={proposal.bess_system} />
            </>
          )}

          <SectionHeading>Documents</SectionHeading>
          <ProposalDocumentsSection proposalId={proposal.id} />

          <SectionHeading>Commercial PDFs</SectionHeading>
          <ProposalCommercialPdfsSection proposalId={proposal.id} />
        </div>
      )}
    </Drawer>
  )
}
