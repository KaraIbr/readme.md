import { useState } from 'react'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { useMoveLeadStage, useCloseLead } from '../mutations/useLeadMutations'
import { NON_TERMINAL_STAGES, STAGE_LABELS } from '../types'
import type { LeadStage, LeadRead } from '../types'

interface LeadStageSectionProps {
  lead: LeadRead
  onUpdated: () => void
}

export function LeadStageSection({ lead, onUpdated }: LeadStageSectionProps) {
  const [newStage, setNewStage] = useState<LeadStage | ''>('')
  const [closeOutcome, setCloseOutcome] = useState<'WON' | 'LOST' | ''>('')
  const [closeNotes, setCloseNotes] = useState('')

  const moveStage = useMoveLeadStage()
  const closeLead = useCloseLead()

  const isTerminal = lead.current_stage === 'CLOSED_WON' || lead.current_stage === 'CLOSED_LOST'

  async function handleMoveStage() {
    if (!newStage) return
    await moveStage.mutateAsync({ id: lead.id, body: { stage: newStage as LeadStage } })
    setNewStage('')
    onUpdated()
  }

  async function handleClose() {
    if (!closeOutcome) return
    await closeLead.mutateAsync({ id: lead.id, body: { outcome: closeOutcome as 'WON' | 'LOST', notes: closeNotes || null } })
    setCloseOutcome('')
    setCloseNotes('')
    onUpdated()
  }

  if (isTerminal) {
    return null
  }

  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-6">
      <h3 className="text-sm font-semibold text-text">Stage & Close</h3>

      <div className="flex items-end gap-3">
        <FormField label="Move to Stage">
          <select
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
            value={newStage}
            onChange={(e) => setNewStage(e.target.value as LeadStage)}
          >
            <option value="">Select stage...</option>
            {NON_TERMINAL_STAGES.filter(s => s !== lead.current_stage).map((stage) => (
              <option key={stage} value={stage}>{STAGE_LABELS[stage]}</option>
            ))}
          </select>
        </FormField>
        <Button size="sm" onClick={handleMoveStage} loading={moveStage.isPending} disabled={!newStage}>
          Move
        </Button>
      </div>

      <div className="border-t border-border pt-4 space-y-3">
        <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wide">Close Lead</h4>
        <div className="flex items-end gap-3">
          <FormField label="Outcome">
            <select
              className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
              value={closeOutcome}
              onChange={(e) => setCloseOutcome(e.target.value as 'WON' | 'LOST')}
            >
              <option value="">Select outcome...</option>
              <option value="LOST">Lost</option>
            </select>
          </FormField>
          <Button size="sm" variant="danger" onClick={handleClose} loading={closeLead.isPending} disabled={!closeOutcome}>
            Close
          </Button>
        </div>
        <textarea
          className="w-full h-20 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
          placeholder="Close notes (optional)..."
          value={closeNotes}
          onChange={(e) => setCloseNotes(e.target.value)}
        />
      </div>
    </div>
  )
}
