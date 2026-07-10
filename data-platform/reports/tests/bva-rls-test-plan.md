# BVA RLS test plan (Sprint 15 · T6)

Verifies the two BVA row-level-security roles on the `capacity-dashboard`
semantic model before the gated publish (AGENTS.md §4). BVA Gold is synthetic,
non-PHI Azure-consumption + value data, so the predicates scope **hospital
attribution** rather than PHI.

## Roles under test

| Role | Predicate | Assigned to |
| --- | --- | --- |
| `BvaExecFull` | none (all hospitals) | `HCC.ExecBoard` (SIT + PROD) |
| `BvaBoardReadOnly` | `bva_dim_hospital[hospital_key] = "Aggregated"` | `HCC.GuestReadOnly` (SIT + PROD) |

## Test matrix

| # | Identity / role | Expected `bva_dim_hospital` rows | Expected pages | Result |
| --- | --- | --- | --- | --- |
| 1 | `BvaExecFull` | USZ, LUKS, Zollikerberg, Aggregated | all 6 | ☐ |
| 2 | `BvaBoardReadOnly` | Aggregated only | Board summary only | ☐ |
| 3 | `BvaBoardReadOnly` on a CEO card | measures compute over Aggregated only; no per-hospital drill | — | ☐ |
| 4 | No BVA role (operational-only user) | no BVA tables visible | — | ☐ |

## Verification steps

1. **Model validation** — after publish, in Fabric → semantic model → *Security*,
   confirm both roles exist with the predicates above.
2. **View as role** — use *View as* → `BvaBoardReadOnly` and confirm a
   `bva_fact_*` visual returns only `Aggregated`-attributed totals.
3. **View as** → `BvaExecFull` and confirm all four hospital keys are visible.
4. **Report binding** — open the boardroom report as each role and confirm the
   page-visibility expectations in the matrix.
5. **Evidence** — capture screenshots into the PR thread; tick the matrix.

## Automated pre-check (CI)

The report/model structure (page count, every card's measure exists in
`bva_measures`, both roles present) is asserted before publish by:

```bash
python3 -m unittest discover -s data-platform/reports/tests -v
```

This is a structural gate only — the actual RLS row filtering is verified
manually in Fabric per the matrix above (DAX/RLS cannot be evaluated in the
sandbox).
