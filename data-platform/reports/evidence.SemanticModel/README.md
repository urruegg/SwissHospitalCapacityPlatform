# evidence.SemanticModel

Direct Lake semantic model for the **Showcase Evidence** data product
(Sprint 14.1 T4). Exposes readiness scoring so the presenter whiteboard / Backstage
Evidence tab can read `readiness score per BOM item × region × track`
(design spec [§3](../../../docs/superpowers/specs/2026-07-09-sprint-14-evidence-design.md)/§6).

Measure ownership — a **separate** model rather than folding into
`capacity-dashboard.SemanticModel` — is decided in
[ADR-0026](../../../docs/adr/0026-evidence-readiness-measure-ownership.md)
(Option B).

## Tables (Direct Lake over `lh_ihzhhpf_sit`)

| Table | Gold source | Grain |
| --- | --- | --- |
| `fact_readiness_snapshot` | `gold.fact_readiness_snapshot` | one row per `bomId × track` (`bomId`, `track`, `region`, `status`, `showcaseOnly`, `blockingReason`) |
| `fact_readiness_summary` | `gold.fact_readiness_summary` | one row per track + a GA-parity-gap row (`track`, `readyCount`, `total`, `readyPct`) |

Both Gold tables are written by
[`score_readiness.py`](../../notebooks/evidence/score_readiness.py), which applies
the pure T-SHOW / T-PROD rules in
[`readiness_rules.py`](../../notebooks/evidence/readiness_rules.py) (ADR-0021).

## Measures (design spec §6 · plan Task 4)

| Measure | Meaning |
| --- | --- |
| `BOM count` | Distinct BOM items in context. |
| `Readiness % (T-SHOW)` | % of BOM items `Ready` on the synthetic showcase track. |
| `Readiness % (T-PROD)` | % of BOM items `Ready` on the real-PHI GA-only track. |
| `GA-Parity Gap` | `#Ready(T-SHOW)` − `#Ready(T-PROD)` — the GA-parity gap. |
| `Blocked requirements count` | BOM items `Blocked` on the T-PROD track. |

DAX validation queries + expected values on the readiness golden fixture are in
[`evidence-measure-tests.md`](evidence-measure-tests.md).

## RLS

Showcase Evidence data is synthetic non-PHI (ADR-0016). No row-level restriction
is required; the model ships one read-only role `EvidenceReadOnly`
(`modelPermission: read`, no filter) for least-privilege access by the presenter
audience. Row-scoped RLS is deferred (ADR-0026 §RLS decision).

## Status

**Authored TMDL skeleton, publish-gated.** The TMDL here is the source of truth
for Fabric Git integration (S17 T1). Publish to `ws-ihzhhpf-sit-data` is a
`deploy`-ceiling action gated by `approved-to-apply` (AGENTS.md §4). Structure is
checked off-Fabric by
[`../tests/test_evidence_semantic_model.py`](../tests/test_evidence_semantic_model.py).
