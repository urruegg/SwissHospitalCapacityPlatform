# Web IQ live signals without Fabric Admin — Design

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-08-12 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Accepted (decided autonomously; user to review) |
| **Previous Version** | n/a (new design) |
| **Plan** | [`docs/superpowers/plans/2026-08-12-sprint-44-webiq-live-eh-to-fabric-to-app-plan.md`](../plans/2026-08-12-sprint-44-webiq-live-eh-to-fabric-to-app-plan.md) |
| **Governance ADR** | [`docs/adr/0060-webiq-external-signal-channel.md`](../../adr/0060-webiq-external-signal-channel.md) |

## Problem

The preferred live path is `provider-runner → Event Hub → Fabric gold →
agent-host golden surface → app`. It is blocked at exactly one hop: the
agent-host reading `gold.ext_fact_signal` from **OneLake as an external
application** requires a Fabric **tenant-admin** setting ("allow apps/service
principals to access OneLake", Sprint 43 WS-2). We have no Fabric Admin rights,
so we need a path that puts live signals in the app **without** that setting.

The blocker is narrow — only the OneLake external read is gated. Event Hub RBAC,
Storage RBAC, and Container App code are all within our control.

## Options evaluated

| # | The agent-host reads… | Fabric Admin | Reuses gold→BoardSignal mapping | Robustness | Verdict |
|---|-----------------------|--------------|--------------------------------|------------|---------|
| 0 | OneLake `gold.ext_fact_signal` (abfss) | required ❌ | yes | — | **blocked** |
| A | a Blob a **Fabric notebook** writes from gold | none ✅ | yes | medium | keeps Fabric in-loop but needs Eventstream + notebook + schedule + capacity |
| B″ | the **Event Hub** stream directly (cached) | none ✅ | new envelope mapping | medium | smallest footprint; fiddly bounded multi-partition read + TTL cache per request |
| **B′** | a gold-shaped **Blob snapshot the provider-runner writes** each pass | none ✅ | yes | **high** | trivial blob GET; reuses medallion `to_gold_signal` + the shipped mapping |

## Decision — Option B′ (runner-written gold snapshot to Blob)

The provider-runner already computes the `DC-EXT-SIGNAL-v1` records every cycle.
In the same pass it also projects them through the **existing pure medallion
functions** (`build_gold_signals.to_gold_signal` / `ext_dim_source_row`,
extended to carry `webCitations`) and writes a small **gold-shaped snapshot**
(`ext_fact_signal[]` + `ext_dim_source[]`) as JSON to a Blob container. The
agent-host golden service reads that one Blob (env-gated, fixture fallback) and
serves it through the **already-shipped** `golden/signals.gold_rows_to_board_signals`
mapping, merged into the `occupancy` + `crisis` payloads.

### Why B′

- **No Fabric Admin** — no OneLake external access; only Storage RBAC (grantable
  by us) and Container App env.
- **Robust for a demo** — serving is a single Blob GET (cacheable), not a
  multi-partition Event Hub scan.
- **Reuses work** — the medallion gold projection **and** the Slice-1a
  `gold_rows_to_board_signals` mapping are reused unchanged; the gold *shape and
  logic* stay in the loop (honours the "Fabric gold" intent minus OneLake).
- **Forward-compatible** — when a Fabric Admin later enables OneLake external
  access, swap the Blob reader for `FabricDeltaClient.query('gold.ext_fact_signal')`
  and the identical mapping serves real OneLake gold. No app change either way.
- **Improves the real path** — extending `to_gold_signal` with `webCitations`
  fixes the current gold-projection gap (gold drops the Trust-B web citations).

## Architecture

```text
provider-runner (Container App, every 900 s)
  records ──► Event Hub  (unchanged; feeds DQA / triage / future Fabric)
  records ──► to_gold_signal(+webCitations) ──► signals-snapshot.json ──► Blob
                                                                           │
agent-host golden service  ◄──────────── reads Blob (env-gated, TTL) ─────┘
  gold rows ──► gold_rows_to_board_signals ──► merge into occupancy/crisis
                                                     │
hcc-app-fluent (Live mode)  ◄── /golden/{occupancy,crisis} ── provenance: live
```

## Components & interfaces

- **Runner snapshot writer** (`data-platform/scripts/external-signals/run.py` +
  a `snapshot.py` helper): pure `build_snapshot(records) -> dict` (gold-shaped)
  unit-tested offline; a lazy Blob writer (mirrors `_eventhub_emit`) behind an
  env gate (`SIGNALS_SNAPSHOT_URL`/container). Absent env ⇒ no snapshot (CI safe).
- **Gold projection extension**: add `ext_web_citations` to `to_gold_signal`
  (additive; existing tests updated).
- **Agent-host snapshot reader** (`golden/signals_source.py`): env-gated
  (`SIGNALS_SNAPSHOT_URL`) Blob reader with injected fetcher (unit-testable),
  short TTL cache; returns `(fact_rows, source_rows)` for the mapping. Unset ⇒
  fixtures (current behaviour).
- **Golden service merge**: when the snapshot source yields rows, replace/merge
  the `signals` list in the `occupancy` + `crisis` payloads via the shipped
  mapping.

## Error handling

- Snapshot missing/unreadable ⇒ agent-host falls back to fixtures flagged (no
  hang), matching the existing `degraded` golden-source contract.
- Runner Blob write failure ⇒ logged, never blocks the Event Hub publish (the
  authoritative sink); isolated like a single-provider failure.

## Testing

- Pure `build_snapshot` + extended `to_gold_signal` (offline, TDD).
- Agent-host snapshot reader with an injected fetcher (offline).
- Golden service: occupancy/crisis payloads carry live signals when the snapshot
  env is set; fixtures otherwise (parity guard stays green).
- Manual: SIT Live-mode screenshot showing `provenance: live` signals.

## Implementation-verification points (not blockers)

- Storage account reachability: the runner runs in the non-VNet
  `cae-sim-ihzhhpf-sit`; confirm the chosen Storage account (e.g.
  `stdpihzhhpfsity26y`) is reachable (public + RBAC or firewall-allow) from it,
  and from the agent-host's CAE. Pick/allow a container accordingly.
- Role assignments: `Storage Blob Data Contributor` (runner MI) +
  `Storage Blob Data Reader` (agent-host MI) on the container scope.

## Out of scope

- The Fabric analytics path (Eventstream → gold → semantic model → Power BI
  Direct Lake) — that reads gold **inside** Fabric and does not need the OneLake
  external-app setting; it can proceed independently for the reporting story.
- PROD cut-over (SIT demo first).
