interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  variant?: 'default' | 'success' | 'warning' | 'info'
}

const variantStyles = {
  default: 'bg-white',
  success: 'bg-success-soft',
  warning: 'bg-warning-soft',
  info: 'bg-info-soft',
}

export function MetricCard({ title, value, subtitle, variant = 'default' }: MetricCardProps) {
  return (
    <div className={`rounded-xl border border-border p-5 ${variantStyles[variant]}`}>
      <p className="text-small text-text-secondary">{title}</p>
      <p className="text-h3 text-text mt-1">{value}</p>
      {subtitle && <p className="text-caption text-text-tertiary mt-1">{subtitle}</p>}
    </div>
  )
}
