import { useState } from 'react'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { useLeadInteractions } from '../queries/useLeads'
import { useCreateLeadInteraction, useDeleteLeadInteraction } from '../mutations/useLeadMutations'
import { LEAD_INTERACTION_TYPES, INTERACTION_LABELS } from '../types'
import type { LeadInteractionType } from '../types'

interface LeadInteractionsSectionProps {
  leadId: number
}

export function LeadInteractionsSection({ leadId }: LeadInteractionsSectionProps) {
  const { data: interactions, isLoading } = useLeadInteractions(leadId)
  const createMutation = useCreateLeadInteraction()
  const deleteMutation = useDeleteLeadInteraction()

  const [form, setForm] = useState({
    interaction_type: '' as LeadInteractionType | '',
    title: '',
    notes: '',
    interaction_date: new Date().toISOString().split('T')[0],
  })

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.interaction_type || !form.title || !form.notes || !form.interaction_date) return
    await createMutation.mutateAsync({
      leadId,
      body: {
        interaction_type: form.interaction_type as LeadInteractionType,
        title: form.title,
        notes: form.notes,
        interaction_date: new Date(form.interaction_date).toISOString(),
      },
    })
    setForm({ interaction_type: '', title: '', notes: '', interaction_date: new Date().toISOString().split('T')[0] })
  }

  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-4">
      <h3 className="text-sm font-semibold text-text">Interactions</h3>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="grid grid-cols-3 gap-3">
          <FormField label="Type">
            <select
              className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
              value={form.interaction_type}
              onChange={(e) => setForm({ ...form, interaction_type: e.target.value as LeadInteractionType })}
            >
              <option value="">Select type...</option>
              {LEAD_INTERACTION_TYPES.map((t) => (
                <option key={t} value={t}>{INTERACTION_LABELS[t]}</option>
              ))}
            </select>
          </FormField>
          <FormField label="Title">
            <input
              className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
              placeholder="Interaction title"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
            />
          </FormField>
          <FormField label="Date">
            <input
              type="date"
              className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
              value={form.interaction_date}
              onChange={(e) => setForm({ ...form, interaction_date: e.target.value })}
            />
          </FormField>
        </div>
        <div className="flex gap-3">
          <textarea
            className="flex-1 h-20 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
            placeholder="Interaction notes..."
            value={form.notes}
            onChange={(e) => setForm({ ...form, notes: e.target.value })}
          />
          <Button type="submit" size="sm" loading={createMutation.isPending} disabled={!form.interaction_type || !form.title || !form.notes}>
            Add
          </Button>
        </div>
      </form>

      {isLoading && <p className="text-sm text-text-secondary">Loading interactions...</p>}

      {interactions && interactions.length === 0 && !isLoading && (
        <p className="text-sm text-text-tertiary">No interactions recorded yet.</p>
      )}

      {interactions && interactions.length > 0 && (
        <div className="space-y-2">
          {interactions.map((interaction) => (
            <div key={interaction.id} className="flex items-start justify-between p-3 rounded-lg bg-neutral-50 border border-border-light">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-medium text-text-secondary uppercase">
                    {INTERACTION_LABELS[interaction.interaction_type]}
                  </span>
                  <span className="text-sm font-medium text-text">{interaction.title}</span>
                  <span className="text-xs text-text-tertiary">
                    {new Date(interaction.interaction_date).toLocaleDateString()}
                  </span>
                </div>
                <p className="text-sm text-text-secondary whitespace-pre-wrap">{interaction.notes}</p>
              </div>
              <button
                className="text-danger hover:underline text-xs shrink-0"
                onClick={() => {
                  if (window.confirm('Delete this interaction?')) {
                    deleteMutation.mutate({ leadId, interactionId: interaction.id })
                  }
                }}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
