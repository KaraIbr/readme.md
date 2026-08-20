import { useState, useCallback } from 'react'
import { Drawer } from '@organisms/Drawer/Drawer'
import { Avatar } from '@atoms/Avatar/Avatar'
import { Badge } from '@atoms/Badge/Badge'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'
import { FormField } from '@molecules/FormField/FormField'
import { UserRoleSelect } from './UserRoleSelect'
import { useUpdateUser } from '../mutations/useUpdateUser'
import { useDeleteUser } from '../mutations/useDeleteUser'
import { grantCrmAccess } from '@features/permissions/services/permissions.service'
import { useEffectivePermissions } from '@features/permissions/queries/useUserPermissions'
import { useAuth } from '@features/auth/hooks/useAuth'
import { Permissions } from '@shared/permissions'
import type { AdminUser } from '../types'

interface UserDrawerProps {
  user: AdminUser | null
  open: boolean
  onClose: () => void
}

const roleVariants: Record<string, 'info' | 'success' | 'warning' | 'default'> = {
  ADMIN: 'info',
  MANAGER: 'success',
  SALES: 'warning',
  TECH: 'default',
}

function Toast({ message, type }: { message: string; type: 'error' | 'success' }) {
  return (
    <div
      className={`fixed bottom-4 right-4 z-[60] border px-4 py-2.5 rounded-lg shadow-md text-sm font-medium ${
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
    <div className="fixed inset-0 z-[70] flex items-center justify-center bg-black/20" onClick={onCancel}>
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

export function UserDrawer({ user, open, onClose }: UserDrawerProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editEmail, setEditEmail] = useState('')
  const [editName, setEditName] = useState('')
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' } | null>(null)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [confirmToggle, setConfirmToggle] = useState(false)

  const { user: currentUser } = useAuth()
  const { can } = useEffectivePermissions()
  const updateUser = useUpdateUser(user?.id ?? 0)
  const deleteUser = useDeleteUser()

  const handleEditClick = useCallback(() => {
    if (!user) return
    setEditEmail(user.email)
    setEditName(user.full_name ?? '')
    setIsEditing(true)
  }, [user])

  const handleCancelEdit = useCallback(() => {
    setIsEditing(false)
  }, [])

  const handleSaveProfile = useCallback(async () => {
    if (!user) return
    if (!can(Permissions.admin.users.edit)) {
      setToast({ message: 'You do not have permission to edit users', type: 'error' })
      return
    }
    try {
      await updateUser.mutateAsync({ email: editEmail, full_name: editName })
      setToast({ message: 'User updated successfully', type: 'success' })
      setIsEditing(false)
    } catch {
      setToast({ message: 'Failed to update user', type: 'error' })
    }
  }, [user, editEmail, editName, updateUser, can])

  const handleRoleChange = useCallback(async (role: string) => {
    if (!can(Permissions.admin.users.role)) {
      setToast({ message: 'You do not have permission to change roles', type: 'error' })
      return
    }
    if (!user) return
    try {
      await grantCrmAccess(user.id, role.toLowerCase())
      setToast({ message: 'Role updated successfully', type: 'success' })
    } catch {
      setToast({ message: 'Failed to assign role', type: 'error' })
    }
  }, [user, can])

  const handleToggleActive = useCallback(async () => {
    if (!can(Permissions.admin.users.edit) || !user) {
      setToast({ message: 'You do not have permission to change user status', type: 'error' })
      setConfirmToggle(false)
      return
    }
    try {
      await updateUser.mutateAsync({ is_active: !user.is_active })
      setToast({
        message: user.is_active ? 'User deactivated' : 'User activated',
        type: 'success',
      })
    } catch {
      setToast({ message: 'Failed to update user status', type: 'error' })
    }
    setConfirmToggle(false)
  }, [user, updateUser, can])

  const handleDelete = useCallback(async () => {
    if (!can(Permissions.admin.users.delete) || !user) {
      setToast({ message: 'You do not have permission to delete users', type: 'error' })
      setConfirmDelete(false)
      return
    }
    if (user.id === currentUser?.id) {
      setToast({ message: 'You cannot delete your own account', type: 'error' })
      setConfirmDelete(false)
      return
    }
    try {
      await deleteUser.mutateAsync(user.id)
      setToast({ message: 'User deleted successfully', type: 'success' })
      setTimeout(onClose, 300)
    } catch {
      setToast({ message: 'Failed to delete user', type: 'error' })
    }
    setConfirmDelete(false)
  }, [user, currentUser, deleteUser, can, onClose])

  if (!user) return null

  const initials = user.full_name
    ? user.full_name.split(' ').map((n) => n[0]).join('').slice(0, 2).toUpperCase()
    : user.email.slice(0, 2).toUpperCase()

  return (
    <>
      <Drawer
        open={open}
        onClose={onClose}
        title="User Details"
        subtitle={user.email}
        width="w-full sm:max-w-lg"
        editable={!isEditing}
        actionLabel={user.is_active ? 'Deactivate' : 'Activate'}
        onAction={() => setConfirmToggle(true)}
      >
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Avatar size="lg" initials={initials} />
              <div className="min-w-0">
                {isEditing ? (
                  <p className="text-h6 text-text">{user.full_name || 'No name'}</p>
                ) : (
                  <p className="text-h6 text-text truncate">{user.full_name || 'No name'}</p>
                )}
                <p className="text-sm text-text-secondary truncate">{user.email}</p>
              </div>
            </div>
            {!isEditing && can(Permissions.admin.users.edit) && (
              <button
                type="button"
                onClick={handleEditClick}
                className="p-1.5 rounded-lg hover:bg-gray-100 text-text-tertiary hover:text-text transition-colors"
                title="Edit profile"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                  <path d="m15 5 4 4" />
                </svg>
              </button>
            )}
          </div>

          {isEditing && (
            <div className="space-y-3 border border-border rounded-xl p-4 bg-gray-50">
              <FormField label="Email" required>
                <Input value={editEmail} onChange={(e) => setEditEmail(e.target.value)} placeholder="user@example.com" />
              </FormField>
              <FormField label="Full Name">
                <Input value={editName} onChange={(e) => setEditName(e.target.value)} placeholder="Full name" />
              </FormField>
              <div className="flex justify-end gap-2 pt-1">
                <Button variant="ghost" size="sm" onClick={handleCancelEdit}>Cancel</Button>
                <Button variant="primary" size="sm" onClick={handleSaveProfile} loading={updateUser.isPending}>
                  Save
                </Button>
              </div>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-text-tertiary mb-1">Role</p>
              <Badge variant={roleVariants[user.role ?? ''] ?? 'default'} size="md">
                {user.role || '—'}
              </Badge>
            </div>
            <div>
              <p className="text-xs text-text-tertiary mb-1">Status</p>
              <Badge variant={user.is_active ? 'success' : 'default'} size="md">
                {user.is_active ? 'Active' : 'Inactive'}
              </Badge>
            </div>
          </div>

          <div className="space-y-3">
            <div>
              <p className="text-xs text-text-tertiary mb-1">Created</p>
              <p className="text-sm text-text">{new Date(user.created_at).toLocaleDateString()}</p>
            </div>
            <div>
              <p className="text-xs text-text-tertiary mb-1">Last Login</p>
              <p className="text-sm text-text">{user.last_login ? new Date(user.last_login).toLocaleString() : 'Never'}</p>
            </div>
          </div>

          <div className="border-t border-border pt-4">
            <p className="text-xs text-text-tertiary mb-2">Change Role</p>
            <UserRoleSelect
              value={user.role}
              onChange={handleRoleChange}
              disabled={!can(Permissions.admin.users.role)}
            />
          </div>

          <div className="flex gap-3">
            <Button
              variant="danger"
              size="sm"
              onClick={() => {
                if (user.id === currentUser?.id) {
                  setToast({ message: 'You cannot delete your own account', type: 'error' })
                  return
                }
                setConfirmDelete(true)
              }}
              disabled={!can(Permissions.admin.users.delete) || user.id === currentUser?.id}
            >
              Delete User
            </Button>
          </div>
        </div>
      </Drawer>

      {confirmDelete && (
        <ConfirmDialog
          title="Delete user"
          message={`Are you sure you want to delete "${user.full_name || user.email}"? This action cannot be undone.`}
          confirmLabel="Delete"
          onConfirm={handleDelete}
          onCancel={() => setConfirmDelete(false)}
          loading={deleteUser.isPending}
        />
      )}

      {confirmToggle && (
        <ConfirmDialog
          title={user.is_active ? 'Deactivate user' : 'Activate user'}
          message={`Are you sure you want to ${user.is_active ? 'deactivate' : 'activate'} "${user.full_name || user.email}"?`}
          confirmLabel={user.is_active ? 'Deactivate' : 'Activate'}
          onConfirm={handleToggleActive}
          onCancel={() => setConfirmToggle(false)}
          loading={updateUser.isPending}
        />
      )}

      {toast && (
        <Toast message={toast.message} type={toast.type} />
      )}
    </>
  )
}
