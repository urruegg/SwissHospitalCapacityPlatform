# Sprint 22 — Curavias Golden-Source Master Data + Reproducible Medallion (P1a)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-19 |
| **Author** | @urruegg |
| **Status** | Ready for execution |
| **Previous Version** | n/a (new document) |

> **Sprint theme.** Make git the single source of truth for the capacity master data and modernize the operational medallion notebooks to the schemas-enabled `gold.*` layout, so a fresh schemas-enabled lakehouse rebuilds byte-reproducibly in SIT and PROD. This is **Part 1a** of the Curavias shared-master-data design and **supersedes issue #253**.

---

## 1. Sprint goal

Establish `data/master-data/` as the canonical, CI-gated home for the operational capacity master data, load it identically into SIT and PROD, and rewrite the medallion notebook writes from path-based (`Tables/gold/reference/*`, `Files/gold/*`) to schema-qualified `saveAsTable('{bronze,silver,gold}.*')`, proving a reproducible rebuild that the `capacity-dashboard` Direct Lake model binds to without manual migration.

**Success shape:**

* The 9 capacity CSVs live under `data/master-data/capacity/`, guarded by a dependency-free validator and a `master-data.yml` CI gate.
* `upload_to_onelake.py` is environment-parameterized (`--workspace-id` / `--lakehouse-id` / `--source-root` / `--target`) — no hard-coded SIT GUIDs.
* The operational notebooks (`01_bronze`, `02_silver`, `03_gold_master_data`, `04_load_or_samples`, eventstream `03_gold_eventstream`) write managed `gold.*` tables.
* A gold-schema parity check asserts the produced gold table set covers the `capacity-dashboard` contract.
* Running the modernized notebooks against an empty schemas-enabled lakehouse produces an identical `gold.*` set in SIT and PROD; issue #253 is closed and the readiness-design Phase 2 is unblocked.

---

## 2. Source baseline

1. [Design Spec — Curavias shared master data + ontology](../superpowers/specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md) — §4.1–4.4 (golden source, validator, loader, medallion modernization)
2. [Implementation Plan — P1a](../superpowers/plans/2026-07-19-curavias-p1a-golden-source-reproducible-medallion.md) — 15 bite-sized TDD tasks
3. [Fabric IQ → Foundry Readiness Design](../superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md) — Phase 2 blocker this sprint resolves
4. [Issue #253](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/253) — original notebook-modernization backlog (superseded)
5. `data/entra/` — the git-tracked master-data + validator + CI pattern this sprint mirrors
6. `data-platform/scripts/fabric/README-fabric-cicd.md` — release-train runbook (extended with the P1a rebuild evidence)

---

## 3. Sprint scope

| # | Task | Deliverable | DoD |
|---|------|-------------|-----|
| T1 | Relocate capacity CSVs | 9 CSVs under `data/master-data/capacity/` + `README.md` + provenance pointer | Git-moved; README committed |
| T2 | Validator (tests-first) | `validate_master_data.py` + `tests/` (PK, FK, presence) | Tests fail then pass; real data valid |
| T3 | CI gate | `.github/workflows/master-data.yml` | Runs validator + unittests on `data/master-data/**` |
| T4 | Parameterize loader | `upload_to_onelake.py` (`--workspace-id/--lakehouse-id/--source-root/--target`) + arg test | Callers updated; test passes |
| T5 | Gold-schema parity check | `verify_gold_schema.py` + tests | Contract excludes `bva_*`; tests pass |
| T6 | Modernize bronze/silver/gold | `01/02/03_*_master_data.ipynb` -> `saveAsTable('*.*')` | Managed tables; header docs updated |
| T7 | Modernize OR + eventstream | `04_load_or_samples`, `03_gold_eventstream` -> `gold.*` + batch seed | Files-based OR read; documented seed |
| T8 | Reproducibility proof | Runbook P1a section + parity evidence (SIT + PROD) | Identical `gold.*` set; parity green |
| T9 | Governance | Close #253; readiness-design MINOR bump | Doc gates green; #253 closed |

---

## 4. Key decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Git is the single source of truth for master data | Reproducibility, review, and no cross-environment drift; mirrors the proven `data/entra/` pattern. |
| D2 | Canonical home = `data/master-data/capacity/` | Moves the CSVs out of a buried review folder into a first-class, CI-gated location. |
| D3 | Schema-qualified `saveAsTable('gold.*')`, drop path-based writes | The `capacity-dashboard` Direct Lake model binds to `[gold].[*]`; a schemas-enabled managed layout is the only reproducible target. |
| D4 | Parameterize the uploader instead of per-env copies | One code path loads SIT and PROD identically; removes the hard-coded SIT GUIDs (an original #253 item). |
| D5 | Prove parity on an empty SIT clone AND empty PROD lakehouse | Reproducibility is only demonstrated when a fresh workspace yields the identical contract in both environments. |

---

## 5. Definition of Done

* [ ] T1–T9 committed on a `sprint22/*` implementation branch
* [ ] Golden-source CSVs under `data/master-data/capacity/`; validator + `master-data.yml` gate green
* [ ] `upload_to_onelake.py` parameterized with a passing arg unit test; all callers updated
* [ ] Operational notebooks write managed `bronze.*` / `silver.*` / `gold.*` tables
* [ ] `verify_gold_schema.py` parity check passes against the `capacity-dashboard` contract in SIT and PROD
* [ ] Reproducibility evidence (table counts + parity output, SIT + PROD) recorded in the fabric-cicd runbook
* [ ] Issue #253 closed with a pointer to this sprint's spec + plan; readiness design bumped
* [ ] Live Fabric applies gated by `approved-to-apply`; PR merges human-performed
* [ ] All CI checks pass (markdown lint + mojibake on docs; validator + unit tests on code)

---

## 6. References

* Design: [`2026-07-19-curavias-shared-master-data-and-ontology-design.md`](../superpowers/specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md)
* Plan: [`2026-07-19-curavias-p1a-golden-source-reproducible-medallion.md`](../superpowers/plans/2026-07-19-curavias-p1a-golden-source-reproducible-medallion.md)
* Readiness design: [`2026-07-17-fabric-iq-foundry-readiness-design.md`](../superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md)
* Successor sprint: [Sprint 23 — Unified org spine + skills ontology (P1b)](sprint-23-curavias-org-spine-and-skills-ontology.md)
* Issue: [#254 — Sprint 22: Curavias golden-source master data + reproducible medallion (P1a)](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/254)
* Supersedes: [#253 — Modernize operational medallion notebooks](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/253)
