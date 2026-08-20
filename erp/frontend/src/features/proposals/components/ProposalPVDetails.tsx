import type { ProposalPVSystemRead } from '../types'

interface ProposalPVDetailsProps {
  pv: ProposalPVSystemRead
}

export function ProposalPVDetails({ pv }: ProposalPVDetailsProps) {
  return (
    <div className="bg-white rounded-xl border border-border p-6 space-y-4">
      <h3 className="text-sm font-semibold text-text">PV System Details</h3>
      <div className="grid grid-cols-2 gap-x-8 gap-y-3 text-sm">
        <Field label="Panel Count" value={pv.panel_count} />
        <Field label="Panel Model" value={pv.panel_model} />
        <Field label="Panel Power" value={pv.panel_power} />
        <Field label="Inverter Model" value={pv.inverter_model} />
        <Field label="Inverter Count" value={pv.inverter_count} />
        <Field label="Inverter Power" value={pv.inverter_power} />
        <Field label="Surface Type" value={pv.type_of_surface} />
        <Field label="Total Power (AC)" value={pv.total_power_ac} />
        <Field label="System Size (kW)" value={pv.system_size_kw} />
        <Field label="Oversizing (kW)" value={pv.oversizing_kw} />
        <Field label="Est. Annual kWh" value={pv.estimated_annual_kwh} />
        <Field label="Est. Savings (kW)" value={pv.estimated_savings_kw} />
        <Field label="Connection Mode" value={pv.connection_mode} />
        <Field label="Cost/Watt" value={pv.cost_watt} />
        <Field label="Price/Watt" value={pv.price_watt} />
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
