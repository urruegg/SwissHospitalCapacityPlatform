# BVA boardroom report (Sprint 15 · T6)

Five C-suite pages (CEO / CFO / CIO / COO / CTO) plus a blended **Board summary**
landing page, bound to the BVA KPI measures on the `capacity-dashboard` semantic
model (`bva_measures` — see
[`../capacity-dashboard.SemanticModel/README-bva.md`](../capacity-dashboard.SemanticModel/README-bva.md)).

## Pages

| Page | Headline KPIs (design spec §6) |
| --- | --- |
| **Board summary** | Net value realized (3yr), ROI %, Actual TCO, Strategic adoption %, Benefit realization %, Cost-to-value |
| **CEO** | Net value realized (3yr) + Benefit realization %; ROI %, Strategic adoption % |
| **CFO** | Actual TCO vs budget variance %; Net annual benefit, Cost-to-value, Payback |
| **CIO** | Azure run-rate + Cost optimization realized; Cost avoidance %, Active users |
| **COO** | Avoidable bed-day index (synthetic); Manual touches saved, Decision cycles |
| **CTO** | Cost per copilot turn; Cost per decision cycle, Cost per capability, Inference efficiency |

Each card binds a real measure from `bva_measures` — no hard-coded values. The
COO proxies are explicitly synthetic until the operational Gold facts are joined
(ADR-0025).

## RLS

Two BVA roles gate the rows (design spec §8):

- **`BvaExecFull`** — C-suite/board members see every hospital.
- **`BvaBoardReadOnly`** — guests see only the `Aggregated` rollup (the Board
  summary landing), never a specific hospital's cost/value rows.

Verification steps and the persona matrix are in
[`../tests/bva-rls-test-plan.md`](../tests/bva-rls-test-plan.md).

## Publish (gated)

Publishing the report **and** assigning the RLS roles to
`HCC.ExecBoard` / `HCC.GuestReadOnly` is a `deploy`-ceiling action gated by
`approved-to-apply` (AGENTS.md §4). No autonomous publish is wired into CI; the
human operator publishes via Fabric deployment tooling after the plan is
approved on the PR.
