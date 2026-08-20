export type AvatarSize = 'sm' | 'md' | 'lg'

export interface AvatarProps {
  size?: AvatarSize
  src?: string
  alt?: string
  initials?: string
  className?: string
}

const sizeMap: Record<AvatarSize, { size: number; text: string }> = {
  sm: { size: 32, text: 'text-xs' },
  md: { size: 40, text: 'text-sm' },
  lg: { size: 48, text: 'text-base' },
}

export function Avatar({
  size = 'md',
  src,
  alt = '',
  initials,
  className = '',
}: AvatarProps) {
  const config = sizeMap[size]

  if (src) {
    return (
      <img
        src={src}
        alt={alt}
        className={`rounded-full object-cover flex-shrink-0 ${className}`}
        style={{ width: config.size, height: config.size }}
      />
    )
  }

  return (
    <div
      className={`
        rounded-full bg-neutral-100 text-text-secondary font-medium
        flex items-center justify-center flex-shrink-0
        ${config.text}
        ${className}
      `.trim()}
      style={{ width: config.size, height: config.size }}
    >
      {initials ? initials.slice(0, 2).toUpperCase() : null}
    </div>
  )
}
