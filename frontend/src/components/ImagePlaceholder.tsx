import { useState } from 'react'

type Props = {
  src: string
  alt: string
  label: string
  width: number
  height: number
  className?: string
  onClick?: () => void
}

export default function ImagePlaceholder({ src, alt, label, width, height, className = '', onClick }: Props) {
  const [failed, setFailed] = useState(false)

  if (failed || !src) {
    return (
      <div
        className={`placeholder ${onClick ? 'placeholder--clickable' : ''} ${className}`}
        style={{ width, height }}
        onClick={onClick}
        role={onClick ? 'button' : undefined}
        aria-label={label}
      >
        {label}
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={alt}
      className={className}
      style={{ width, height, objectFit: 'contain', cursor: onClick ? 'pointer' : undefined }}
      onClick={onClick}
      onError={() => setFailed(true)}
    />
  )
}
