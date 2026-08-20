const FIELD_LABELS: Record<string, string> = {
  version: 'Version',
  tariff: 'Tariff',
  contracted_demand: 'Contracted Demand',
  system_type: 'System Type',
  total_price: 'Total Price',
  annual_savings: 'Annual Savings',
  currency: 'Currency',
  estimated_cost: 'Estimated Cost',
  expected_profit: 'Expected Profit',
  submitted_at: 'Submitted At',
  valid_until: 'Valid Until',
  'installation_address.address_line': 'Address Line',
  'installation_address.city': 'City',
  'installation_address.state': 'State',
  'installation_address.postal_code': 'Postal Code',
  'pv_system.panel_count': 'Panel Count',
  'pv_system.panel_model': 'Panel Model',
  'pv_system.panel_power': 'Panel Power',
  'pv_system.inverter_model': 'Inverter Model',
  'pv_system.inverter_count': 'Inverter Count',
  'pv_system.inverter_power': 'Inverter Power',
  'pv_system.type_of_surface': 'Type of Surface',
  'pv_system.total_power_ac': 'Total Power (AC)',
  'pv_system.system_size_kw': 'System Size (kW)',
  'pv_system.oversizing_kw': 'Oversizing (kW)',
  'pv_system.estimated_annual_kwh': 'Est. Annual kWh',
  'pv_system.estimated_savings_kw': 'Est. Savings (kW)',
  'pv_system.connection_mode': 'Connection Mode',
  'pv_system.cost_watt': 'Cost/Watt',
  'pv_system.price_watt': 'Price/Watt',
  'bess_system.battery_model': 'Battery Model',
  'bess_system.battery_count': 'Battery Count',
  'bess_system.battery_power_kw': 'Battery Power (kW)',
  'bess_system.battery_storage_kwh': 'Battery Storage (kWh)',
  'bess_system.bess_primary_use': 'Primary Use',
  'bess_system.technical_notes': 'Technical Notes',
  'bess_system.cost_kwh': 'Cost/kWh',
  'bess_system.price_kwh': 'Price/kWh',
}

type FieldGroup = {
  label: string
  icon: string
  fields: string[]
  color: string
}

const FIELD_GROUPS: FieldGroup[] = [
  {
    label: 'General Information',
    icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
    fields: ['version', 'tariff', 'contracted_demand', 'system_type', 'total_price', 'annual_savings', 'currency', 'estimated_cost', 'expected_profit', 'submitted_at', 'valid_until'],
    color: 'border-l-amber-400',
  },
  {
    label: 'Installation Address',
    icon: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z',
    fields: ['installation_address.address_line', 'installation_address.city', 'installation_address.state', 'installation_address.postal_code'],
    color: 'border-l-blue-400',
  },
  {
    label: 'PV System',
    icon: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z',
    fields: [
      'pv_system.panel_count', 'pv_system.panel_model', 'pv_system.panel_power',
      'pv_system.inverter_model', 'pv_system.inverter_count', 'pv_system.inverter_power',
      'pv_system.type_of_surface', 'pv_system.total_power_ac', 'pv_system.system_size_kw',
      'pv_system.oversizing_kw', 'pv_system.estimated_annual_kwh', 'pv_system.estimated_savings_kw',
      'pv_system.connection_mode', 'pv_system.cost_watt', 'pv_system.price_watt',
    ],
    color: 'border-l-emerald-400',
  },
  {
    label: 'BESS System',
    icon: 'M13 10V3L4 14h7v7l9-11h-7z',
    fields: [
      'bess_system.battery_model', 'bess_system.battery_count', 'bess_system.battery_power_kw',
      'bess_system.battery_storage_kwh', 'bess_system.bess_primary_use', 'bess_system.technical_notes',
      'bess_system.cost_kwh', 'bess_system.price_kwh',
    ],
    color: 'border-l-purple-400',
  },
]

function getLabel(field: string): string {
  return FIELD_LABELS[field] ?? field
}

function groupMissingFields(missingFields: string[]): FieldGroup[] {
  return FIELD_GROUPS.map((group) => ({
    ...group,
    fields: group.fields.filter((f) => missingFields.includes(f)),
  })).filter((g) => g.fields.length > 0)
}

interface MissingFieldsCardProps {
  missingFields: string[]
}

export function MissingFieldsCard({ missingFields }: MissingFieldsCardProps) {
  if (missingFields.length === 0) return null

  const groups = groupMissingFields(missingFields)
  const uncovered = missingFields.filter(
    (f) => !FIELD_GROUPS.some((g) => g.fields.includes(f))
  )

  return (
    <div className="border border-danger/30 bg-danger-soft/30 rounded-xl p-5 space-y-4">
      <div className="flex items-center gap-2">
        <svg className="size-4 text-danger shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4.5c-.77-.833-2.694-.833-3.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <p className="text-xs font-semibold text-danger uppercase tracking-wide">
          Missing Required Fields ({missingFields.length})
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {groups.map((group) => (
          <div
            key={group.label}
            className={`bg-white rounded-lg border border-border border-l-2 ${group.color} p-3`}
          >
            <div className="flex items-center gap-1.5 mb-2">
              <svg className="size-3.5 text-text-secondary shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d={group.icon} />
              </svg>
              <p className="text-xs font-semibold text-text-secondary">{group.label}</p>
            </div>
            <ul className="space-y-1">
              {group.fields.map((f) => (
                <li key={f} className="flex items-center gap-1.5 text-xs text-danger">
                  <svg className="size-3 shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <circle cx="10" cy="10" r="3" />
                  </svg>
                  {getLabel(f)}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {uncovered.length > 0 && (
        <div className="bg-white rounded-lg border border-border p-3">
          <p className="text-xs font-semibold text-text-secondary mb-1">Other</p>
          <ul className="space-y-0.5">
            {uncovered.map((f) => (
              <li key={f} className="text-xs text-danger">{f}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
