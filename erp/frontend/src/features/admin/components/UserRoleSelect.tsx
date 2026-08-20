import { ADMIN_ROLES } from '../types'

interface UserRoleSelectProps {
  value: string | null
  onChange: (role: string) => void
  disabled?: boolean
  className?: string
}

const roleColors: Record<string, string> = {
  ADMIN: 'text-info',
  MANAGER: 'text-success',
  SALES: 'text-warning',
  TECH: 'text-text-secondary',
}

export function UserRoleSelect({ value, onChange, disabled, className = '' }: UserRoleSelectProps) {
  return (
    <select
      value={value ?? ''}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      className={`
        h-9 px-3 pr-8 rounded-lg border border-border bg-white text-sm font-medium
        focus:outline-none focus:ring-2 focus:ring-primary/30
        disabled:opacity-50 disabled:cursor-not-allowed
        appearance-none cursor-pointer
        bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2012%2012%22%20fill%3D%22none%22%3E%3Cpath%20d%3D%22M3%204.5L6%207.5L9%204.5%22%20stroke%3D%22%236B7280%22%20stroke-width%3D%221.5%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E')]
        bg-[length:12px] bg-[right_8px_center] bg-no-repeat
        ${roleColors[value ?? ''] ?? 'text-text'}
        ${className}
      `.trim()}
    >
      {ADMIN_ROLES.map((role) => (
        <option key={role} value={role}>{role}</option>
      ))}
    </select>
  )
}
