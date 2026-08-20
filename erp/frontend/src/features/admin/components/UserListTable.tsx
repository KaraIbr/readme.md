import { useState, useMemo } from 'react'
import { DataTable } from '@organisms/DataTable/DataTable'
import { Badge } from '@atoms/Badge/Badge'
import { UserOverflowMenu } from './UserOverflowMenu'
import type { AdminUser } from '../types'
import type { Column } from '@organisms/DataTable/DataTable'

const roleVariants: Record<string, 'info' | 'success' | 'warning' | 'default'> = {
  ADMIN: 'info',
  MANAGER: 'success',
  SALES: 'warning',
  TECH: 'default',
}

interface UserListTableProps {
  users: AdminUser[]
  onSelectUser: (user: AdminUser) => void
  onDeactivate: (user: AdminUser) => void
  onDelete: (user: AdminUser) => void
}

export function UserListTable({ users, onSelectUser, onDeactivate, onDelete }: UserListTableProps) {
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState<string>('ALL')
  const [statusFilter, setStatusFilter] = useState<string>('ALL')

  const filteredUsers = useMemo(() => {
    return users.filter((u) => {
      const matchesSearch = search === '' ||
        u.full_name?.toLowerCase().includes(search.toLowerCase()) ||
        u.email.toLowerCase().includes(search.toLowerCase())
      const matchesRole = roleFilter === 'ALL' || u.role === roleFilter
      const matchesStatus = statusFilter === 'ALL' ||
        (statusFilter === 'ACTIVE' && u.is_active) ||
        (statusFilter === 'INACTIVE' && !u.is_active)
      return matchesSearch && matchesRole && matchesStatus
    })
  }, [users, search, roleFilter, statusFilter])

  const columns: Column<AdminUser>[] = [
    {
      key: 'full_name',
      header: 'Name',
      render: (u) => (
        <button
          type="button"
          onClick={() => onSelectUser(u)}
          className="font-medium text-text hover:text-primary hover:underline text-left"
        >
          {u.full_name || u.email}
        </button>
      ),
    },
    { key: 'email', header: 'Email' },
    {
      key: 'role',
      header: 'Role',
      render: (u) => (
        <Badge variant={roleVariants[u.role ?? ''] ?? 'default'} size="sm">
          {u.role || '—'}
        </Badge>
      ),
    },
    {
      key: 'is_active',
      header: 'Status',
      render: (u) => (
        <Badge variant={u.is_active ? 'success' : 'default'} size="sm">
          {u.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'created_at',
      header: 'Created',
      render: (u) => (
        <span className="text-sm text-text-secondary">
          {new Date(u.created_at).toLocaleDateString()}
        </span>
      ),
    },
    {
      key: 'actions',
      header: '',
      render: (u) => (
        <UserOverflowMenu
          onEdit={() => onSelectUser(u)}
          onDeactivate={() => onDeactivate(u)}
          onDelete={() => onDelete(u)}
          isActive={u.is_active}
        />
      ),
    },
  ]

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="text"
          placeholder="Search by name or email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="h-9 px-3 rounded-lg border border-border bg-white text-sm text-text placeholder:text-text-tertiary focus:outline-none focus:ring-2 focus:ring-primary/30 w-64"
        />
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="h-9 px-3 pr-8 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 appearance-none cursor-pointer bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2012%2012%22%20fill%3D%22none%22%3E%3Cpath%20d%3D%22M3%204.5L6%207.5L9%204.5%22%20stroke%3D%22%236B7280%22%20stroke-width%3D%221.5%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E')] bg-[length:12px] bg-[right_8px_center] bg-no-repeat"
        >
          <option value="ALL">All Roles</option>
          <option value="ADMIN">Admin</option>
          <option value="MANAGER">Manager</option>
          <option value="SALES">Sales</option>
          <option value="TECH">Tech</option>
        </select>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="h-9 px-3 pr-8 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30 appearance-none cursor-pointer bg-[url('data:image/svg+xml;charset=utf-8,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%2212%22%20height%3D%2212%22%20viewBox%3D%220%200%2012%2012%22%20fill%3D%22none%22%3E%3Cpath%20d%3D%22M3%204.5L6%207.5L9%204.5%22%20stroke%3D%22%236B7280%22%20stroke-width%3D%221.5%22%20stroke-linecap%3D%22round%22%20stroke-linejoin%3D%22round%22%2F%3E%3C%2Fsvg%3E')] bg-[length:12px] bg-[right_8px_center] bg-no-repeat"
        >
          <option value="ALL">All Status</option>
          <option value="ACTIVE">Active</option>
          <option value="INACTIVE">Inactive</option>
        </select>
        {(search || roleFilter !== 'ALL' || statusFilter !== 'ALL') && (
          <button
            type="button"
            onClick={() => { setSearch(''); setRoleFilter('ALL'); setStatusFilter('ALL') }}
            className="text-sm text-primary hover:underline"
          >
            Clear filters
          </button>
        )}
      </div>

      <DataTable<AdminUser>
        columns={columns}
        data={filteredUsers}
        keyExtractor={(u) => String(u.id)}
        emptyTitle="No users found"
        emptyDescription={search || roleFilter !== 'ALL' || statusFilter !== 'ALL'
          ? 'Try adjusting your filters.'
          : 'Create your first user to get started.'}
      />
    </div>
  )
}
