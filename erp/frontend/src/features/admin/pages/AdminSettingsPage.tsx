import { useState } from 'react'
import { PageHeader } from '@organisms/PageHeader/PageHeader'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'
import { FormField } from '@molecules/FormField/FormField'

function Toast({ message, type }: { message: string; type: 'error' | 'success' }) {
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

export function Component() {
  const [appName, setAppName] = useState('VERP')
  const [defaultRole, setDefaultRole] = useState('SALES')
  const [sessionTimeout, setSessionTimeout] = useState('30')
  const [toast, setToast] = useState<{ message: string; type: 'error' | 'success' } | null>(null)

  const handleSave = () => {
    setToast({ message: 'Settings saved successfully', type: 'success' })
  }

  return (
    <div>
      <PageHeader title="Settings" description="System configuration" />
      <div className="px-6 pb-6 space-y-6">
        <div className="bg-white rounded-xl border border-border p-6">
          <h3 className="text-h6 text-text mb-4">General</h3>
          <div className="space-y-4 max-w-lg">
            <FormField label="Application Name">
              <Input value={appName} onChange={(e) => setAppName(e.target.value)} />
            </FormField>

            <FormField label="Default Role for New Users">
              <select
                value={defaultRole}
                onChange={(e) => setDefaultRole(e.target.value)}
                className="w-full h-10 px-3 rounded-lg border border-border bg-white text-sm text-text focus:outline-none focus:ring-2 focus:ring-primary/30"
              >
                <option value="ADMIN">Admin</option>
                <option value="MANAGER">Manager</option>
                <option value="SALES">Sales</option>
                <option value="TECH">Tech</option>
              </select>
            </FormField>

            <FormField label="Session Timeout (minutes)">
              <Input
                type="number"
                value={sessionTimeout}
                onChange={(e) => setSessionTimeout(e.target.value)}
                min="5"
                max="1440"
              />
            </FormField>
          </div>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleSave}>Save Settings</Button>
        </div>
      </div>

      {toast && (
        <Toast message={toast.message} type={toast.type} />
      )}
    </div>
  )
}

Component.displayName = 'AdminSettingsPage'
