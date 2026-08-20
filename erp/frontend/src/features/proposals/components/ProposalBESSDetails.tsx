import type { ProposalBESSSystemRead } from '../types'

interface ProposalBESSDetailsProps {
  bess: ProposalBESSSystemRead
}

export function ProposalBESSDetails({ bess }: ProposalBESSDetailsProps) {
  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-4">
      <h3 className="text-sm font-semibold text-text">BESS System Details</h3>
      <div className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
        <Field label="Battery Model" value={bess.battery_model} />
        <Field label="Battery Count" value={bess.battery_count} />
        <Field label="Battery Power (kW)" value={bess.battery_power_kw} />
        <Field label="Battery Storage (kWh)" value={bess.battery_storage_kwh} />
        <Field label="Primary Use" value={bess.bess_primary_use} />
        <Field label="Technical Notes" value={bess.technical_notes} />
        <Field label="Cost/kWh" value={bess.cost_kwh} />
        <Field label="Price/kWh" value={bess.price_kwh} />
      </div>
    </div>
  )
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div>
      <p className="text-xs font-medium text-text-secondary">{label}</p>
      <p className="text-sm text-text mt-0.5">{value ?? '—'}</p>
    </div>
  )
}
