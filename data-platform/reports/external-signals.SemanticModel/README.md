# external-signals.SemanticModel

Direct Lake semantic model for the **Trusted External Signals** data product
(Sprint 21 M5). It exposes `gold.ext_*` signal, trigger audit, source, hazard,
and region tables so operators can surface authoritative Swiss hazard signals
for advisory CSA pre-seeding.

This is a **separate** semantic model, following the ADR-0026 precedent used by
[`evidence.SemanticModel`](../evidence.SemanticModel/README.md). It is
intentionally not folded into `capacity-dashboard.SemanticModel`, and is
therefore deliberately outside the `capacity-dashboard` exact-count verify gate
in `.github/workflows/verify-semantic-model.yml`.

## Tables (Direct Lake over `lh_ihzhhpf_sit`)

| Table | Gold source | Grain |
| --- | --- | --- |
| `ext_fact_signal` | `gold.ext_fact_signal` | one row per active normalized signal (`ext_signal_id`, source, hazard, severity, Lage tier, canton membership, onset, status) |
| `ext_fact_trigger_event` | `gold.ext_fact_trigger_event` | one row per signal-triage evaluation/fire/quarantine audit event, including CSA `runId` when fired |
| `ext_dim_source` | `gold.ext_dim_source` | one row per trusted source (`ext_source_id`, authority, trust tier) |
| `ext_dim_hazard_type` | `gold.ext_dim_hazard_type` | one row per hazard type (`ext_hazard_type`, scenario template, default Lage tier) |
| `ext_dim_region` | `gold.ext_dim_region` | one row per affected Swiss canton (`ext_canton`) |

Gold signal and dimension rows are projected by
[`build_gold_signals.py`](../../notebooks/external-signals/build_gold_signals.py)
from the DC-EXT-SIGNAL-v1 Silver records.

`ext_fact_signal.ext_cantons` preserves the Gold fact's canton-membership field;
`ext_dim_region.ext_canton` provides the dimension list for canton browsing.

## Relationships

| From | To |
| --- | --- |
| `ext_fact_signal.ext_source_id` | `ext_dim_source.ext_source_id` |
| `ext_fact_signal.ext_hazard_type` | `ext_dim_hazard_type.ext_hazard_type` |
| `ext_fact_trigger_event.ext_hazard_type` | `ext_dim_hazard_type.ext_hazard_type` |

## Measures

| Measure | Meaning |
| --- | --- |
| `Active Signals` | Distinct active `Actual` signals in the current context. |
| `Signals by Severity` | Distinct signals in the current severity filter context. |
| `Highest Lage Tier` | Maximum `defaultLageTier` surfaced by the current signals. |
| `Triggers Fired (24h)` | `trigger-fired` audit rows with `ext_triggered_at` in the last 24 hours. |
| `Mean Time Source->Trigger` | Average minutes from `ext_source_onset` to `ext_triggered_at`. |
| `Signals Quarantined` | `quarantined-status` audit rows recorded because they must not escalate. |

## RLS

Trusted external signals are public-authority, synthetic/demo scoped, and non-PHI
per the Sprint 21 design. No row-level restriction is required; the model ships
one least-privilege read-only role, `SignalsReadOnly` (`modelPermission: read`,
no filter).

## CI scope

The repository semantic-model verifier currently triggers only for
`data-platform/reports/capacity-dashboard.SemanticModel/**` plus the verifier
script/workflow itself. This model is intentionally outside that gate; local
README checks are mojibake and markdownlint.

## Status

**Authored TMDL skeleton, publish-gated.** The TMDL here is the source of truth
for Fabric Git integration. Publishing to a Fabric workspace is a
`deploy`-ceiling action gated by `approved-to-apply` (AGENTS.md section 4).
