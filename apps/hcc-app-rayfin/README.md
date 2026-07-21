# hcc-app-rayfin — Sprint 13 T7 (Rayfin PoC)

> **Status: not evaluable in scope.** The Rayfin app generator is a proprietary
> CLI/toolchain that could not be run in this environment (no network-reachable
> Rayfin service or license available to the coding agent). Per the T7 time-box
> rule (design spec §2.2 and plan T7: *"If not producing comparable output by
> then, PoC stops and decision memo records 'not evaluable in scope'"*), the
> Rayfin track is recorded as **not evaluable** and does **not** block T8. The
> decision ADR ([ADR-0023](../../docs/adr/0023-app-stack-fluent-vs-rayfin-decision.md))
> therefore recommends the **Fluent** baseline for Sprint 14+.

## What is here

This folder contains a **minimal, buildable placeholder shell** (Vite + React +
TypeScript) that:

- reuses the Curavias brand tokens from
  [`curavias-token-mapping.md`](../../data-platform/reports/capacity-dashboard.Report/themes/curavias-token-mapping.md);
- renders a Curavias-branded banner so the shared Playwright smoke test has a
  target and the track stays green in CI;
- clearly labels itself as a placeholder, not a Rayfin-generated artefact.

It exists so the DoD item "*`apps/hcc-app-rayfin/` builds in CI*" is satisfiable
and the repository layout matches the design spec §3, **without** misrepresenting
placeholder code as PoC evidence.

## What was intended (and would be run with Rayfin access)

Had the Rayfin CLI been available, T7 would have:

1. generated the same two-workspace shell (Main + Backstage tabs, top bar);
2. injected the same Brandkit / Curavias theme tokens;
3. generated the one reference operational whiteboard (BedManager @ USZ);
4. reused the Fluent Playwright smoke test to prove parity;
5. scored the output against the design spec §4 rubric (build velocity, Fluent
   parity, Brandkit fidelity, customisation depth, agent-drawer feasibility,
   license/GA posture, test tooling, long-term maintenance).

The generation command, prompts used, and deviations from the Fluent baseline
would be recorded here. Because the toolchain was unavailable, those rubric
criteria are marked **not evaluable** in ADR-0023.

## Build / test

```bash
cd apps/hcc-app-rayfin
npm ci
npm run lint     # tsc --noEmit
npm run build    # tsc -b && vite build
npm run test:e2e # Playwright placeholder smoke
```
