import { useState } from 'react'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { useMoveProposalStage, useMarkProposalWon, useMarkProposalLost } from '../mutations/useProposalMutations'
import { NON_TERMINAL_PROPOSAL_STAGES, STAGE_LABELS, TERMINAL_PROPOSAL_STAGES } from '../types'
import type { ProposalStage, ProposalRead } from '../types'

interface ProposalStageSectionProps {
  proposal: ProposalRead
  onUpdated: () => void
}

export function ProposalStageSection({ proposal, onUpdated }: ProposalStageSectionProps) {
  const [newStage, setNewStage] = useState<ProposalStage | ''>('')
  const [lossReason, setLossReason] = useState('')

  const moveStage = useMoveProposalStage()
  const markWon = useMarkProposalWon()
  const markLost = useMarkProposalLost()

  const isTerminal = TERMINAL_PROPOSAL_STAGES.includes(proposal.current_stage as typeof TERMINAL_PROPOSAL_STAGES[number])

  async function handleMoveStage() {
    if (!newStage) return
    await moveStage.mutateAsync({ id: proposal.id, body: { stage: newStage as ProposalStage } })
    setNewStage('')
    onUpdated()
  }

  async function handleMarkWon() {
    if (!window.confirm('Mark this proposal as Won? This will close the lead and supersede other proposals.')) return
    await markWon.mutateAsync(proposal.id)
    onUpdated()
  }

  async function handleMarkLost() {
    if (!lossReason) return
    await markLost.mutateAsync({ id: proposal.id, body: { loss_reason: lossReason } })
    setLossReason('')
    onUpdated()
  }

  if (isTerminal) return null

  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-6">
      <h3 className="text-sm font-semibold text-text">Stage & Outcome</h3>

      <div className="flex items-end gap-3">
        <FormField label="Move to Stage">
          <select
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
            value={newStage}
            onChange={(e) => setNewStage(e.target.value as ProposalStage)}
          >
            <option value="">Select stage...</option>
            {NON_TERMINAL_PROPOSAL_STAGES.filter(s => s !== proposal.current_stage).map((stage) => (
              <option key={stage} value={stage}>{STAGE_LABELS[stage]}</option>
            ))}
          </select>
        </FormField>
        <Button size="sm" onClick={handleMoveStage} loading={moveStage.isPending} disabled={!newStage}>
          Move
        </Button>
      </div>

      <div className="border-t border-border pt-4 space-y-3">
        <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wide">Terminal Actions</h4>
        <div className="flex gap-3">
          <Button size="sm" variant="primary" onClick={handleMarkWon} loading={markWon.isPending}>
            Mark as Won
          </Button>
          <div className="flex items-end gap-3">
            <FormField label="Loss Reason">
              <input
                className="w-64 h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                placeholder="Reason for loss"
                value={lossReason}
                onChange={(e) => setLossReason(e.target.value)}
              />
            </FormField>
            <Button size="sm" variant="danger" onClick={handleMarkLost} loading={markLost.isPending} disabled={!lossReason}>
              Mark Lost
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
