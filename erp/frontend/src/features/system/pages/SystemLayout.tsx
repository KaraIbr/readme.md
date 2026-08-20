import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import { Topbar } from '@organisms/Topbar/Topbar'
import { Sidebar } from '@organisms/Sidebar/Sidebar'

export function Component() {
  const navigate = useNavigate()
  const location = useLocation()

  const navItems = [
    {
      key: 'tokens',
      label: 'Tokens',
      active: location.pathname === '/system',
      onClick: () => navigate('/system'),
    },
    {
      key: 'atoms',
      label: 'Atoms',
      active: location.pathname === '/system/atoms',
      onClick: () => navigate('/system/atoms'),
    },
    {
      key: 'molecules',
      label: 'Molecules',
      active: location.pathname === '/system/molecules',
      onClick: () => navigate('/system/molecules'),
    },
    {
      key: 'organisms',
      label: 'Organisms',
      active: location.pathname === '/system/organisms',
      onClick: () => navigate('/system/organisms'),
    },
    {
      key: 'templates',
      label: 'Templates',
      active: location.pathname === '/system/templates',
      onClick: () => navigate('/system/templates'),
    },
  ]

  return (
    <div className="flex h-screen overflow-hidden bg-neutral-25">
      <Sidebar
        items={navItems}
        header={<div className="text-h5 text-text">System</div>}
      />
      <div className="flex flex-col flex-1 min-w-0">
        <Topbar
          left={
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-text-secondary">Design System /</span>
            </div>
          }
        />
        <main className="flex-1 overflow-y-auto">
          <div className="p-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}

Component.displayName = 'SystemLayout'
