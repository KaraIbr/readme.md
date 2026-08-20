import { useState, useMemo, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Spinner } from '@atoms/Spinner/Spinner'
import { useLeadList } from '@features/leads/queries/useLeads'
import { useMoveLeadStage } from '@features/leads/mutations/useLeadMutations'
import type { LeadRead, LeadStage } from '@features/leads/types'

const LEAD_STAGES = ['NEW', 'QUALIFYING', 'PROPOSAL_PHASE', 'CLOSED_WON', 'CLOSED_LOST'] as const

const STAGE_LABELS: Record<string, string> = {
  NEW: 'New',
  QUALIFYING: 'Qualifying',
  PROPOSAL_PHASE: 'Proposal Phase',
  CLOSED_WON: 'Closed Won',
  CLOSED_LOST: 'Closed Lost',
}

const STAGE_ACCENTS: Record<string, string> = {
  NEW: 'border-l-blue-400',
  QUALIFYING: 'border-l-amber-400',
  PROPOSAL_PHASE: 'border-l-purple-400',
  CLOSED_WON: 'border-l-emerald-400',
  CLOSED_LOST: 'border-l-rose-400',
}

const LEAD_TRANSITIONS: Record<string, LeadStage[]> = {
  NEW: ['QUALIFYING', 'CLOSED_WON', 'CLOSED_LOST'],
  QUALIFYING: ['PROPOSAL_PHASE', 'CLOSED_WON', 'CLOSED_LOST'],
  PROPOSAL_PHASE: ['CLOSED_WON', 'CLOSED_LOST'],
  CLOSED_WON: [],
  CLOSED_LOST: [],
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
  item: LeadRead
  onTransition: (entityId: number, toStage: string) => void
}) {
  const navigate = useNavigate()
  const stage = item.current_stage || 'NEW'
  const allowedNext = LEAD_TRANSITIONS[stage] ?? []

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => navigate(`/leads/${item.id}`)}
        className="w-full text-left bg-white rounded-lg border border-border p-3 hover:shadow-sm hover:border-primary/30 transition-all group"
      >
        <div className="flex items-start justify-between gap-2">
          <span className="font-medium truncate text-sm text-text">{item.title}</span>
          <CardMenu allowedNext={allowedNext} onTransition={onTransition} entityId={item.id} />
        </div>
        <div className="flex items-center gap-2 mt-1">
          {item.interest_type && (
            <span className="text-xs text-text-secondary">{item.interest_type}</span>
          )}
          {item.qualification_score != null && (
            <>
              <span className="text-xs text-text-tertiary">•</span>
              <span className="text-xs text-text-secondary">Score {item.qualification_score}</span>
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
  items: LeadRead[]
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
          <p className="text-xs text-text-tertiary text-center py-8">No leads</p>
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

export function LeadBoard() {
  const { data: leadsData, isLoading, error } = useLeadList()
  const moveLeadStage = useMoveLeadStage()
  const [toast, setToast] = useState<{ message: string; id: number } | null>(null)

  const showToast = useCallback((msg: string) => setToast({ message: msg, id: Date.now() }), [])

  useEffect(() => {
    if (!error) return
    const t = setTimeout(() => showToast('Failed to load leads'), 0)
    return () => clearTimeout(t)
  }, [error, showToast])

  const leadsByStage = useMemo(() => {
    const map: Record<string, LeadRead[]> = {}
    if (!leadsData?.items) return map
    for (const l of leadsData.items) {
      const stage = l.current_stage || 'NEW'
      if (!map[stage]) map[stage] = []
      map[stage].push(l)
    }
    return map
  }, [leadsData])

  const total = leadsData?.items?.length ?? 0
  const won = leadsData?.items?.filter((l) => l.current_stage === 'CLOSED_WON').length ?? 0

  async function handleTransition(entityId: number, toStage: string) {
    try {
      await moveLeadStage.mutateAsync({ id: entityId, body: { stage: toStage as LeadStage } })
    } catch {
      showToast('Failed to move lead')
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
        <MetricCard title="Total Leads" value={total} />
        <MetricCard title="Won Leads" value={won} subtitle={total > 0 ? `${((won / total) * 100).toFixed(0)}% conversion` : undefined} />
      </div>

      <div className="flex gap-5 overflow-x-auto pb-4">
        {LEAD_STAGES.map((s) => (
          <KanbanColumn
            key={s}
            title={STAGE_LABELS[s]}
            items={leadsByStage[s] ?? []}
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
