import { colors, typography, spacing, radius, shadows } from '@tokens'

function ColorSwatch({ name, value }: { name: string; value: string }) {
  return (
    <div className="flex items-center gap-4 p-4 rounded-lg border border-border bg-white">
      <div
        className="size-12 rounded-lg border border-border flex-shrink-0"
        style={{ backgroundColor: value }}
      />
      <div className="min-w-0">
        <p className="text-sm font-medium text-text">{name}</p>
        <p className="text-xs text-text-tertiary font-mono">{value}</p>
      </div>
    </div>
  )
}

function TokenSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mb-10">
      <h2 className="text-h4 text-text mb-5">{title}</h2>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-3">
        {children}
      </div>
    </div>
  )
}

export function Component() {
  return (
    <div>
      <h1 className="text-h2 text-text mb-8">Design Tokens</h1>

      <TokenSection title="Primary Colors">
        <ColorSwatch name="Primary" value={colors.primary} />
        <ColorSwatch name="Primary Hover" value={colors.primaryHover} />
        <ColorSwatch name="Primary Soft" value={colors.primarySoft} />
        <ColorSwatch name="Warning" value={colors.warning} />
        <ColorSwatch name="Warning Hover" value={colors.warningHover} />
        <ColorSwatch name="Warning Soft" value={colors.warningSoft} />
        <ColorSwatch name="Info" value={colors.info} />
        <ColorSwatch name="Info Hover" value={colors.infoHover} />
        <ColorSwatch name="Info Soft" value={colors.infoSoft} />
        <ColorSwatch name="Danger" value={colors.danger} />
        <ColorSwatch name="Danger Hover" value={colors.dangerHover} />
        <ColorSwatch name="Danger Soft" value={colors.dangerSoft} />
      </TokenSection>

      <TokenSection title="Neutral Scale">
        {Object.entries(colors.neutral).map(([key, value]) => (
          <ColorSwatch key={key} name={`Neutral ${key}`} value={value} />
        ))}
        <ColorSwatch name="Text" value={colors.text} />
        <ColorSwatch name="Text Secondary" value={colors.textSecondary} />
        <ColorSwatch name="Text Tertiary" value={colors.textTertiary} />
      </TokenSection>

      <TokenSection title="Surface & Border">
        <ColorSwatch name="Border" value={colors.border} />
        <ColorSwatch name="Border Light" value={colors.borderLight} />
        <ColorSwatch name="Surface" value={colors.surface} />
        <ColorSwatch name="Surface Secondary" value={colors.surfaceSecondary} />
      </TokenSection>

      <div className="mb-10">
        <h2 className="text-h4 text-text mb-5">Typography</h2>
        <div className="space-y-4">
          <div className="p-4 rounded-lg border border-border bg-white">
            <p className="text-h1 text-text">Heading 1 (2.5rem / 800)</p>
            <p className="text-xs text-text-tertiary mt-1">font-size: {typography.fontSize['5xl']} / weight: {typography.fontWeight.extrabold}</p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-white">
            <p className="text-h2 text-text">Heading 2 (2rem / 700)</p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-white">
            <p className="text-h3 text-text">Heading 3 (1.5rem / 600)</p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-white">
            <p className="text-h4 text-text">Heading 4 (1.25rem / 600)</p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-white">
            <p className="text-h5 text-text">Heading 5 (1.125rem / 600)</p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-white">
            <p className="text-body text-text">Body (0.875rem / 400) — The quick brown fox jumps over the lazy dog.</p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-white">
            <p className="text-body-medium text-text">Body Medium (0.875rem / 500) — The quick brown fox jumps over the lazy dog.</p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-white">
            <p className="text-small text-text-secondary">Small (0.8125rem / 400) — Used for labels and secondary information.</p>
          </div>
          <div className="p-4 rounded-lg border border-border bg-white">
            <p className="text-caption text-text-tertiary">Caption (0.75rem / 400) — Used for help text and timestamps.</p>
          </div>
        </div>
      </div>

      <div className="mb-10">
        <h2 className="text-h4 text-text mb-5">Spacing</h2>
        <div className="space-y-3">
          {Object.entries(spacing).map(([key, value]) => {
            const numKey = Number(key)
            return (
              <div key={key} className="flex items-center gap-4 p-3 rounded-lg border border-border bg-white">
                <span className="text-sm font-medium text-text w-12">spc-{key}</span>
                <div
                  className="h-6 bg-primary rounded flex-shrink-0"
                  style={{ width: numKey || 2 }}
                />
                <span className="text-xs text-text-tertiary">{value}</span>
              </div>
            )
          })}
        </div>
      </div>

      <div className="mb-10">
        <h2 className="text-h4 text-text mb-5">Border Radius</h2>
        <div className="flex gap-4 flex-wrap">
          {Object.entries(radius).filter(([k]) => k !== 'none' && k !== 'full').map(([key, value]) => (
            <div key={key} className="flex flex-col items-center gap-2 p-4 rounded-lg border border-border bg-white">
              <div
                className="size-16 bg-primary-soft border border-primary"
                style={{ borderRadius: value }}
              />
              <p className="text-sm font-medium text-text">{key}</p>
              <p className="text-xs text-text-tertiary">{value}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="mb-10">
        <h2 className="text-h4 text-text mb-5">Shadows</h2>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(shadows).map(([key, value]) => (
            <div key={key} className="p-6 rounded-lg bg-white" style={{ boxShadow: value }}>
              <p className="text-sm font-medium text-text capitalize">{key}</p>
              <p className="text-xs text-text-tertiary mt-1 font-mono break-all">{value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

Component.displayName = 'TokensPage'
