import { useState } from 'react'
import type { ReactNode } from 'react'

export interface SidebarItem {
  key: string
  label: string
  icon?: ReactNode
  active?: boolean
  onClick?: () => void
  badge?: string | number
  category?: string
}

export interface SidebarProps {
  items: SidebarItem[]
  header?: ReactNode
  footer?: ReactNode
  bottomItems?: SidebarItem[]
  collapsed?: boolean
  onToggleCollapse?: () => void
  collapseAtTop?: boolean
  categoryOptions?: Record<string, { showLabel?: boolean; showDivider?: boolean; className?: string }>
  className?: string
}

function CategoryLabel({ label, collapsed }: { label: string; collapsed: boolean }) {
  if (collapsed) {
    return <div className="mx-auto my-2 w-6 h-px bg-border-light" />
  }
  return (
    <div className="px-3 pt-4 pb-1">
      <span className="text-[10px] font-semibold uppercase tracking-wider text-text-tertiary">{label}</span>
    </div>
  )
}

export function Sidebar({
  items,
  header,
  footer,
  bottomItems,
  collapsed = false,
  onToggleCollapse,
  collapseAtTop = false,
  categoryOptions = {},
  className = '',
}: SidebarProps) {
  const [hoveredKey, setHoveredKey] = useState<string | null>(null)

  const catMap = new Map<string | undefined, SidebarItem[]>()
  for (const item of items) {
    const cat = item.category ?? '__none__'
    if (!catMap.has(cat)) catMap.set(cat, [])
    catMap.get(cat)!.push(item)
  }
  const groupedItems = Array.from(catMap.entries()).map(([cat, groupItems]) => ({
    category: cat === '__none__' ? undefined : cat,
    items: groupItems,
  }))

  const collapseButton = onToggleCollapse && (
    <button
      type="button"
      onClick={onToggleCollapse}
      className="p-1.5 rounded-lg text-text-tertiary hover:text-text hover:bg-neutral-100 transition-all duration-150"
      title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
    >
      <svg className={`w-4 h-4 transition-transform duration-200 ${collapsed ? 'rotate-180' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="15 18 9 12 15 6" />
      </svg>
    </button>
  )

  return (
    <aside
      className={`
        ${collapsed ? 'w-16' : 'w-64'}
        h-full bg-white border-r border-border flex flex-col
        transition-all duration-300 ease-out-expo
        ${className}
      `.trim()}
    >
      {header && (
        <div className={`${collapsed ? 'px-2 py-4' : 'px-5 py-6'} flex items-center gap-2 ${collapseAtTop ? 'justify-between' : 'justify-center'}`}>
          {collapsed ? (
            <div className="size-8 rounded-lg bg-primary flex items-center justify-center flex-shrink-0">
              <span className="text-white font-bold text-sm">V</span>
            </div>
          ) : (
            <div className="flex-1 min-w-0">{header}</div>
          )}
          {collapseAtTop && collapseButton}
        </div>
      )}

      <nav className="flex-1 overflow-y-auto overflow-x-hidden p-3">
        {groupedItems.map((group, gi) => {
          const catKey = group.category ?? '__none__'
          const opts = categoryOptions[catKey] ?? {}
          const showLabel = opts.showLabel !== false
          const showDivider = opts.showDivider !== false

          return (
            <div key={catKey}>
              {gi > 0 && showDivider && <div className="mx-3 my-2 border-t border-border-light" />}
              {group.category && showLabel && <CategoryLabel label={group.category} collapsed={collapsed} />}
              <ul className={`flex flex-col gap-0.5 ${opts.className ?? ''}`}>
                {group.items.map((item) => {
                  const isHovered = hoveredKey === item.key
                  return (
                    <li key={item.key} className="relative">
                      {item.active && !collapsed && (
                        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-primary rounded-full" />
                      )}
                      <button
                        type="button"
                        onClick={item.onClick}
                        onMouseEnter={() => setHoveredKey(item.key)}
                        onMouseLeave={() => setHoveredKey(null)}
                        title={collapsed ? item.label : undefined}
                        className={`
                          w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                          transition-all duration-150
                          whitespace-nowrap
                          ${collapsed ? 'justify-center' : 'pl-4'}
                          ${
                            item.active
                              ? 'bg-primary-soft text-primary'
                              : 'text-text-secondary hover:bg-neutral-100 hover:text-text hover:translate-x-0.5'
                          }
                        `.trim()}
                      >
                        {item.icon && (
                          <span className={`size-5 flex-shrink-0 [&_svg]:size-5 transition-transform duration-150 ${isHovered ? 'scale-110' : ''}`}>
                            {item.icon}
                          </span>
                        )}
                        {!collapsed && (
                          <>
                            <span className="flex-1 text-left truncate">{item.label}</span>
                            {item.badge && (
                              <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-neutral-100 text-text-secondary">
                                {item.badge}
                              </span>
                            )}
                          </>
                        )}
                      </button>
                    </li>
                  )
                })}
              </ul>
            </div>
          )
        })}
      </nav>

      {!collapseAtTop && collapseButton && (
        <div className="border-t border-border-light p-3 flex justify-center">
          {collapseButton}
        </div>
      )}

      {bottomItems && bottomItems.length > 0 && !collapsed && (
        <div className="border-t border-border-light p-3 space-y-0.5">
          {bottomItems.map((item) => (
            <button
              key={item.key}
              type="button"
              onClick={item.onClick}
              className={`
                w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                transition-all duration-150
                ${
                  item.active
                    ? 'bg-primary-soft text-primary'
                    : 'text-text-secondary hover:bg-neutral-100 hover:text-text'
                }
              `.trim()}
            >
              {item.icon && (
                <span className="size-5 flex-shrink-0 [&_svg]:size-5">{item.icon}</span>
              )}
              <span className="flex-1 text-left truncate">{item.label}</span>
            </button>
          ))}
        </div>
      )}

      {footer && !collapsed && (
        <div className={`px-5 py-3 border-t border-border-light text-[11px] text-text-tertiary ${bottomItems?.length ? '' : ''}`}>{footer}</div>
      )}
    </aside>
  )
}
