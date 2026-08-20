import { useState, useCallback, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Spinner } from '@atoms/Spinner/Spinner'
import { queryKeys } from '@lib/query-keys'
import { useUsers } from '../queries/useAdminUsers'
import { useCreateUser } from '../mutations/useCreateUser'
import { useDeleteUser } from '../mutations/useDeleteUser'
import { updateUser } from '../services/admin.service'
import { UserListTable } from '../components/UserListTable'
import { UserDrawer } from '../components/UserDrawer'
import { UserCreateForm } from '../components/UserCreateForm'
import { assignUserRole } from '@features/permissions/services/permissions.service'
import { useEffectivePermissions } from '@features/permissions/queries/useUserPermissions'
import { useAuth } from '@features/auth/hooks/useAuth'
import { Permissions } from '@shared/permissions'
import type { AdminUser, AdminUserCreate } from '../types'

function Toast({ message, type, onClose }: { message: string; type: 'error' | 'success'; onClose: () => void }) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500)
    return () => clearTimeout(t)
  }, [onClose])
  return (
    <div
      className={`fixed bottom-4 right-4 z-50 border px-4 py-2.5 rounded-lg shadow-md text-sm font-medium ${
        type === 'error'
          ? 'bg-red-50 border-red-200 text-red-700'
          : 'bg-green-50 border-green-200 text-green-700'
      }`}
    >
      {message}
    </div>
  )
}

function ConfirmDialog({
  title,
  message,
  confirmLabel,
  onConfirm,
  onCancel,
  loading,
}: {
  title: string
  message: string
  confirmLabel?: string
  onConfirm: () => void
  onCancel: () => void
  loading?: boolean
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/20" onClick={onCancel}>
      <div className="bg-white rounded-xl border border-border shadow-lg p-6 max-w-sm mx-4" onClick={(e) => e.stopPropagation()}>
        <h3 className="text-h6 text-text mb-2">{title}</h3>
        <p className="text-sm text-text-secondary mb-5">{message}</p>
        <div className="flex justify-end gap-2">
          <Button variant="ghost" size="sm" onClick={onCancel}>Cancel</Button>
          <Button variant="danger" size="sm" onClick={onConfirm} loading={loading}>
            {confirmLabel || 'Confirm'}
          </Button>
        </div>
      </div>
    </div>
  )
}

export function Component() {
  const { data: users, isLoading, error } = useUsers()
  const createUser = useCreateUser()
  const { can } = useEffectivePermissions()
  const { user: currentUser } = useAuth()

  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' } | null>(null)

  const queryClient = useQueryClient()
  const [pendingDeactivate, setPendingDeactivate] = useState<AdminUser | null>(null)
  const [pendingDelete, setPendingDelete] = useState<AdminUser | null>(null)
  const deactivateMutation = useMutation({
    mutationFn: ({ id, ...body }: { id: number; is_active: boolean }) => updateUser(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.admin.users.all })
    },
  })
  const deleteMutation = useDeleteUser()

  const handleCreate = useCallback(async (data: AdminUserCreate) => {
    try {
      const newUser = await createUser.mutateAsync(data)
      if (data.role) {
        try {
          await assignUserRole(newUser.id, data.role.toLowerCase())
        } catch {
          // Role assignment failed but user was created
        }
      }
      setShowCreateForm(false)
      setToast({ message: 'User created successfully', type: 'success' })
    } catch {
      setToast({ message: 'Failed to create user', type: 'error' })
    }
  }, [createUser])

  const handleSelectUser = useCallback((user: AdminUser) => {
    setSelectedUser(user)
  }, [])

  const handleDeactivate = useCallback((user: AdminUser) => {
    if (!can(Permissions.admin.users.edit)) {
      setToast({ message: 'You do not have permission to change user status', type: 'error' })
      return
    }
    setPendingDeactivate(user)
  }, [can])

  const handleConfirmDeactivate = useCallback(async () => {
    if (!pendingDeactivate) return
    try {
      await deactivateMutation.mutateAsync({
        id: pendingDeactivate.id,
        is_active: !pendingDeactivate.is_active,
      })
      setToast({
        message: pendingDeactivate.is_active ? 'User deactivated' : 'User activated',
        type: 'success',
      })
      if (selectedUser?.id === pendingDeactivate.id) {
        setSelectedUser({ ...pendingDeactivate, is_active: !pendingDeactivate.is_active })
      }
    } catch {
      setToast({ message: 'Failed to update user status', type: 'error' })
    }
    setPendingDeactivate(null)
  }, [pendingDeactivate, deactivateMutation, selectedUser])

  const handleDelete = useCallback((user: AdminUser) => {
    if (!can(Permissions.admin.users.delete)) {
      setToast({ message: 'You do not have permission to delete users', type: 'error' })
      return
    }
    if (user.id === currentUser?.id) {
      setToast({ message: 'You cannot delete your own account', type: 'error' })
      return
    }
    setPendingDelete(user)
  }, [can, currentUser])

  const handleConfirmDelete = useCallback(async () => {
    if (!pendingDelete) return
    try {
      await deleteMutation.mutateAsync(pendingDelete.id)
      setToast({ message: 'User deleted successfully', type: 'success' })
      if (selectedUser?.id === pendingDelete.id) {
        setSelectedUser(null)
      }
    } catch {
      setToast({ message: 'Failed to delete user', type: 'error' })
    }
    setPendingDelete(null)
  }, [pendingDelete, deleteMutation, selectedUser])

  if (isLoading) {
    return (
      <div>
        <PageHeader title="Users" description="Manage system users" />
        <div className="flex items-center justify-center py-16">
          <Spinner size="lg" />
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div>
        <PageHeader title="Users" description="Manage system users" />
        <div className="px-6 pb-6">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6 text-center">
            <p className="text-sm font-medium text-red-700">Failed to load users</p>
            <p className="text-xs text-red-500 mt-1">{(error as Error)?.message || 'An unexpected error occurred'}</p>
            <Button variant="ghost" size="sm" className="mt-3" onClick={() => window.location.reload()}>
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        title="Users"
        description="Manage system users"
        actions={
          <Button onClick={() => setShowCreateForm(true)} size="sm">
            New User
          </Button>
        }
      />

      <div className="px-6 pb-6">
        {showCreateForm && (
          <div className="bg-white rounded-xl border border-border p-6 mb-6">
            <h3 className="text-h6 text-text mb-4">Create New User</h3>
            <UserCreateForm
              onSubmit={handleCreate}
              isSubmitting={createUser.isPending}
              onCancel={() => setShowCreateForm(false)}
            />
          </div>
        )}

        <UserListTable
          users={users ?? []}
          onSelectUser={handleSelectUser}
          onDeactivate={handleDeactivate}
          onDelete={handleDelete}
        />
      </div>

      <UserDrawer
        key={selectedUser?.id ?? 'none'}
        user={selectedUser}
        open={selectedUser !== null}
        onClose={() => setSelectedUser(null)}
      />

      {pendingDeactivate && (
        <ConfirmDialog
          title={pendingDeactivate.is_active ? 'Deactivate user' : 'Activate user'}
          message={`Are you sure you want to ${pendingDeactivate.is_active ? 'deactivate' : 'activate'} "${pendingDeactivate.full_name || pendingDeactivate.email}"?`}
          confirmLabel={pendingDeactivate.is_active ? 'Deactivate' : 'Activate'}
          onConfirm={handleConfirmDeactivate}
          onCancel={() => setPendingDeactivate(null)}
          loading={deactivateMutation.isPending}
        />
      )}

      {pendingDelete && (
        <ConfirmDialog
          title="Delete user"
          message={`Are you sure you want to delete "${pendingDelete.full_name || pendingDelete.email}"? This action cannot be undone.`}
          confirmLabel="Delete"
          onConfirm={handleConfirmDelete}
          onCancel={() => setPendingDelete(null)}
          loading={deleteMutation.isPending}
        />
      )}

      {toast && (
        <Toast message={toast.message} type={toast.type} onClose={() => setToast(null)} />
      )}
    </div>
  )
}

Component.displayName = 'AdminUsersPage'
