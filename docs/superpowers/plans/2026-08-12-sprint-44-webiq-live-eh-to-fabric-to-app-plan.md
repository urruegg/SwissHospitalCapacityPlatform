# Sprint 44 — Web IQ live path: Event Hub → Fabric → app — Implementation Plan

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-08-12 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | In progress |
| **Previous Version** | 1.0.0 (initial OneLake-read plan); this bump pivots the app read to the no-Fabric-Admin **Option B′** (runner-written gold-shaped Blob snapshot) per [the without-admin design](../specs/2026-08-12-webiq-live-signals-without-fabric-admin-design.md) |
| **Design (no-admin)** | [`docs/superpowers/specs/2026-08-12-webiq-live-signals-without-fabric-admin-design.md`](../specs/2026-08-12-webiq-live-signals-without-fabric-admin-design.md) |
| **Sprint doc** | [`docs/sprints/sprint-44-webiq-external-signal-channel.md`](../../sprints/sprint-44-webiq-external-signal-channel.md) |
| **Governance ADR** | [`docs/adr/0060-webiq-external-signal-channel.md`](../../adr/0060-webiq-external-signal-channel.md) |

## Goal

Make live external-signal envelopes flow end-to-end so they are visible in the
Curavias app: **provider-runner → Event Hub → Fabric `gold.ext_fact_signal` →
agent-host golden surface → app board signal panels**. This is the user's
preferred path (over the batch-only or app-only alternatives).

## Current state (verified 2026-08-12)

- **Live & proven:** SIT + PROD provider-runners publish `DC-EXT-SIGNAL-v1` to the
  Event Hub every 900 s (SIT ingress = 21 msgs metric-proven).
- **Gap A — EH → Fabric:** no `es-ihzhhpf-events` Eventstream / Eventhouse deployed;
  the `external-signals` medallion notebooks read the synthetic `signals_synth` seed,
  so `gold.ext_fact_signal` is not fed from the Event Hub.
- **Gap B — Fabric → app:** the agent-host golden service
  ([`apps/hcc-agent-host/src/golden/service.py`](../../../apps/hcc-agent-host/src/golden/service.py))
  serves **exported JSON fixtures**, not live `gold.ext_fact_signal`. A live Fabric
  Delta seam (`FabricDeltaClient`, Sprint 43 WS-2, env-gated on `FABRIC_WORKSPACE_ID`
  / `FABRIC_LAKEHOUSE_ID`) exists but is unused by the board payloads.
- **App → agent-host:** already wired — Live mode reads `<agent-host>/golden/{resource}`
  ([`golden-source-client.ts`](../../../apps/hcc-app-fluent/src/data/roleboard/golden-source-client.ts)).

## Key decisions

| # | Decision | Rationale |
|---|----------|-----------|
| P1 | **App read uses Option B′ (no Fabric Admin):** the provider-runner writes a gold-shaped signals snapshot to Blob; the agent-host reads that Blob. | The agent-host OneLake external read is tenant-admin-gated; B′ sidesteps it with Storage RBAC we control. See the without-admin design. |
| P2 | **Reuse the medallion `to_gold_signal`/`ext_dim_source_row` pure functions** in the runner to shape the snapshot; extend them with `webCitations`. | Keeps the gold shape/logic in the loop; fixes the gold web-citations gap; the shipped `gold_rows_to_board_signals` mapping consumes it unchanged. |
| P3 | **Env-gated everywhere, fixture fallback.** Snapshot write + read are gated on `SIGNALS_SNAPSHOT_URL`; unset ⇒ current behaviour (CI + un-provisioned envs unchanged). | Safe rollout; no CI network calls; matches the existing `degraded` golden-source contract. |
| P4 | **Forward-compatible:** when a Fabric Admin later enables OneLake external access, swap the Blob reader for `FabricDeltaClient.query('gold.ext_fact_signal')`; identical mapping, no app change. | Preserves the option value of the true OneLake path without blocking now. |
| P5 | **Fabric analytics path (Eventstream → gold → Power BI Direct Lake) is a separate, independent track** — it reads gold inside Fabric and needs no admin setting. | Keeps the reporting story alive without coupling it to the app read. |

## Fabric Admin dependency — resolved by B′

The original OneLake read needed a Fabric **tenant-admin** setting we do not have.
**Option B′ removes that dependency** for the app read (Storage RBAC only, which we
control). The true OneLake read is retained as a forward-compatible swap (P4) for
when an admin enables it. No user/admin action is required to ship the live app
signals.

## Slices

### Slice 1 — Golden service mapping (in-repo, TDD) — DONE (1a)

- **1a (done, `4af549bb`):** pure `golden/signals.gold_rows_to_board_signals`
  (`gold.ext_fact_signal` + `ext_dim_source` rows → `BoardSignal[]`), 5 tests green.
- **1b:** extend `to_gold_signal` (+`ext_web_citations`) and the mapping to carry
  `webCitations`; keep the app parity guard green.

### Slice 2 — Runner writes gold-shaped snapshot to Blob (TDD)

- Pure `snapshot.build_snapshot(records) -> {ext_fact_signal[], ext_dim_source[]}`
  reusing `to_gold_signal`/`ext_dim_source_row`; unit-tested offline.
- Env-gated lazy Blob writer in `run.py` (mirrors `_eventhub_emit`), gated on
  `SIGNALS_SNAPSHOT_URL`; failure logged, never blocks the Event Hub publish.
- Grant the runner MI `Storage Blob Data Contributor` on the container scope.

### Slice 3 — Agent-host reads snapshot + golden merge (TDD)

- `golden/signals_source.py`: env-gated (`SIGNALS_SNAPSHOT_URL`) Blob reader with an
  injected fetcher + short TTL; returns `(fact_rows, source_rows)`; unset ⇒ fixtures.
- Golden service merges the mapped signals into the `occupancy` + `crisis` payloads.
- Grant the agent-host MI `Storage Blob Data Reader` on the container scope.

### Slice 4 — Deploy + verify end-to-end

- Deploy runner (snapshot env) + agent-host (snapshot env), gated by
  `approved-to-apply`; confirm the Blob updates each cycle; app Live mode shows the
  Web IQ (+ other) signals with `provenance: live` + web citations. Evidence captured.

## Verification

- Slices 1b/2/3: `apps/hcc-agent-host` + `data-platform/scripts/external-signals`
  unit suites green; app vitest parity guard green.
- Slice 4: the Blob snapshot updates each runner cycle; app Live-mode screenshot with
  `provenance: live` + web citations on the OOA/CSA signal panel. Evidence captured.

## Out of scope / follow-up

- PROD cut-over (SIT demo first).
- The true OneLake read (`FabricDeltaClient`) — forward-compatible swap once a Fabric
  Admin enables external OneLake access (P4).
- The Fabric analytics path (Eventstream → gold → Power BI Direct Lake) — independent
  track, no admin needed (P5).
