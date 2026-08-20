import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { Input } from '@atoms/Input/Input'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { adminUserCreateSchema, type AdminUserCreateFormData } from '../schemas/admin.schema'
import type { AdminUserCreate } from '../types'

interface UserCreateFormProps {
  onSubmit: (data: AdminUserCreate) => Promise<void>
  isSubmitting?: boolean
  onCancel: () => void
}

export function UserCreateForm({ onSubmit, isSubmitting, onCancel }: UserCreateFormProps) {
  const methods = useForm<AdminUserCreateFormData>({
    resolver: zodResolver(adminUserCreateSchema),
    defaultValues: { email: '', password: '', full_name: '', role: 'SALES' },
  })

  return (
    <form onSubmit={methods.handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField label="Email" required error={methods.formState.errors.email?.message}>
          <Input placeholder="user@example.com" {...methods.register('email')} />
        </FormField>

        <FormField label="Full Name" error={methods.formState.errors.full_name?.message}>
          <Input placeholder="Full name" {...methods.register('full_name')} />
        </FormField>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <FormField label="Password" required error={methods.formState.errors.password?.message}>
          <Input type="password" placeholder="Min 8 characters" {...methods.register('password')} />
        </FormField>

        <FormField label="Role" required error={methods.formState.errors.role?.message}>
          <select
            className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
            {...methods.register('role')}
          >
            <option value="ADMIN">Admin</option>
            <option value="MANAGER">Manager</option>
            <option value="SALES">Sales</option>
            <option value="TECH">Tech</option>
          </select>
        </FormField>
      </div>

      <div className="flex justify-end gap-3 pt-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" loading={isSubmitting}>
          Create User
        </Button>
      </div>
    </form>
  )
}
