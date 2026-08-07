import { useId } from 'react';

const GRADIENT_STOPS = [
  { offset: '0', color: '#22C08A' },
  { offset: '0.5', color: '#1FA9D6' },
  { offset: '1', color: '#5A6CF0' },
] as const;

type CuraviasMarkProps = {
  /**
   * Accessible name. When provided the SVG is exposed as `role="img"` with this
   * label; when omitted the mark is treated as decorative (`aria-hidden`).
   */
  title?: string;
  className?: string;
  testId?: string;
};

/**
 * Sprint 40 START polish — the standalone Curavias brand mark from the
 * Frontier-Showcase mockup: a gradient rising path with three milestones —
 * a navy Start dot, a red Swiss-cross Care node, and a green check Success node.
 *
 * Rendered inline (not from `/public`) so it inherits crisp vector scaling and,
 * critically, a unique gradient id per instance (via `useId`) — the mark is
 * shown twice on the vision section (brandlock + "The mark" card) and duplicate
 * SVG gradient ids would be invalid markup and trip the axe duplicate-id rule.
 */
export function CuraviasMark({ title, className, testId }: CuraviasMarkProps) {
  const gradientId = useId();
  const decorative = title === undefined;

  return (
    <svg
      viewBox="0 0 300 250"
      className={className}
      data-testid={testId}
      role={decorative ? undefined : 'img'}
      aria-hidden={decorative ? true : undefined}
      aria-label={decorative ? undefined : title}
      focusable="false"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="1" x2="1" y2="0">
          {GRADIENT_STOPS.map((stop) => (
            <stop key={stop.offset} offset={stop.offset} stopColor={stop.color} />
          ))}
        </linearGradient>
      </defs>

      {/* The patient's rising path from start through care to success. */}
      <path
        d="M46,212 C130,196 150,150 258,74"
        fill="none"
        stroke={`url(#${gradientId})`}
        strokeWidth="14"
        strokeLinecap="round"
      />

      {/* Start — entry into care (navy). */}
      <circle cx="46" cy="212" r="16" fill="#365B7D" />

      {/* Care — the Swiss medical cross (federal red). */}
      <circle cx="150" cy="146" r="30" fill="#E30613" />
      <g transform="translate(150,146)">
        <rect x="-13" y="-5" width="26" height="10" rx="2" fill="#FFFFFF" />
        <rect x="-5" y="-13" width="10" height="26" rx="2" fill="#FFFFFF" />
      </g>

      {/* Success — the patient made well (green). */}
      <circle cx="258" cy="74" r="38" fill="#17B890" />
      <g transform="translate(258,74) scale(1.5)">
        <path
          d="M-14,1 L-4,12 L15,-12"
          fill="none"
          stroke="#FFFFFF"
          strokeWidth="7"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </g>
    </svg>
  );
}
