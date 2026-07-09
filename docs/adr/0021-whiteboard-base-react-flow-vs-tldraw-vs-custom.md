# ADR-0021 — Whiteboard base for the operational whiteboard (React Flow vs tldraw vs custom)

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Deciders** | @urruegg |
| **Superseded by** | — |

> Sprint 13 T3 kickoff mini-ADR. Records the whiteboard-base choice for the
> BedManager reference operational whiteboard (design spec
> [`2026-07-09-sprint-13-app-design.md`](../superpowers/specs/2026-07-09-sprint-13-app-design.md) §5.2)
> and the risk mitigation in §9 ("choose one, document why; wrap behind a thin
> adapter so replacement is bounded").

## Context

The BedManager whiteboard renders six card types on a spatial surface. Three
candidate bases were considered:

1. **React Flow** — node/edge graph library. Rich pan/zoom, edges, handles.
2. **tldraw** — full drawing/whiteboard SDK. Freeform shapes, collaboration.
3. **Custom** — a small absolutely-positioned canvas with a card registry.

Sprint 13 scope (design spec §2.3) is deliberately narrow: **mock data only, no
edges, no zoom, in-memory layout, no persistence**. Real Fabric wiring and any
graph/edge semantics are Sprint 14+.

## Decision

Use a **custom lightweight canvas** for Sprint 13:

- `whiteboard/Canvas.tsx` — absolutely-positioned card host over a dotted grid.
- `whiteboard/CardRegistry.tsx` — maps `CardType` → renderer; the canvas is
  card-agnostic.
- `whiteboard/LayoutManager.tsx` — in-memory positions as a swappable hook.

The base is wrapped behind the `Canvas` component and the `LayoutManager` hook so
that swapping in React Flow or tldraw later is bounded to those two files.

## Rationale

- **No edges/zoom needed in S13.** React Flow's and tldraw's value (edges,
  zoom/pan, collaboration) is unused by the six-card reference board; adopting
  either now adds a heavy dependency and API surface for no S13 benefit.
- **Dependency and bundle footprint.** The Fluent bundle is already large; a
  custom canvas keeps the whiteboard dependency-free.
- **Bounded replacement.** The registry + layout-manager seam means a future
  board that needs edges/zoom can adopt React Flow (preferred if graph semantics
  arrive) without touching the six card components.
- **License/GA posture.** Avoids taking on tldraw's licensing terms or React
  Flow's version cadence before we know we need them.

## Consequences

- Sprint 13 ships no graph/edge or zoom affordance — acceptable per §2.3.
- If Sprint 14+ requires edges, zoom, or multi-user collaboration, revisit with a
  superseding ADR; the recommended upgrade path is **React Flow** for
  graph/edge boards and **tldraw** only if freeform drawing is required.
- Whiteboard layout is not persisted (in-memory only), consistent with §2.3.
