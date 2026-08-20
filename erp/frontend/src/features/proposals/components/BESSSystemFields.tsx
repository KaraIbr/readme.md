import { FormField } from '@molecules/FormField/FormField'
import type { UseFormRegister } from 'react-hook-form'
import type { ProposalCreateFormData } from '../schemas/proposal.schema'

interface BESSSystemFieldsProps {
  register: UseFormRegister<ProposalCreateFormData>
}

export function BESSSystemFields({ register }: BESSSystemFieldsProps) {
  return (
    <div className="border border-border rounded-lg p-4 space-y-3">
      <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wide">BESS System</h4>
      <div className="grid grid-cols-2 gap-3">
        <FormField label="Battery Model">
          <input className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.battery_model')} />
        </FormField>
        <FormField label="Battery Count">
          <input type="number" min={0} className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.battery_count', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Battery Power (kW)">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.battery_power_kw', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Battery Storage (kWh)">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.battery_storage_kwh', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Primary Use">
          <input className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.bess_primary_use')} />
        </FormField>
        <FormField label="Technical Notes">
          <textarea className="w-full h-20 px-3 py-2 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none" {...register('bess_system.technical_notes')} />
        </FormField>
        <FormField label="Cost/kWh">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.cost_kwh', { valueAsNumber: true })} />
        </FormField>
        <FormField label="Price/kWh">
          <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.price_kwh', { valueAsNumber: true })} />
        </FormField>
      </div>
    </div>
  )
}
