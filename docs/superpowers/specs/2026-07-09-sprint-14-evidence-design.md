# Sprint 14 — Showcase Evidence Data Product (presenter whiteboard) — Design Spec

| Field | Value |
| ----- | ----- |
| **Version** | 1.2.0 |
| **Date** | 2026-07-10 |
| **Author** | Urs Rüegg |
| **Status** | In execution (T1–T6 landed; Fabric/SIT deploy gated) |
| **Previous Version** | 1.1.0 (Sprint 14.1 mini-sprint: T4 evidence.SemanticModel, T5/T6 Evidence tab + provenance contract landed) |
| **Roadmap** | [2026-07-09-sprints-11-16-roadmap-design.md](2026-07-09-sprints-11-16-roadmap-design.md) |
| **Anchor idea** | [docs/superpowers/ideas/SwissHospitalPlatformShowcaseEvidence.md](../ideas/SwissHospitalPlatformShowcaseEvidence.md) |

---

## Table of Contents

1. [Goal and desired end state](#1-goal-and-desired-end-state)
2. [Scope](#2-scope)
3. [Architecture and data flow](#3-architecture-and-data-flow)
4. [Presenter whiteboard vs. operational whiteboard](#4-presenter-whiteboard-vs-operational-whiteboard)
5. [Card catalog](#5-card-catalog)
6. [Readiness scoring rules](#6-readiness-scoring-rules)
7. [Agent and skill mix](#7-agent-and-skill-mix)
8. [GitHub delegation](#8-github-delegation)
9. [Side-effect posture and approval gates](#9-side-effect-posture-and-approval-gates)
10. [Verification strategy](#10-verification-strategy)
11. [Risks and mitigations](#11-risks-and-mitigations)
12. [Dependencies](#12-dependencies)
13. [Definition of done](#13-definition-of-done)

---

## 1. Goal and desired end state

The showcase-evidence data product is live end-to-end:

- `data/evidence/*.json` is auto-published from repo changes (PRD, ADR, infra, BOM, region-availability);
- ingested into the Fabric medallion (Bronze → Silver → Gold star schema per [showcase-evidence idea §5](../ideas/SwissHospitalPlatformShowcaseEvidence.md#5-extended-data-model-star-schema));
- scored for readiness per T-SHOW / T-PROD × region;
- rendered as an **infinite presenter whiteboard** where each artefact (BOM, ADR, PRD requirement, GA-evidence card) is a draggable, drill-in card;
- lives in the Sprint 13 app's Backstage → new "Evidence" tab.

---

## 2. Scope

### 2.1 In-scope MVP

- Evidence-publish workflow `.github/workflows/evidence-publish.yml` — on push to `main` (paths: `docs/PRD.md`, `docs/adr/**`, `infra/**`, `docs/bom.yaml`, `docs/region-availability.yaml`), parse to `data/evidence/*.json` and commit to an `evidence-latest` branch (or upload to OneLake shortcut).
- Fabric pipeline: Bronze (raw JSON) → Silver (typed tables) → Gold (star schema).
- Readiness scoring rules per [§5.3](../ideas/SwissHospitalPlatformShowcaseEvidence.md#53-readiness-scoring-logic) — T-SHOW / T-PROD × region.
- Seed BOM catalog — 25 items from [§6](../ideas/SwissHospitalPlatformShowcaseEvidence.md#6-bom-seed-catalog-starter--to-be-maintained-in-bomyaml).
- Seed ADR mappings — 10 rows from [§8.1](../ideas/SwissHospitalPlatformShowcaseEvidence.md#81-adr--requirement--readiness-map-seed).
- **Presenter whiteboard component** — infinite canvas (base chosen in the Sprint 13 decision ADR), 5 card types.
- MVP scope on the whiteboard: BOM + ADR + one PRD requirement card visible for Switzerland North × T-SHOW.

### 2.2 Out-of-scope / deferred

- Automated GA-status verification (curated list only in S14; auto-check via Azure Resource Graph is a follow-up — see roadmap Q-3).
- Multi-region readiness view (only CH North + one EU fallback in MVP).
- Time-series readiness trends (Sprint 15 dependency).
- Whiteboard save/share layouts (in-memory only in MVP).

---

## 3. Architecture and data flow

```text
[repo edits] ─push→ evidence-publish.yml ─→ data/evidence/*.json
                                                    │
                                    OneLake shortcut / commit
                                                    ▼
                            Fabric Medallion (Bronze → Silver → Gold)
                                                    │
                            Readiness scoring rules (Silver → Gold)
                                                    ▼
                            Direct Lake semantic model + RLS
                                                    ▼
                    Presenter Whiteboard (React component in Backstage)
                        ├─ BOM cards (drag / group / drill)
                        ├─ ADR cards
                        ├─ PRD requirement cards
                        ├─ GA-evidence cards
                        └─ Dependency edges
```

**Parser inputs.**

| Source | Parser output | Refresh |
| --- | --- | --- |
| `docs/PRD.md` | `requirements.json` (one row per `FR-*` / `NFR-*`; family, MVP flag, source commit) | On-commit |
| `docs/adr/**` | `adrs.json` + `req_adr_map.json` | On-commit |
| `docs/bom.yaml` (new) | `bom.json` + `dependencies.json` | On-commit |
| `docs/region-availability.yaml` (new) | `region_availability.json` | On-commit |
| `infra/**` (deployed actuals via ARG optional) | `deployed_bom.json` | Daily (follow-up) |

**Silver typing.**

- Every fact carries `sourceUrl`, `asOf`, `verifiedBy` for provenance.
- Every dimension carries `sourcePath`, `sourceCommit`.

**Gold star schema** — see anchor idea §5.1 (`Dim_Resource`, `Dim_Region`, `Dim_Track`, `Dim_MaturityStatus`, `Dim_Requirement`, `Dim_ADR`, `Dim_Environment`, `Dim_Date`) and §5.2 (`Fact_AvailabilityEvidence`, `Fact_BOMDeployment`, `Fact_ReadinessSnapshot`, `Bridge_Resource_Dependency`, `Bridge_Requirement_Resource`, `Bridge_Requirement_ADR`).

---

## 4. Presenter whiteboard vs. operational whiteboard

| Aspect | Sprint 13 operational | Sprint 14 presenter |
| --- | --- | --- |
| Audience | Bed Manager, ED Lead, etc. | Presenter, Platform Admin, Ontology Steward, Auditor, Guest |
| Data source | Fabric Gold operational tables | Fabric Gold evidence tables |
| Card types | Power BI tile, Agent, KPI, Live-stream, Responsible, Scenario | BOM, ADR, PRD requirement, GA-evidence, Dependency edge |
| Layout persistence | Per user + role + hospital (S13 in-memory; follow-up persistent) | Per presenter (shared "demo layouts") |
| Reuses code from | — | Sprint 13's whiteboard framework (same infinite-canvas base and card registry, distinct card catalog) |

**Reuse contract.** The whiteboard framework in `apps/hcc-app-fluent/src/whiteboard/` is agnostic of card catalog. Sprint 14 adds a new card registry entry per card type; the framework itself is not forked.

---

## 5. Card catalog

| Card type | Content | Drill-in | Provenance shown |
| --- | --- | --- | --- |
| **BOM item** | Resource name, type, category, SKU, region availability chip, dependency count | Panel with dependencies + realising requirements + governing ADRs | `sourcePath` + `bom.yaml` commit |
| **ADR** | ADR id, title, status, one-line decision | Full decision text + governed requirements + affected BOM items | ADR file + commit |
| **PRD requirement** | Requirement id, family, title, MVP flag, readiness chips per track/region | Governing ADR(s) + realising BOM item(s) + readiness score | PRD file + commit |
| **GA-evidence** | Resource × region chip (GA / Preview / Not available) + as-of date | Evidence source URL + verifier + history | Curated YAML + verifier |
| **Dependency edge** | Directed edge with type (`requires` / `hosts` / `grounds` / `binds` / `governs`) | Both endpoint cards side-by-side | Derived from `bom.yaml` |

---

## 6. Readiness scoring rules

Implemented in Silver → Gold transform. Recomputed on every ingest.

**T-SHOW (synthetic data).** `Ready` if the resource is available in the chosen showcase region (CH North, else EU fallback) at any maturity (GA or Preview) and all its dependencies are likewise available. Flagged `Showcase-only` when it relies on a Preview feature or a global model — allowed because ADR-0006 (preview = non-production) is scoped to regulated data, and T-SHOW uses synthetic non-PHI data.

**T-PROD (real PHI).** `Ready` only if the resource is GA in Switzerland North (or an approved region), all dependencies are GA, the deployment type is residency-compliant (regional/Swiss-resident for PHI per ADR-0003/0004), and no Preview feature sits on the critical path (ADR-0006). Otherwise `Blocked` with a `blockingReason` (e.g., "Fabric IQ Ontology Preview — ADR-0002", "frontier model global-only — ADR-0003").

**Aggregate.** % of requirements Ready per track per region → headline readiness gauge; delta between T-SHOW-ready and T-PROD-ready = GA-parity gap.

---

## 7. Agent and skill mix

| Component | Superpowers skills | Domain skills |
| --- | --- | --- |
| Evidence-publish workflow | `writing-plans`, `test-driven-development`, `verification-before-completion` | (none) |
| Fabric medallion pipeline | Same + `subagent-driven-development` | `e2e-medallion-architecture`, `spark-authoring` |
| Semantic model + Direct Lake | Same | `fabric-semantic-model-authoring`, `powerbi-optimization` |
| Presenter whiteboard component | Same | (from Sprint 13 decision stack) |
| Readiness scoring rules | Same | `spark-authoring` |

---

## 8. GitHub delegation

| Asset | Path | Trigger |
| --- | --- | --- |
| Workflow — evidence publish | `.github/workflows/evidence-publish.yml` | Push to `main` on parsed paths |
| Issue template — BOM item | `.github/ISSUE_TEMPLATE/bom-item.yml` | New/updated BOM item |
| Issue template — GA-evidence refresh | `.github/ISSUE_TEMPLATE/ga-evidence-refresh.yml` | Availability-fact refresh cycle |
| Labels | `sprint-14`, `evidence`, `bom`, `ga-refresh`, `readiness-rules` | Applied by templates |
| CODEOWNERS | `.github/CODEOWNERS` | `docs/bom.yaml`, `docs/region-availability.yaml`, `data/evidence/**` → @urruegg |

---

## 9. Side-effect posture and approval gates

| Action | Ceiling | Gate |
| --- | --- | --- |
| `data/evidence/*.json` publish | `write` | Automated (workflow has write only to the `evidence-latest` branch) |
| Fabric pipeline changes | `deploy` | `approved-to-apply` |
| Semantic model publish | `deploy` | `approved-to-apply` |
| Presenter whiteboard component (app source) | `write` | Standard PR review |
| Readiness scoring rules changes | `write` | Standard PR review + explicit `readiness-rules` label |

---

## 10. Verification strategy

- **Parser unit tests** — PRD parser handles every requirement family (FR-OM, FR-DATA, …, NFR-*); ADR parser handles Accepted / Superseded / Proposed statuses; BOM parser validates against JSON schema.
- **Integration test** — seed evidence dataset → Fabric pipeline → semantic model → one measure returns expected value.
- **Readiness rule regression** — golden fixtures: for a fixed input BOM + region-availability, the scored output is byte-stable.
- **E2E** — presenter opens the Evidence tab in Backstage, sees at least 25 BOM cards + 10 ADR cards + dependency edges; drill-in on one BOM card shows realising requirement(s) + governing ADR(s).
- **Provenance check** — every card exposes `sourceUrl` / `sourcePath` + `asOf`; missing values fail the card render.

---

## 11. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Parser breaks on PRD format changes | Golden-input fixtures under `tests/evidence/fixtures/`; CI diffs on parser output |
| GA-evidence curation drift (facts go stale) | Weekly refresh issue template (`ga-evidence-refresh.yml`); `verifiedBy` + `asOf` required on every fact; freshness KPI |
| Whiteboard performance with > 100 cards | Virtualise off-viewport cards; lazy-load dependency edges |
| Sprint 13 decision ADR delays whiteboard-base choice | Fallback: land pipeline + data model first; ship whiteboard in a follow-up mini-sprint |
| Readiness rules encode outdated ADR references | Rule change requires `readiness-rules` label + ADR reference validated in CI |
| Committing evidence JSON to `main` bloats history | Publish to `evidence-latest` branch OR OneLake shortcut only; never squash-merge evidence into `main` |

---

## 12. Dependencies

**In**: Sprint 13 (whiteboard component + Backstage tab pattern), all prior sprints (source of PRD/ADR/BOM/infra).

**Out**: Sprint 15 (BVA cards live on this whiteboard as a filter tab).

---

## 13. Definition of done

Status legend: `[x]` landed in this sprint's PR · `[~]` partial / authored-as-code but publish-gated · `[ ]` deferred to follow-up (see §11 fallback).

- [x] `evidence-publish.yml` runs on push and produces `data/evidence/*.json` on `evidence-latest` branch (or OneLake).
- [~] Fabric medallion pipeline populated end-to-end from at least one publish cycle. *(notebooks authored + readiness golden green; Fabric publish is `deploy`-gated by `approved-to-apply`.)*
- [x] Semantic model returns `readiness score per BOM item × region × track` for Switzerland North × T-SHOW. *(T4 — Sprint 14.1: `data-platform/reports/evidence.SemanticModel/`, [ADR-0026](../../adr/0026-evidence-readiness-measure-ownership.md); Fabric deploy still gated on S17 T1 Git integration.)*
- [x] Backstage → Evidence tab renders the presenter whiteboard with ≥ 25 BOM cards + ≥ 10 ADR cards + 1 PRD-requirement card and their dependency edges. *(T5/T6 — Sprint 14.1: `apps/hcc-app-fluent/src/workspaces/backstage/tabs/evidence/`; SIT re-deploy gated on S13.1.)*
- [x] Provenance visible on every card (`sourceUrl`, `asOf`). *(T5 card contract — Sprint 14.1: `apps/hcc-app-fluent/src/cards/evidence/_provenance.tsx`, missing provenance fails render.)*
- [x] Golden readiness-rule test green.
- [x] Sprint 14 retro entry in [docs/sprints/superpowers-checkpoint-matrix.md](../../sprints/superpowers-checkpoint-matrix.md).
