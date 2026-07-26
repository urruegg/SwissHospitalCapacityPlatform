# Brandkit Icons

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-25 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | n/a (new document) |
| **Sprint** | 27 (Curavias App UX Polish, tracker #365) |
| **Applies to** | `apps/hcc-app-fluent` (internal app) and brandkit reference |

Third-party product marks used by the internal Curavias app, kept here as the
brandkit reference copy. The app consumes the same files from
`apps/hcc-app-fluent/src/assets/brand/`.

## Assets

| File | viewBox | Use |
|------|---------|-----|
| `copilot.svg` | `0 0 24 24` | The clean Microsoft Copilot glyph. Used in-app as the Copilot affordance (header + floating action button) via `src/shell/CopilotIcon.tsx`, sized to `1em`. |
| `copilot-365.svg` | `0 0 73 73` | The Microsoft 365 Copilot lockup (Copilot glyph plus the `M365` badge). Reference-only; too detailed for a small icon slot. |

## Provenance and usage

- **Source**: [`DamoBird365/microsoft-cloud-icons`](https://github.com/DamoBird365/microsoft-cloud-icons)
  (`icons/copilot/`).
- These are **Microsoft product marks**. They are used here only to reflect the
  Microsoft Copilot experience inside an internal, non-commercial demonstration
  app and must follow Microsoft trademark and brand guidelines. Do not restyle,
  recolour, or distort the marks.
- Rendered as `<img>` (not inlined) so the multi-stop gradients never collide
  across instances and the mark stays pixel-faithful.
