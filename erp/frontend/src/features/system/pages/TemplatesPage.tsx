import { Sidebar } from '@organisms/Sidebar/Sidebar'
import { Topbar } from '@organisms/Topbar/Topbar'
import { Button } from '@atoms/Button/Button'
import { Input } from '@atoms/Input/Input'

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-10">
      <h2 className="text-h4 text-text mb-5">{title}</h2>
      {children}
    </div>
  )
}

export function Component() {
  const sampleNavItems = [
    { key: '1', label: 'Dashboard', active: true, onClick: () => {} },
    { key: '2', label: 'Leads', onClick: () => {} },
    { key: '3', label: 'Contacts', onClick: () => {} },
    { key: '4', label: 'Companies', onClick: () => {} },
  ]

  return (
    <div>
      <h1 className="text-h2 text-text mb-8">Templates</h1>

      <Section title="Auth Template">
        <div className="border border-border rounded-lg overflow-hidden">
          <div className="min-h-[400px] flex items-center justify-center bg-neutral-25 px-4">
            <div className="w-full max-w-md bg-surface rounded-xl shadow-elevated p-8">
              <div className="flex justify-center mb-8">
                <div className="size-10 rounded-lg bg-primary flex items-center justify-center">
                  <span className="text-white font-bold">V</span>
                </div>
              </div>
              <div className="text-center mb-8">
                <h1 className="text-h3 text-text">Welcome back</h1>
                <p className="text-body text-text-secondary mt-1.5">Sign in to your account to continue</p>
              </div>
              <div className="space-y-4">
                <Input placeholder="Email" type="email" />
                <Input placeholder="Password" type="password" />
                <Button className="w-full">Sign In</Button>
              </div>
            </div>
          </div>
        </div>
      </Section>

      <Section title="Dashboard Template">
        <div className="border border-border rounded-lg overflow-hidden" style={{ height: 480 }}>
          <div className="flex h-full overflow-hidden bg-neutral-25">
            <Sidebar
              items={sampleNavItems}
              header={<div className="text-sm font-bold text-text">VERP CRM</div>}
            />
            <div className="flex flex-col flex-1 min-w-0">
              <Topbar
                left={<span className="text-sm font-medium text-text-secondary">Dashboard</span>}
                right={
                  <div className="flex items-center gap-3">
                    <span className="text-sm text-text-secondary">John Doe</span>
                    <div className="size-8 rounded-full bg-neutral-200" />
                  </div>
                }
              />
              <div className="flex-1 overflow-y-auto p-6">
                <div className="grid grid-cols-3 gap-4">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="h-24 rounded-lg border border-border bg-white p-4 flex items-center justify-center text-sm text-text-tertiary">
                      Metric Card {i}
                    </div>
                  ))}
                </div>
                <div className="mt-4 h-48 rounded-lg border border-border bg-white flex items-center justify-center text-sm text-text-tertiary">
                  Main Content Area
                </div>
              </div>
            </div>
          </div>
        </div>
      </Section>
    </div>
  )
}

Component.displayName = 'TemplatesPage'
