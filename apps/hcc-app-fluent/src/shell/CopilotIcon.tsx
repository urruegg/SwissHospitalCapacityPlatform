import { useId } from 'react';

/**
 * Sprint 27 — Copilot mark. A gradient sparkle (teal → blue → violet) used as the
 * Copilot affordance in place of the generic Fluent bot glyph. Sizes to `1em`
 * like a Fluent icon (inherits the surrounding fontSize) and is decorative
 * (`aria-hidden`) — the hosting button carries the accessible label.
 */
export function CopilotIcon({ className }: { className?: string }) {
  const gid = useId();
  return (
    <svg
      className={className}
      width="1em"
      height="1em"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      focusable="false"
    >
      <defs>
        <linearGradient id={gid} x1="3" y1="4" x2="21" y2="20" gradientUnits="userSpaceOnUse">
          <stop stopColor="#18C7D0" />
          <stop offset="0.5" stopColor="#2E7CF6" />
          <stop offset="1" stopColor="#B14CF0" />
        </linearGradient>
      </defs>
      <path
        d="M12 2c.7 4.8 4.4 8.5 9.2 9.2.5.1.5.8 0 .9C16.4 12.8 12.7 16.5 12 21.3c-.1.5-.8.5-.9 0C10.3 16.5 6.6 12.8 1.8 12.1c-.5-.1-.5-.8 0-.9C6.6 10.5 10.3 6.8 11 2c.1-.5.9-.5 1 0Z"
        fill={`url(#${gid})`}
      />
    </svg>
  );
}
