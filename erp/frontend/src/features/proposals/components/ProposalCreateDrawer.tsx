import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Input } from '@atoms/Input/Input'
import { FormField } from '@molecules/FormField/FormField'
import { useCreateProposal } from '../mutations/useProposalMutations'
import { proposalCreateSchema, type ProposalCreateFormData } from '../schemas/proposal.schema'
import { PROPOSAL_SYSTEM_TYPES, SYSTEM_TYPE_LABELS } from '../types'
import { useLeadList } from '@features/leads/queries/useLeads'
import { PVSystemFields } from './PVSystemFields'

interface ProposalCreateDrawerProps {
  open: boolean
  onClose: () => void
}

function todayString(): string {
  const d = new Date()
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

export function ProposalCreateDrawer({ open, onClose }: ProposalCreateDrawerProps) {
  const navigate = useNavigate()
  const createProposal = useCreateProposal()
  const { data: leadsData } = useLeadList()

  const { register, watch, handleSubmit, reset, formState: { errors } } = useForm<ProposalCreateFormData>({
    resolver: zodResolver(proposalCreateSchema),
    defaultValues: {
      lead_id: undefined,
      name: '',
      version: 'v1.0',
      installation_address: undefined,
      tariff: undefined,
      contracted_demand: undefined,
      system_type: undefined,
      total_price: undefined,
      annual_savings: undefined,
      currency: undefined,
      estimated_cost: undefined,
      expected_profit: undefined,
      submitted_at: todayString(),
      valid_until: undefined,
      pv_system: undefined,
      bess_system: undefined,
    },
  })

  const systemType = watch('system_type')
  const showPv = systemType === 'PV' || systemType === 'HIBRID'
  const showBess = systemType === 'BESS' || systemType === 'HIBRID'

  const onSubmit = useCallback(async (data: ProposalCreateFormData) => {
    if (data.installation_address) {
      const addr = data.installation_address
      if (!addr.address_line && !addr.city && !addr.state && !addr.postal_code) {
        data.installation_address = null
      }
    }
    const result = await createProposal.mutateAsync(data)
    reset()
    onClose()
    navigate(`/proposals/${result.id}`)
  }, [createProposal, reset, onClose, navigate])

  return (
    <Drawer
      open={open}
      onClose={onClose}
      title="New Proposal"
      subtitle="Create a new commercial proposal"
      editable
      actionLabel="Create Proposal"
      cancelLabel="Cancel"
      onAction={handleSubmit(onSubmit)}
      actionLoading={createProposal.isPending}
      actionDisabled={createProposal.isPending}
      width="w-full sm:max-w-3xl"
    >
      <div className="space-y-6">
        <div>
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-3">General Info</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Name" required error={errors.name?.message}>
              <Input placeholder="Proposal name" {...register('name')} />
            </FormField>
            <FormField label="Lead" required error={errors.lead_id?.message}>
              <select
                className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                {...register('lead_id', { valueAsNumber: true })}
              >
                <option value="">Select lead...</option>
                {(leadsData?.items ?? []).map((l) => (
                  <option key={l.id} value={l.id}>{l.title} (#{l.id})</option>
                ))}
              </select>
            </FormField>
            <FormField label="Version" error={errors.version?.message}>
              <Input placeholder="v1.0" {...register('version')} />
            </FormField>
            <FormField label="System Type" error={errors.system_type?.message}>
              <select
                className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                {...register('system_type')}
              >
                <option value="">Select system...</option>
                {PROPOSAL_SYSTEM_TYPES.map((t) => (
                  <option key={t} value={t}>{SYSTEM_TYPE_LABELS[t]}</option>
                ))}
              </select>
            </FormField>
          </div>
        </div>

        <div className="border-t border-border pt-4">
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-3">Pricing</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Total Price" error={errors.total_price?.message}>
              <Input type="number" step="0.01" min={0} placeholder="0.00" {...register('total_price', { valueAsNumber: true })} />
            </FormField>
            <FormField label="Currency" error={errors.currency?.message}>
              <select
                className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
                {...register('currency')}
              >
                <option value="">Select currency...</option>
                <option value="MXN">MXN</option>
                <option value="USD">USD</option>
              </select>
            </FormField>
            <FormField label="Annual Savings" error={errors.annual_savings?.message}>
              <Input type="number" step="0.01" placeholder="0.00" {...register('annual_savings', { valueAsNumber: true })} />
            </FormField>
            <FormField label="Tariff" error={errors.tariff?.message}>
              <Input placeholder="Tariff" {...register('tariff')} />
            </FormField>
            <FormField label="Contracted Demand" error={errors.contracted_demand?.message}>
              <Input type="number" step="0.01" placeholder="0.00" {...register('contracted_demand', { valueAsNumber: true })} />
            </FormField>
            <FormField label="Estimated Cost" error={errors.estimated_cost?.message}>
              <Input type="number" step="0.01" placeholder="0.00" {...register('estimated_cost', { valueAsNumber: true })} />
            </FormField>
            <FormField label="Expected Profit" error={errors.expected_profit?.message}>
              <Input type="number" step="0.01" placeholder="0.00" {...register('expected_profit', { valueAsNumber: true })} />
            </FormField>
          </div>
        </div>

        <div className="border-t border-border pt-4">
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-3">Dates</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Submitted At" error={errors.submitted_at?.message}>
              <Input type="date" {...register('submitted_at')} />
            </FormField>
            <FormField label="Valid Until" error={errors.valid_until?.message}>
              <Input type="date" {...register('valid_until')} />
            </FormField>
          </div>
        </div>

        <div className="border-t border-border pt-4">
          <h4 className="text-xs font-semibold text-text-secondary uppercase tracking-wide mb-3">Installation Address</h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <FormField label="Address Line" error={errors.installation_address?.address_line?.message}>
              <Input placeholder="Street, number, neighborhood" {...register('installation_address.address_line')} />
            </FormField>
            <FormField label="City" error={errors.installation_address?.city?.message}>
              <Input placeholder="City" {...register('installation_address.city')} />
            </FormField>
            <FormField label="State" error={errors.installation_address?.state?.message}>
              <Input placeholder="State" {...register('installation_address.state')} />
            </FormField>
            <FormField label="Postal Code" error={errors.installation_address?.postal_code?.message}>
              <Input placeholder="Postal code" {...register('installation_address.postal_code')} />
            </FormField>
          </div>
        </div>

        {showPv && (
          <div className="border-t border-border pt-4">
            <PVSystemFields register={register} />
          </div>
        )}

        {showBess && (
          <div className="border-t border-border pt-4">
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
                  <input className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.technical_notes')} />
                </FormField>
                <FormField label="Cost/kWh">
                  <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.cost_kwh', { valueAsNumber: true })} />
                </FormField>
                <FormField label="Price/kWh">
                  <input type="number" step="any" className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30" {...register('bess_system.price_kwh', { valueAsNumber: true })} />
                </FormField>
              </div>
            </div>
          </div>
        )}
      </div>
    </Drawer>
  )
}
