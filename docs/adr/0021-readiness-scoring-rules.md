# ADR-0021 — Showcase Evidence readiness scoring rules (T-SHOW / T-PROD)

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-09 |
| **Deciders** | @urruegg |
| **Superseded by** | — |
| **Related** | [ADR-0001](0001-ga-only-mvp-critical-path.md) (GA-only critical path), [ADR-0003](0003-swiss-regional-inference-for-phi.md) / [ADR-0004](0004-block-global-and-data-zone-for-phi.md) (Swiss residency for PHI), [ADR-0006](0006-preview-features-non-production-rule.md) (preview = non-production for regulated data), [ADR-0013](0013-temporary-us-region-demo-scope.md) (demo scope), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) (no PHI in demo) |
| **Realises** | Sprint 14 design spec [§6 Readiness scoring rules](../superpowers/specs/2026-07-09-sprint-14-evidence-design.md) |

## Context

The Showcase Evidence data product scores every Bill-of-Materials (BOM) item for
**readiness** on two delivery tracks so the presenter whiteboard can show a
headline gauge and a GA-parity gap:

- **T-SHOW** — the synthetic, non-PHI demo (currently `westus2` per ADR-0013,
  targeting Swiss regions when GA).
- **T-PROD** — the regulated, real-PHI production posture bound to Switzerland
  North residency.

The rules must be deterministic and byte-stable so a golden regression fixture
can protect them (design spec §10), and they must reference the governing ADRs
so a rule drift is auditable (design spec §11 — `readiness-rules` label + ADR
reference validated in review).

## Decision

Readiness is computed in the Silver → Gold transform and recomputed on every
ingest. The canonical implementation is the pure module
[`data-platform/notebooks/evidence/readiness_rules.py`](../../data-platform/notebooks/evidence/readiness_rules.py);
the Fabric `score_readiness` notebook applies it to Silver Delta rows.

Regions: showcase region = **Switzerland North**, with **West Europe** as the EU
fallback; production region = **Switzerland North**.

### T-SHOW (synthetic data)

A resource is **Ready** when:

1. it is available (`GA` **or** `Preview`) in the showcase region, else in the EU
   fallback region; **and**
2. every one of its dependencies is likewise available.

It is additionally flagged **`showcaseOnly`** when the resource itself, or any of
its dependencies, is `Preview`-only. This is permitted because ADR-0006 (preview
= non-production) is scoped to *regulated* data, and T-SHOW uses synthetic,
non-PHI data (ADR-0016). Otherwise the resource is **Blocked**.

### T-PROD (real PHI)

A resource is **Ready** only when:

1. it is `GA` in Switzerland North (per ADR-0001); **and**
2. every dependency is `GA` in Switzerland North; **and**
3. no `Preview` feature sits on its critical path (ADR-0006); residency is
   Swiss-resident for PHI (ADR-0003 / ADR-0004).

Otherwise it is **Blocked** with a human-readable `blockingReason` naming the
offending resource and its maturity (e.g. `bom-iq-ontology is Preview (not GA) in
Switzerland North`).

### Aggregate

`% Ready` per track = ready count ÷ total BOM items. The **GA-parity gap** is the
difference between T-SHOW-ready and T-PROD-ready counts.

## Consequences

- Rules are unit-testable off-cluster and protected by a byte-stable golden
  regression fixture in
  [`data-platform/notebooks/evidence/tests/fixtures/readiness_golden/`](../../data-platform/notebooks/evidence/tests/).
- Any change to these rules requires the `readiness-rules` label and an update to
  this ADR (design spec §9 / §11).
- Automated GA-status verification (Azure Resource Graph) remains out of scope for
  Sprint 14; availability facts are curated in `docs/region-availability.yaml`
  with `verifiedBy` + `asOf` provenance.
