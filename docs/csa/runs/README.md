# CSA recommendation runs

Sprint 16 T9 — merged recommendation outputs of the `csa-agent`
Prepare → Run → Evaluate → Recommend flow. One file per run, named
`YYYY-MM-DD-<scenarioId>.md`.

> **Synthetic model derivation.** The KPI and tier figures in these MVP run docs
> are computed deterministically by the pure `simulate()` function in
> [`data-platform/notebooks/csa/csa-simulate.py`](../../../data-platform/notebooks/csa/csa-simulate.py)
> over synthetic Gold-shaped baselines (ADR-0016 — no PHI). A live Fabric
> notebook run (behind `approved-to-apply`) writes the authoritative
> `DC-SIM-RESULT` and `simulation-runs` records; these docs reproduce the same
> classifier output so the recommendation trail is reviewable without live
> Azure connectivity.

A run doc **may** carry a `runIssue:` front-matter key; when present, on merge to
`main` [`csa-run-followup.yml`](../../../.github/workflows/csa-run-followup.yml)
closes that parent run-tracking issue. The synthetic MVP demo docs below omit it
(no live parent run issue), so the follow-up workflow no-ops for them.

## MVP runs (the three `mvpRequired` scenarios)

| Run doc | Scenario | Tier | Peak util | Shortfall |
| ------- | -------- | ---- | --------- | --------- |
| `2026-07-09-pediatric-virus-surge-rsv.md` | RSV surge | 2 — Besondere Lage | 1.13 | 5 beds |
| `2026-07-09-cyberattack-hospital-services.md` | Cyberattack | 3 — Ausserordentliche Lage | 1.29 | 4 ICU beds |
| `2026-07-09-summer-heatwave-demand-surge.md` | Heatwave | 2 — Besondere Lage | 1.02 | 6 beds |

Tier classification is version-pinned by
[ADR-0021](../../adr/0021-csa-tier-classifier-rules.md).
