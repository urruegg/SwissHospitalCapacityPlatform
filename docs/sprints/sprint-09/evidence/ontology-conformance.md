# Ontology Conformance CI — Sprint 09 v2.0.0 Evidence

| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Date | 2026-07-03 |
| Author | Urs Rüegg |
| Status | Reviewed |
| Previous Version | n/a |

## Purpose

Design spec §3.5 gate — every `hcp:*` reference in [`docs/ontology/crosswalk.md`](../../../ontology/crosswalk.md) must exist in [`docs/ontology/reference-layer.ttl`](../../../ontology/reference-layer.ttl) and be marked either **concrete** or **deferred** via the backtick convention.

## Result

**PASS — STRICT mode green on `sprint-09-v2/t1-foundation` (merge base for main)**

## Method

- **Workflow:** [`.github/workflows/ontology-conformance.yml`](../../../../.github/workflows/ontology-conformance.yml) — runs on every PR touching `docs/ontology/**`
- **Script:** [`scripts/ontology/check_crosswalk_conformance.py`](../../../../scripts/ontology/check_crosswalk_conformance.py)
- **Modes:**
  - Non-strict — every `hcp:*` reference must resolve
  - **STRICT** — additionally, every reference must be marked concrete (`` ` `` prefix) or explicitly deferred; contracts (`FR-*`, `NFR-*`) referenced in the crosswalk must exist in [`docs/PRD.md`](../../../PRD.md)
- **Trigger:** every push and every PR modifying `docs/ontology/**` or the check script itself

## Latest run (successful)

| Run | Branch | SHA | Conclusion | Date | URL |
| --- | ------ | --- | ---------- | ---- | --- |
| 28642572095 | `sprint-09-v2/t1-foundation` | `068d315` | **success** | 2026-07-03 06:22 UTC | [Actions run](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/28642572095) |
| 28609627041 | `refresh/sprint-09-mvo-track` | `68df341` | success | 2026-07-02 17:35 UTC | [Actions run](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/28609627041) |
| 28607286119 | `refresh/sprint-09-dc-or-contracts` | `15edae6` | success | 2026-07-02 16:55 UTC | [Actions run](https://github.com/urruegg/SwissHospitalCapacityPlatform/actions/runs/28607286119) |

## Governance

- STRICT mode is a **blocking merge check** for any PR touching `docs/ontology/**`
- New ontology entities added to `reference-layer.ttl` require the crosswalk entry marked either concrete `` ` `` or explicitly deferred with rationale
- FR/NFR references in the crosswalk are cross-checked against `docs/PRD.md` §7 traceability matrix

## Reproducibility

```powershell
python scripts/ontology/check_crosswalk_conformance.py --strict
```

Expected exit 0.

## References

- Design spec §3 ontology extension + §3.5 CI gate — [`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../../../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md)
- Reference-layer TTL v0.2.0 — [`docs/ontology/reference-layer.ttl`](../../../ontology/reference-layer.ttl)
- Crosswalk v0.2.1 — [`docs/ontology/crosswalk.md`](../../../ontology/crosswalk.md)
