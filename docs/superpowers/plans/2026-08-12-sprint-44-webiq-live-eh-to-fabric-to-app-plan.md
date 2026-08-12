# Sprint 44 — Web IQ live path: Event Hub → Fabric → app — Implementation Plan

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-08-12 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | In progress |
| **Previous Version** | n/a (new plan) |
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
| P1 | **Fabric leg = Eventstream → Lakehouse Delta table** (not Eventhouse KQL). | The medallion + golden service already read the Lakehouse `lh_ihzhhpf_sit`; a Lakehouse destination reuses the existing gold path with no new store. |
| P2 | **Gold projection reuses the existing silver/gold notebooks**, repointed from the synthetic seed to the Eventstream-landed bronze table. | Minimal new code; keeps the `gold.ext_fact_signal` contract stable. |
| P3 | **Golden service reads external signals from `gold.ext_fact_signal` via the existing `FabricDeltaClient` seam, env-gated, fixture fallback.** | Additive, fully unit-testable offline; lights up automatically once gold is fed; no app change. |
| P4 | **Build Fabric → app (Slice 1) first**, since it is entirely in-repo + TDD-able and independent of Fabric-side provisioning. | De-risks the leg I control; the ingestion leg has external dependencies. |

## External blocker (needs the user / a Fabric admin)

- Live Fabric Delta reads from the agent-host were **"blocked pending a Fabric
  Administrator tenant-setting change"** (Sprint 43 WS-2 test notes: *Service
  principals / MI can use Fabric APIs*). Slice 1 is built + unit-tested regardless;
  the live SIT cut-over of the golden surface depends on that tenant setting being
  enabled. Flag to the user.

## Slices

### Slice 1 — Golden service reads `gold.ext_fact_signal` (in-repo, TDD)

- Extend `golden/service.py` (or a small `golden/signals.py` helper) to, when
  `FABRIC_WORKSPACE_ID`/`FABRIC_LAKEHOUSE_ID` are set, read `gold.ext_fact_signal`
  (+ `ext_dim_source`/`ext_dim_hazard_type`/`ext_dim_region`) via `FabricDeltaClient`
  and map rows → `BoardSignal[]`, merged into the `occupancy` + `crisis` payloads'
  `signals`. Unset env ⇒ current fixtures (no behaviour change).
- TDD: unit tests for the row→`BoardSignal` mapping (trustClass, provenance from
  `activeBinding`, webCitations, canton/hazard) and the env-gated fixture fallback.
- Keep the app-side parity guard green (fixtures remain the default).

### Slice 2 — EH → Fabric (Eventstream → Lakehouse) + gold projection

- Create a Fabric **Eventstream** (`es-ihzhhpf-events`) sourcing
  `evh-ihzhhpf-sit-y26y/events`, filtered to external-signal envelopes, landing into
  a Lakehouse bronze Delta table in `lh_ihzhhpf_sit` (use the `eventstream-authoring`
  skill; needs a Fabric Event Hub connection). Gate the apply with `approved-to-apply`.
- Repoint `ingest_bronze_signals.py` (or add a thin reader) from `signals_synth` to
  the Eventstream-landed bronze table; run silver + gold to populate
  `gold.ext_fact_signal`.

### Slice 3 — Verify end-to-end

- With the tenant setting enabled + golden surface pointed at gold, switch the app to
  Live mode and confirm the Web IQ (+ other) signals render with `provenance: live`
  and their web citations, sourced from the Event-Hub-fed gold — captured as evidence.

## Verification

- Slice 1: `apps/hcc-agent-host` unit + integration golden tests green; app vitest
  parity guard green.
- Slice 2: Eventstream shows flowing events; `gold.ext_fact_signal` row count > 0 from
  live envelopes; `az`/Fabric evidence captured.
- Slice 3: app Live-mode screenshot + `provenance: live` on the signal panel.

## Out of scope / follow-up

- PROD cut-over of the live golden surface (SIT demo first).
- Real-time (Eventhouse KQL) path — deferred in favour of the Lakehouse path (P1).
