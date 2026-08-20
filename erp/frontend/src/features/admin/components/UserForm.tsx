import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Input } from '@atoms/Input/Input'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { adminUserCreateSchema, type AdminUserCreateFormData } from '../schemas/admin.schema'
import { ADMIN_ROLES } from '../types'
import type { AdminUserCreate } from '../types'

interface UserFormProps {
  initialData?: { email: string; full_name: string | null; role: string | null }
  onSubmit: (data: AdminUserCreate) => Promise<void>
  isSubmitting?: boolean
  onCancel?: () => void
}

export function UserForm({ initialData, onSubmit, isSubmitting, onCancel }: UserFormProps) {
  const methods = useForm<AdminUserCreateFormData>({
    resolver: zodResolver(adminUserCreateSchema),
    defaultValues: initialData
      ? { email: initialData.email, full_name: initialData.full_name ?? '', role: (initialData.role ?? 'SALES') as AdminUserCreateFormData['role'], password: '' }
      : { email: '', password: '', full_name: '', role: 'SALES' },
  })

  const isEditing = !!initialData

  return (
    <form onSubmit={methods.handleSubmit(onSubmit)} className="space-y-4">
      <FormField label="Email" required error={methods.formState.errors.email?.message}>
        <Input placeholder="user@example.com" {...methods.register('email')} />
      </FormField>

      <FormField label="Full Name" error={methods.formState.errors.full_name?.message}>
        <Input placeholder="Full name" {...methods.register('full_name')} />
      </FormField>

      {!isEditing && (
        <FormField label="Password" required error={methods.formState.errors.password?.message}>
          <Input type="password" placeholder="Min 6 characters" {...methods.register('password')} />
        </FormField>
      )}

      <FormField label="Role" required error={methods.formState.errors.role?.message}>
        <select
          className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
          {...methods.register('role')}
        >
          {ADMIN_ROLES.map((role) => (
            <option key={role} value={role}>{role}</option>
          ))}
        </select>
      </FormField>

      <div className="flex justify-end gap-3 pt-2">
        {onCancel && (
          <Button type="button" variant="secondary" onClick={onCancel}>
            Cancel
          </Button>
        )}
        <Button type="submit" loading={isSubmitting}>
          {isEditing ? 'Update User' : 'Create User'}
        </Button>
      </div>
    </form>
  )
}
