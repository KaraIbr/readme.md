import { useState, useMemo, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Spinner } from '@atoms/Spinner/Spinner'
import { useProposalList } from '@features/proposals/queries/useProposals'
import { useMoveProposalStage } from '@features/proposals/mutations/useProposalMutations'
import type { ProposalRead, ProposalStage } from '@features/proposals/types'

const PROPOSAL_STAGES = ['DRAFT', 'SENT', 'NEGOTIATION', 'WON', 'LOST', 'SUPERSEDED'] as const

const STAGE_LABELS: Record<string, string> = {
  DRAFT: 'Draft',
  SENT: 'Sent',
  NEGOTIATION: 'Negotiation',
  WON: 'Won',
  LOST: 'Lost',
  SUPERSEDED: 'Superseded',
}

const STAGE_ACCENTS: Record<string, string> = {
  DRAFT: 'border-l-slate-400',
  SENT: 'border-l-sky-400',
  NEGOTIATION: 'border-l-orange-400',
  WON: 'border-l-emerald-400',
  LOST: 'border-l-rose-400',
  SUPERSEDED: 'border-l-neutral-400',
}

const PROPOSAL_TRANSITIONS: Record<string, ProposalStage[]> = {
  DRAFT: ['SENT', 'SUPERSEDED'],
  SENT: ['NEGOTIATION', 'WON', 'LOST', 'SUPERSEDED'],
  NEGOTIATION: ['WON', 'LOST', 'SUPERSEDED'],
  WON: [],
  LOST: [],
  SUPERSEDED: [],
}

function Toast({ message, onClose }: { message: string; onClose: () => void }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3000)
    return () => clearTimeout(t)
  }, [onClose])
  return (
    <div className="fixed bottom-4 right-4 z-50 border border-border bg-white text-xs text-text-secondary px-3 py-2 rounded-lg shadow-sm">
      {message}
    </div>
  )
}

function MetricCard({ title, value, subtitle }: { title: string; value: string | number; subtitle?: string }) {
  return (
    <div className="rounded-xl border border-border bg-white p-5">
      <p className="text-small text-text-secondary">{title}</p>
      <p className="text-h3 text-text mt-1">{value}</p>
      {subtitle && <p className="text-caption text-text-tertiary mt-1">{subtitle}</p>}
    </div>
  )
}

function CardMenu({ allowedNext, onTransition, entityId }: {
  allowedNext: string[]
  onTransition: (entityId: number, toStage: string) => void
  entityId: number
}) {
  const [open, setOpen] = useState(false)
  if (allowedNext.length === 0) return null
  return (
    <div className="relative">
      <button
        type="button"
        onClick={(e) => { e.stopPropagation(); setOpen(!open) }}
        className="text-text-tertiary hover:text-text transition-colors p-0.5 rounded hover:bg-neutral-100"
      >
        <svg className="size-4" fill="currentColor" viewBox="0 0 20 20">
          <circle cx="10" cy="4" r="1.5" />
          <circle cx="10" cy="10" r="1.5" />
          <circle cx="10" cy="16" r="1.5" />
        </svg>
      </button>
      {open && (
        <>
          <div className="fixed inset-0 z-10" onClick={() => setOpen(false)} />
          <div className="absolute z-20 right-0 top-full mt-1 w-44 bg-white border border-border rounded-lg shadow-lg overflow-hidden">
            {allowedNext.map((to) => (
              <button
                key={to}
                type="button"
                onClick={(e) => {
                  e.stopPropagation()
                  onTransition(entityId, to)
                  setOpen(false)
                }}
                className="w-full text-left px-3 py-2 text-sm hover:bg-neutral-50 text-text transition-colors"
              >
                {STAGE_LABELS[to]}
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function KanbanCard({ item, onTransition }: {
  item: ProposalRead
  onTransition: (entityId: number, toStage: string) => void
}) {
  const navigate = useNavigate()
  const stage = item.current_stage || 'DRAFT'
  const allowedNext = PROPOSAL_TRANSITIONS[stage] ?? []

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => navigate(`/proposals/${item.id}`)}
        className="w-full text-left bg-white rounded-lg border border-border p-3 hover:shadow-sm hover:border-primary/30 transition-all group"
      >
        <div className="flex items-start justify-between gap-2">
          <span className="font-medium truncate text-sm text-text">{item.name}</span>
          <CardMenu allowedNext={allowedNext} onTransition={onTransition} entityId={item.id} />
        </div>
        <div className="flex items-center gap-2 mt-1">
          {item.system_type && (
            <span className="text-xs text-text-secondary">{item.system_type}</span>
          )}
          {item.total_price != null && (
            <>
              <span className="text-xs text-text-tertiary">•</span>
              <span className="text-xs text-text-secondary">${item.total_price}</span>
            </>
          )}
        </div>
        <span className="text-xs text-text-tertiary mt-1.5 block">#{item.id}</span>
      </button>
    </div>
  )
}

function KanbanColumn({ title, items, stage, onTransition }: {
  title: string
  items: ProposalRead[]
  stage: string
  onTransition: (entityId: number, toStage: string) => void
}) {
  return (
    <div className="flex-shrink-0 w-72 flex flex-col">
      <div className={`sticky top-0 bg-background z-10 border-b border-border pb-3 mb-3 border-l-2 pl-3 ${STAGE_ACCENTS[stage]}`}>
        <div className="flex items-center justify-between">
          <span className="text-sm font-semibold text-text">{title}</span>
          <span className="text-xs font-medium text-text-tertiary bg-neutral-100 px-2 py-0.5 rounded-full">{items.length}</span>
        </div>
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto max-h-[600px] min-h-[200px] pr-1">
        {items.length === 0 ? (
          <p className="text-xs text-text-tertiary text-center py-8">No proposals</p>
        ) : items.map((item) => (
          <KanbanCard
            key={item.id}
            item={item}
            onTransition={onTransition}
          />
        ))}
      </div>
    </div>
  )
}

export function ProposalBoard() {
  const { data: proposalsData, isLoading, error } = useProposalList()
  const moveProposalStage = useMoveProposalStage()
  const [toast, setToast] = useState<{ message: string; id: number } | null>(null)

  const showToast = useCallback((msg: string) => setToast({ message: msg, id: Date.now() }), [])

  useEffect(() => {
    if (!error) return
    const t = setTimeout(() => showToast('Failed to load proposals'), 0)
    return () => clearTimeout(t)
  }, [error, showToast])

  const proposalsByStage = useMemo(() => {
    const map: Record<string, ProposalRead[]> = {}
    if (!proposalsData?.items) return map
    for (const p of proposalsData.items) {
      const stage = p.current_stage || 'DRAFT'
      if (!map[stage]) map[stage] = []
      map[stage].push(p)
    }
    return map
  }, [proposalsData])

  const total = proposalsData?.items?.length ?? 0
  const won = proposalsData?.items?.filter((p) => p.current_stage === 'WON').length ?? 0

  async function handleTransition(entityId: number, toStage: string) {
    try {
      await moveProposalStage.mutateAsync({ id: entityId, body: { stage: toStage as ProposalStage } })
    } catch {
      showToast('Failed to move proposal')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <MetricCard title="Total Proposals" value={total} />
        <MetricCard title="Won Proposals" value={won} subtitle={total > 0 ? `${((won / total) * 100).toFixed(0)}% conversion` : undefined} />
      </div>

      <div className="flex gap-5 overflow-x-auto pb-4">
        {PROPOSAL_STAGES.map((s) => (
          <KanbanColumn
            key={s}
            title={STAGE_LABELS[s]}
            items={proposalsByStage[s] ?? []}
            stage={s}
            onTransition={handleTransition}
          />
        ))}
      </div>

      {toast && (
        <Toast key={toast.id} message={toast.message} onClose={() => setToast(null)} />
      )}
    </div>
  )
}
