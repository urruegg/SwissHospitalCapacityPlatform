# Foresight tier in Fabric — evidence (Sprint 26 WS-A)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rüegg |
| **Status** | Draft |
| **Previous Version** | — (new document) |
| **Related** | [WS-A Foresight plan](../superpowers/plans/2026-07-23-sprint-26-ws-a-foresight-plan.md), [Decision-ontology design](../superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md), [Signals Fabric evidence](signals-fabric-evidence.md), [ADR-0034](../adr/0034-fabric-iq-demo-scope-artefacts.md), [PR #346](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/346), [issue #335](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/335) |

## Purpose

This document proves that the **Sprint 26 WS-A Foresight tier** is not merely
scaffolded but is **live and queryable** in the SIT Fabric lakehouse across the
three Gold Delta tables the predictive tier produces:

1. `gold.fact_occupancy_forecast` — the 72h occupancy forecast per ward × horizon.
2. `gold.fact_forecast_driver` — the driver decomposition (the "why").
3. `gold.fact_signal` — the deny-by-default Trust-A signal projection over the
   Sprint 21 external-signal spine.

Scope is demo-only and bounded by [ADR-0034](../adr/0034-fabric-iq-demo-scope-artefacts.md):
**synthetic, deterministic** data (no model, no LLM-guessed numbers), **no PHI**,
`westus2` per [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md), read-only
downstream, live changes approval-gated by [AGENTS.md §4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete).

## Environment

| Item | Value |
| ---- | ----- |
| Fabric workspace | `ws-ihzhhpf-sit-data` — `f3af9733-9503-4e92-98f9-a901d96f1c87` (`westus2`) |
| Lakehouse | `lh_ihzhhpf_sit` — `30594c20-46ba-40ea-91fa-4701b105e0b9` |
| Evidence notebook | `run_foresight_evidence` — `50159429-bc58-4c3e-82ff-89871a2fbc1d` |
| SQL analytics endpoint | `pimdoe2bjsuu3d6komn3u6sdfe-gol274ydswje5ghzvea5s3y4q4.datawarehouse.fabric.microsoft.com` / `lh_ihzhhpf_sit` |
| Tenant / subscription | `1337187a-4c41-4da9-8fca-731bba7a4329` (`MngEnvMCAP164444`) / `66a9953a-df37-4c51-856c-9971b9bf3e03` |

## 0. Baseline (motivation)

At the start of this evidence run (2026-07-23), an OneLake DFS listing of the SIT
lakehouse `gold` schema showed the external-signal spine (`ext_*`) and the prior
descriptive Gold tables present, but **none of the three WS-A Foresight tables**
(`fact_occupancy_forecast`, `fact_forecast_driver`, `fact_signal`) — the Foresight
tier existed only as offline-validated notebook code
([PR #346](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/346)),
never materialised. This document records closing that gap.

## 1. Data (gold) proof

`verify_forecast_gold.py --environment SIT` (Fabric SQL analytics endpoint over
the lakehouse) — captured 2026-07-23:

```text
--- WS-A gold row counts ---
  gold.fact_occupancy_forecast: 73 rows
  gold.fact_forecast_driver: 292 rows
  gold.fact_signal: 4 rows

--- distinct fact_signal trust_tier values ---
  'A'

--- distinct driver factors: 4 ---

[OK] All 3 WS-A gold tables populated; driver decomposition 4x forecast; signal projection Trust-A only.
```

The counts match the deterministic offline computation exactly: one forecast row
per ward × horizon-hour (1 ward × 73 hours `0..72` = **73**), four driver factors
per forecast point (**292** = 73 × 4), and **4** Trust-A signals.

### 1a. Forecast + breach

The synthetic `Medicine A` ward (capacity 50) breaches at every horizon and the
occupancy climbs as admissions outpace discharges — captured 2026-07-23:

```text
wardId       horizonH  forecastOccupiedBeds  forecastOccupancyPct  breach
Medicine A   0         51                    102                   True
Medicine A   72        55                    110                   True
```

### 1b. Driver decomposition reconciles

The h72 driver deltas sum to the net forecast change
(`55 − 51 = +4` beds), proving the "why" reconciles to the "what" — captured
2026-07-23:

```text
factor               delta  note
forecast_admissions  6      forecast admissions
planned_discharges   -2     planned discharges
seasonality          0      flu season
transfers            0      net transfers
```

`+6 − 2 + 0 + 0 = +4`, exactly the `51 → 55` bed change. This reconciliation is a
unit-tested invariant (`tests/test_forecast_pure.py::test_driver_deltas_reconcile_to_net_forecast_change`)
and now holds live in Fabric.

### 1c. Signal projection is deny-by-default Trust-A

`gold.fact_signal` carries only Trust-A signals, each with a deterministic
severity-derived probability, evidencing the `seasonality` driver — captured
2026-07-23:

```text
source_id    hazard_type  severity  trust_tier  probability  evidences_factor
alertswiss   heat         Severe    A           0.9          seasonality
bag          rsv          Moderate  A           0.6          seasonality
meteoswiss   heat         Severe    A           0.9          seasonality
sed          earthquake   Severe    A           0.9          seasonality
```

No non-Trust-A signal leaked into the projection (`trust_tier` distinct set is
`{'A'}`), confirming the deny-by-default gate end to end.

## 2. Ontology proof

The Foresight concepts are first-class in
[`docs/ontology/reference-layer.ttl`](../ontology/reference-layer.ttl):
`hcp:Ward`, `hcp:Forecast`, `hcp:Driver`, with object properties `hcp:forWard`,
`hcp:explainedBy`, `hcp:evidencedBy` (the driver → `hcp:ExternalSignal` link that
grounds the `evidences_factor = seasonality` column above). The two-layer
crosswalk conformance gate passes STRICT (0 WARN, 0 FAIL) with the three WS-A
tables bound to `DC-OCCUPANCY-FORECAST-v1` / `DC-FORECAST-DRIVER-v1` and the
reused `DC-EXT-SIGNAL-v1`.

## 3. Reproduce

```powershell
# 0. Auth (MngEnvMCAP164444 tenant)
az login  # admin@mngenvmcap164444.onmicrosoft.com

# 1. Regenerate the self-contained evidence notebook (deterministic; Python 3.14)
python data-platform\scripts\fabric\build_forecast_evidence_notebook.py

# 2. Create + run it in SIT (deploy-gated: needs approved-to-apply)
python data-platform\scripts\fabric\run_single_notebook.py `
    --environment SIT `
    --notebook data-platform\notebooks\foresight\run_foresight_evidence.ipynb `
    --display-name run_foresight_evidence --apply

# 3. Verify the three gold tables (SQL endpoint sync lags a run by ~150 s)
python data-platform\scripts\fabric\verify_forecast_gold.py --environment SIT
```

## 4. Gate record (AGENTS.md §4)

| Action | Target | Approver | Timestamp | Result id |
| ------ | ------ | -------- | --------- | --------- |
| Create + run evidence notebook | SIT lakehouse gold `fact_occupancy_forecast` / `fact_forecast_driver` / `fact_signal` | @urruegg (`approved-to-apply`) | 2026-07-23 | notebook `50159429-bc58-4c3e-82ff-89871a2fbc1d` run Completed |

## 5. Residual risks

- **Data honesty** — the synthetic seed is a single ward (`Medicine A`) with a
  fixed admission/discharge ramp; `transfers` and `seasonality` deltas are 0, so
  those driver rows are present-but-zero. Multi-ward demo depth is a later slice.
- **SQL endpoint latency** — the Fabric SQL-analytics endpoint metadata syncs a
  few minutes after a notebook run; the first `verify_forecast_gold.py` read
  immediately after the run returned 0 rows and passed after ~150 s. The OneLake
  DFS listing confirmed the Delta tables physically existed straight away.
- **No semantic model yet** — WS-A binds the ontology + Gold tables only; the
  Direct-Lake semantic model + measures and the `verify-semantic-model.yml`
  rebaseline are deferred to WS-A2. `gold.fact_signal.cantons` remains a native
  array (no Direct-Lake array-to-string collapse needed until a model consumes it).
- **PROD** — this evidence is **SIT-only**. Applying the same treatment to the
  PROD workspace (Switzerland North) is a separate gated follow-up.
