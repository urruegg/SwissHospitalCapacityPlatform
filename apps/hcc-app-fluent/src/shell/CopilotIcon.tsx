import copilotMarkUrl from '../assets/brand/copilot.svg';

/**
 * Sprint 27 — Copilot mark. The official Microsoft Copilot glyph (source:
 * DamoBird365/microsoft-cloud-icons `icons/copilot/copilot.svg`). Rendered as an
 * `<img>` so its multi-stop gradients never collide across instances (the mark
 * appears in both the header and the floating FAB at once) and it stays
 * pixel-faithful. Sizes to `1em` like a Fluent icon (inherits the surrounding
 * fontSize) and is decorative (`aria-hidden`) — the hosting button carries the
 * accessible label.
 */
export function CopilotIcon({ className }: { className?: string }) {
  return (
    <img
      className={className}
      src={copilotMarkUrl}
      alt=""
      aria-hidden="true"
      style={{ width: '1em', height: '1em', display: 'inline-block' }}
    />
  );
}
