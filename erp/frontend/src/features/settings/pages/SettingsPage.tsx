import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Input } from '@atoms/Input/Input'
import { Button } from '@atoms/Button/Button'
import { FormField } from '@molecules/FormField/FormField'
import { useAuth } from '@features/auth/hooks/useAuth'
import { useUpdateProfile } from '../mutations/useUpdateProfile'

export function Component() {
  const { user, logout } = useAuth()
  const updateProfile = useUpdateProfile(user!.id)
  const [success, setSuccess] = useState(false)

  const { register, handleSubmit, formState: { errors, isDirty } } = useForm({
    defaultValues: {
      full_name: user?.full_name ?? '',
      email: user?.email ?? '',
    },
  })

  async function onSubmit(data: { full_name: string; email: string }) {
    setSuccess(false)
    await updateProfile.mutateAsync({
      full_name: data.full_name || null,
      email: data.email,
    })
    setSuccess(true)
  }

  return (
    <div>
      <PageHeader title="Admin" description="System settings" />
      <div className="px-6 pb-6 max-w-2xl space-y-6">
        <div className="bg-white rounded-xl border border-border p-6">
          <h3 className="text-h6 text-text mb-1">Profile</h3>
          <p className="text-caption text-text-tertiary mb-4">Update your personal information</p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <FormField label="Full Name" error={errors.full_name?.message}>
              <Input placeholder="Your full name" {...register('full_name')} />
            </FormField>

            <FormField label="Email" error={errors.email?.message}>
              <Input type="email" placeholder="email@example.com" {...register('email')} />
            </FormField>

            {success && (
              <div className="p-3 rounded-lg bg-success-soft text-success text-small">
                Profile updated successfully
              </div>
            )}

            {updateProfile.isError && (
              <div className="p-3 rounded-lg bg-danger-soft text-danger text-small" role="alert">
                {(updateProfile.error as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? 'Failed to update profile'}
              </div>
            )}

            <div className="flex items-center gap-3 pt-2">
              <Button type="submit" loading={updateProfile.isPending} disabled={!isDirty}>
                Save Changes
              </Button>
            </div>
          </form>
        </div>

        <div className="bg-white rounded-xl border border-border p-6">
          <h3 className="text-h6 text-text mb-1">Session</h3>
          <p className="text-caption text-text-tertiary mb-4">Manage your current session</p>
          <Button variant="secondary" onClick={logout}>Sign Out</Button>
        </div>
      </div>
    </div>
  )
}

Component.displayName = 'SettingsPage'
