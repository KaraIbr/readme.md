import { FormField } from '@molecules/FormField/FormField'
import type { UseFormRegister } from 'react-hook-form'
import type { ProposalCreateFormData } from '../schemas/proposal.schema'

interface PVSystemFieldsProps {
  register: UseFormRegister<ProposalCreateFormData>
}

export function PVSystemFields({ register }: PVSystemFieldsProps) {
  return (
    <div className="border border-border rounded-lg p-4 space-y-3">
      <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wide">PV System</h4>
      <div className="grid grid-cols-2 gap-3">
        <FormField label="Panel Count">
          <input type="number" min={0} className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.panel_count', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Panel Model">
          <input className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.panel_model')} />
        </FormField>
        <FormField label="Panel Power">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.panel_power', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Inverter Model">
          <input className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.inverter_model')} />
        </FormField>
        <FormField label="Inverter Count">
          <input type="number" min={0} className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.inverter_count', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Inverter Power">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.inverter_power', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Surface Type">
          <input className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.type_of_surface')} />
        </FormField>
        <FormField label="Total Power (AC)">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.total_power_ac', { valueAsNumber: true })} />
        </FormField>
        <FormField label="System Size (kW)">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.system_size_kw', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Oversizing (kW)">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.oversizing_kw', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Est. Annual kWh">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.estimated_annual_kwh', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Est. Savings (kW)">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.estimated_savings_kw', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Connection Mode">
          <input className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.connection_mode')} />
        </FormField>
        <FormField label="Cost/Watt">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.cost_watt', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Price/Watt">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('pv_system.price_watt', { valueAsNumber: true })} />
        </FormField>
      </div>
    </div>
  )
}
