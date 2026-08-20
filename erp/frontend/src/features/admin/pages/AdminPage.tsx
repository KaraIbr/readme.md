import { useNavigate } from 'react-router-dom'
import { PageHeader } from '@organisms/PageHeader/PageHeader'

export function Component() {
  const navigate = useNavigate()

  return (
    <div>
      <PageHeader title="Admin" description="System administration" />
      <div className="px-6 pb-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <button
            type="button"
            onClick={() => navigate('/admin/users')}
            className="p-6 rounded-xl border border-border bg-white text-left hover:shadow-subtle transition-shadow"
          >
            <h3 className="text-h5 text-text mb-1">Users</h3>
            <p className="text-body text-text-secondary">Manage system users</p>
          </button>
          <button
            type="button"
            onClick={() => navigate('/admin/permissions')}
            className="p-6 rounded-xl border border-border bg-white text-left hover:shadow-subtle transition-shadow"
          >
            <h3 className="text-h5 text-text mb-1">Permissions</h3>
            <p className="text-body text-text-secondary">Manage roles and permissions</p>
          </button>

          <button
            type="button"
            onClick={() => navigate('/admin/audit')}
            className="p-6 rounded-xl border border-border bg-white text-left hover:shadow-subtle transition-shadow"
          >
            <h3 className="text-h5 text-text mb-1">Audit Log</h3>
            <p className="text-body text-text-secondary">View pipeline stage transitions</p>
          </button>
        </div>
      </div>
    </div>
  )
}

Component.displayName = 'AdminPage'
