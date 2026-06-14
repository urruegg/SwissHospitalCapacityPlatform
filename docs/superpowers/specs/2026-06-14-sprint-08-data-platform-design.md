# Sprint 08 - Data Platform Resources and Data Ingestion Pipeline (Design)

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-06-14 |
| **Author** | Urs Ruegg (with GitHub Copilot) |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (initial design; corrected to treat silver as intermediate non-contracted zone since DC-EPISODE/ENCOUNTER do not exist in `data/synthetic/schema/`) |
| **Sprint** | [docs/sprints/sprint-08-data-platform-resources-and-ingestion-pipeline.md](../../sprints/sprint-08-data-platform-resources-and-ingestion-pipeline.md) |
| **Umbrella issue** | `#66` |
| **Baseline PR** | `#67` |

## 1. Purpose

Establish the data-platform resources and end-to-end ingestion pipeline that
operate the patient capacity planning data product delivered in Sprint 07.
The platform replicates a synthetic KIS-shape SQL source into Microsoft
Fabric / OneLake, conforms data through bronze, silver, and gold zones aligned
to the Sprint 07 data contracts, publishes a Direct Lake Semantic Model for
Power BI, and runs a Real-Time Capacity Simulator that emits continuous
metadata-only demand events into the same gold path.

Sprint 08 is delivered as a **thin end-to-end vertical first**, then widened
slice by slice. The walking skeleton is one happy-path episode end-to-end by
end of week 1; the sprint exits with all four slices widened to a working
data product in SIT.

## 2. Decisions

| # | Decision | Choice | Rationale |
| --- | -------- | ------ | --------- |
| D1 | Sprint sequencing | Thin end-to-end vertical first | Tracer-bullet; surfaces residency, identity-boundary, and contract-envelope issues earliest. |
| D2 | KIS source pattern | Azure SQL Database with synthetic KIS-shape schema | PaaS, residency clean, cheap, identical wire surface to a real KIS. VM/MI would add cost and ops without learning. |
| D3 | SQL to bronze ingestion | Fabric Mirroring | Zero custom code for the SQL hop; near-real-time; automatic lineage. Pipeline + Copy is the fallback if Mirroring's source list ever changes. |
| D4 | Silver/gold transforms | Fabric notebooks (PySpark) | Reviewable, code-first, TDD-friendly; aligns with regulated pipeline expectations. |
| D5 | Simulator hosting | Azure Container Apps (always-on producer + on-demand kickstart job) | Single shape covers continuous emission and scenario kickstart; scale-to-zero between scenarios. Function App's "always-on producer" is an anti-pattern; AKS is overkill. |
| D6 | Semantic Model storage | Direct Lake on gold Lakehouse | Near-real-time without refresh orchestration; single copy of data; makes the simulator demo land. |
| D7 | Region | `switzerlandnorth` | ADR-0003, ADR-0004. No PHI ever; no cross-region failover for planning data. |
| D8 | Environment | SIT only in Sprint 08 | PROD promotion is out of scope; covered in a future sprint. |
| D9 | IaC | Bicep under `infra/`, modules `source-sql`, `fabric`, `simulator`, `observability` | One module per unit; independently deployable for TDD. |
| D10 | Workflow | Superpowers Basic Workflow, mandatory | Consistent with Sprint 07 (`docs/sprints/sprint-07-data-platform-and-data-products-superpowers.md`). |

## 3. Architecture

### 3.1 Top-level shape

```text
# Region: switzerlandnorth   |   Env: SIT   |   No PHI anywhere

  +-----------------------------+         +-----------------------------+
  |  Azure SQL DB (KIS-shape)   |         |   Container Apps env        |
  |  - Episode, Encounter, etc. |         |  +-----------------------+  |
  |  - Seeded from              |         |  | sim-producer          |  |
  |    data/synthetic/datasets/ |         |  |  always-on, 1-5 evt/m |  |
  |  - Private endpoint, MI     |         |  +-----------+-----------+  |
  +--------------+--------------+         |              |              |
                 |                        |  +-----------+-----------+  |
                 |   Fabric Mirroring     |  | sim-kickstart (ACA    |  |
                 |   (managed CDC,        |  |  Job, on-demand)      |  |
                 |    near real-time)     |  +-----------+-----------+  |
                 v                        +--------------+--------------+
       +---------+----------+                            |
       |  OneLake bronze    |<---- Eventstream ----------+
       |  Delta tables      |
       +---------+----------+
                 |  notebook: validate + pseudonymise re-assert
                 v
       +---------+----------+
       |  OneLake silver    |   intermediate Delta tables
       +---------+----------+   (no formal contract; allow-listed shape)
                 |  notebook: conform, aggregate, tag
                 v
       +---------+----------+
       |  OneLake gold      |   DC-DEMAND-ENCOUNTER-v1
       +---------+----------+
                 |
                 v  Direct Lake (no refresh)
       +---------+----------+        +----------------+
       |  Semantic Model    |------> |  Power BI      |
       |  (Fabric workspace)|        |  (consumer)    |
       +--------------------+        +----------------+

  Crosscutting: Key Vault (managed identity), Log Analytics + App Insights,
                Private Endpoints, Purview lineage (auto), Bicep IaC under infra/
```

### 3.2 Three well-bounded units

1. **Source unit** - Azure SQL DB + seed scripts. Plays the KIS role.
2. **Platform unit** - Fabric capacity, workspace, Lakehouse, Mirror, notebooks, Eventstream, Semantic Model. Enforces contracts, publishes gold.
3. **Simulator unit** - ACA producer + kickstart job. Emits `DC-DEMAND-ENCOUNTER-v1`.

## 4. Components

### 4.1 Source unit (`infra/modules/source-sql/`)

| Component | Implementation | Owner contract |
| --------- | -------------- | -------------- |
| `sql-chhealthpf-sit` | Azure SQL Database, General Purpose Gen5, 2 vCore | Hosts the synthetic KIS schema |
| `kv-chhealthpf-sit` (existing) | Key Vault | Holds the SQL admin password (rotated, MI access only) |
| Private endpoint | Subnet `snet-data-sit` | Only path in |
| Seed job | `infra/scripts/seed-synthetic-kis.ps1`, invoked once at provision | Loads CSVs from `data/synthetic/datasets/` into `kis.*` tables |

**Seeded tables:** `kis.Patient` (pseudonymised header only), `kis.Episode`,
`kis.Encounter`, `kis.Diagnosis`, `kis.Procedure`. The table shape mimics a
real KIS extract; the columns store synthetic pseudonyms, codes, and
timestamps only.

### 4.2 Platform unit (`infra/modules/fabric/`)

| Component | Implementation | Owner contract |
| --------- | -------------- | -------------- |
| Fabric capacity F2 | `fabric-chhealthpf-sit`, `switzerlandnorth` | Smallest SKU supporting Direct Lake + Mirroring |
| Workspace | `ws-chhealthpf-sit-data` | Single workspace for the pipeline |
| Lakehouse | `lh_chhealthpf_sit` | Hosts `bronze.*`, `silver.*`, `gold.*` Delta tables |
| Mirror | `mir_chhealthpf_kis` | Replicates `kis.*` -> `bronze.kis_*` |
| Notebooks | `nb_silver_transform.py`, `nb_gold_publish.py` | Validate, re-assert pseudonymisation invariant, conform to contracts |
| Eventstream | `es_chhealthpf_sit` | Receives `DC-DEMAND-ENCOUNTER-v1` envelopes from the simulator, writes to `bronze.events_demand_encounter` |
| Semantic Model | `sm_capacity_data_product` | Direct Lake on `gold.*`; measures match the data contract |

### 4.3 Simulator unit (`infra/modules/simulator/` + `apps/sim-capacity/`)

| Component | Implementation | Owner contract |
| --------- | -------------- | -------------- |
| ACA env | `cae-chhealthpf-sit` | Shared env, private VNet, Log Analytics attached |
| `aca-sim-producer` | ACA app, scale 1 to 1, 0.5 vCPU / 1 GiB | Continuous emission at 1-5 events/min using profile from `data/synthetic/profiles/baseline.json` |
| `aca-sim-kickstart` | ACA Job, manual trigger | Resets in-memory state and replays a named scenario (`winter-flu-peak`, `surgery-strike`) |
| Image | `acr-chhealthpf-sit/sim:<git-sha>` | Built and pushed by GitHub Actions on PR merge |
| Identity | User-assigned managed identity | Eventstream Sender role, Key Vault Secrets User |

Repo layout for the simulator code:

```text
apps/sim-capacity/
  src/
    producer.py          # always-on entrypoint
    kickstart.py         # one-shot ACA Job entrypoint
    profiles/            # situational profiles
    contracts/           # DC-DEMAND-ENCOUNTER-v1 envelope helpers
  tests/
    test_producer.py
    test_envelope_invariants.py
  Dockerfile
  pyproject.toml
```

### 4.4 Cross-cutting

| Concern | Implementation |
| ------- | -------------- |
| Identity | User-assigned managed identity per unit; no connection strings in code |
| Secrets | Key Vault references in Bicep; never in app config |
| Network | `vnet-chhealthpf-sit`; private endpoints for SQL, Key Vault, Storage, Eventstream; ACA in `snet-aca-sit`; Fabric in `snet-fabric-sit` |
| Observability | App Insights `appi-chhealthpf-sit` for simulator; Log Analytics `log-chhealthpf-sit` for everything; single workbook `Capacity Platform Health` |
| Lineage | Fabric auto-emits to Purview (per `docs/COMPLIANCE.md`) |
| IaC | `infra/main.bicep` composes four modules: `source-sql`, `fabric`, `simulator`, `observability` |

## 5. Data Flow and Contracts

### 5.1 Two paths into bronze, one path out of gold

Batch path (KIS replication):

```text
Azure SQL DB (kis.*)
    | Fabric Mirroring (managed, near-real-time CDC)
    v
bronze.kis_patient, kis_episode, kis_encounter, kis_diagnosis, kis_procedure   (Delta)
    | nb_silver_transform.py (PySpark, micro-batch append)
    v
silver.episode, silver.encounter (intermediate Delta, allow-listed shape)     (Delta)
    | nb_gold_publish.py (PySpark, micro-batch append)
    v
gold.demand_encounter (DC-DEMAND-ENCOUNTER-v1)                                 (Delta)
```

Streaming path (simulator):

```text
aca-sim-producer --> Eventstream --> bronze.events_demand_encounter            (Delta)
                                          | nb_gold_publish.py
                                          v
                                     gold.demand_encounter (same target table)
```

Both paths land in **the same** `gold.demand_encounter` table. Downstream
consumers cannot tell whether a row originated from mirror or simulator; only
`provenance.source` differs (`kis-mirror` vs `simulator`).

### 5.2 Contract enforcement

| Boundary | Enforcement | Rejected payloads |
| -------- | ----------- | ----------------- |
| ACA producer to Eventstream | JSON Schema (`DC-DEMAND-ENCOUNTER-v1`) | Missing `purposeTags`, missing `residency`, any field on PII deny-list |
| Mirror to bronze | None (byte-for-byte) | n/a |
| `nb_silver_transform.py` | Great Expectations on bronze | Failing primary key, broken episode-encounter linkage, PII-shape failures |
| `nb_gold_publish.py` | Great Expectations on silver + envelope assertions | Rows missing `purposeTags=['capacity-planning']` or `residency='CH'` |
| Semantic Model load | Direct Lake fallback to DirectQuery on guardrail violation | Logged; no silent data loss |

### 5.3 Pseudonymisation invariant

`nb_silver_transform.py` enforces:

1. **Schema allow-list** - only columns in `DC-EPISODE-v1` / `DC-ENCOUNTER-v1` survive.
2. **Identifier shape** - `patient_id` matches `^pseudo-[a-z0-9]{16}$`; otherwise quarantine.
3. **Free-text scan** - any string column over 32 chars is hashed and quarantined.

The platform never de-pseudonymises; it only re-asserts that no PII columns
exist.

### 5.4 Contract registry (no new contracts in Sprint 08)

Data contracts apply at data-product boundaries, not at internal transform
layers. Sprint 08 therefore implements only one contracted boundary: the gold
zone.

| Contract | File | Owner |
| -------- | ---- | ----- |
| `DC-DEMAND-ENCOUNTER-v1` | `data/synthetic/schema/dc-demand-encounter-v1.schema.json` | Data design agent |

Silver tables (`silver.episode`, `silver.encounter`) are intermediate Delta
tables with an allow-listed column shape enforced in `nb_silver_transform.py`;
they deliberately have no formal contract. If a future use case needs to
expose silver to an external consumer, file a separate `data-design-agent`
issue to author a contract first.

If any gap appears during implementation against `DC-DEMAND-ENCOUNTER-v1`,
file a separate `data-design-agent` issue and amend the contract first.

### 5.5 Traceability

| Requirement (PRD) | Implemented by |
| ----------------- | -------------- |
| `FR-DATA-001` Hospitalisation Episode as control unit | `nb_silver_transform.py` (one row per episode in `silver.episode`) |
| `FR-DATA-002` Metadata-only envelope | `DC-DEMAND-ENCOUNTER-v1` validation on both paths into gold |
| `FR-DATA-003` Pseudonymous identifiers only | Pseudonymisation invariant (silver allow-list + shape check) |
| `FR-DATA-005` Capacity demand as DC | `nb_gold_publish.py` + simulator |
| `FR-DATA-006` Streaming demand path | Path 2 |
| `FR-DATA-008` Data product publication for Power BI | Direct Lake Semantic Model |
| `NFR-RES-001` Swiss data residency | All resources `switzerlandnorth`; verified in `infra/scripts/verify-residency.ps1` |
| `NFR-SEC-002` Managed identity, no secrets in code | All MI assignments via Bicep |
| `NFR-GOV-006` Traceability per PR | Sprint 08 PR template fields populated for every slice |

## 6. Error Handling

### 6.1 Three failure classes

| Class | Examples | Response | Owner |
| ----- | -------- | -------- | ----- |
| Contract violation | Row fails PII shape; envelope missing `purposeTags`; free-text leakage | Quarantine, never drop; alert | `nb_silver_transform.py`, ACA producer |
| Pipeline failure | Mirror lag over 10 min; notebook job fails; Eventstream backpressure | Retry with backoff, then alert; never silently catch up | Fabric, ACA |
| Infra failure | Region outage; Key Vault unavailable; SQL DB connection refused | Fail closed; no fallback to alt region (residency); alert | All units |

### 6.2 Quarantine pattern

Per silver and gold notebooks:

```text
bronze.kis_episode
    | (allow-list + invariant check)
    +-> silver.episode                       (passes)
    +-> silver.quarantine_episode            (fails; reason column attached)
```

Quarantine tables are first-class: queryable, 30-day retention, weekly KPI
counter, Log Analytics alert if any row appears.

Producer-side: contract violations never reach Eventstream. Failure to emit
valid events for over 60 s flips the readiness probe to unhealthy.

### 6.3 Pipeline failures

| Layer | Detection | Retry | Alert |
| ----- | --------- | ----- | ----- |
| Mirror lag | `mirror_lag_seconds` > 600 | managed | Sev 2 |
| Silver notebook fail | Fabric Pipeline status | 2 retries, exponential | Sev 1 |
| Gold notebook fail | Same | 2 retries, exponential | Sev 1 |
| Eventstream backpressure | `eventstream_inflight_events` > 10000 | ACA producer throttles | Sev 2 |
| ACA producer crash | Liveness probe | ACA restarts pod | App Insights exception |

Notebooks `MERGE INTO` on natural keys; never `OVERWRITE`. Re-running is
idempotent.

### 6.4 Infra failures (residency-first)

If `switzerlandnorth` is down, the platform is down. No automatic failover
for any component handling planning data (ADR-0004). Manual decision required
with governance approval. Runbook lives in `docs/OPERATIONS.md`.

- Key Vault unavailable -> ACA producer's MI token refresh fails -> readiness probe unhealthy -> no events emitted. No fallback to local secrets, ever.
- SQL DB unavailable -> mirror pauses (Fabric managed); catches up on reconnect; notebooks check mirror health before running.
- Eventstream unavailable -> ACA producer buffers up to 1000 events in-process, drops oldest; drop counter alerts at 1.

### 6.5 Explicitly not done

- No dead-letter queue for Eventstream (overkill for SIT-only simulator).
- No cross-region replication of Fabric / OneLake (residency rule).
- No try/except swallowing exceptions in notebooks. Fail loud.
- No SQL retry storms - SDK retry only, no second layer.

### 6.6 Observability contract

- One Log Analytics workspace: `log-chhealthpf-sit`.
- One App Insights component: `appi-chhealthpf-sit`.
- One workbook: `Capacity Platform Health` with three sections (Source, Pipeline, Simulator). IaC under `infra/modules/observability/`.
- Sev 1 alerts: silver fail, gold fail, ACA producer down over 60 s.
- Sev 2 alerts: mirror lag, quarantine over 0, drop counter over 0.

## 7. Testing

### 7.1 Layered strategy (TDD-first, mandatory)

| Layer | Framework | Asserts | Location |
| ----- | --------- | ------- | -------- |
| Contract envelopes | Python `unittest` | Schemas reject PII shapes, missing `purposeTags`, wrong `residency` | `data/synthetic/tests/` (extend) |
| ACA producer | `unittest` + `unittest.mock` | Emits N events at cadence; envelope passes contract; PII deny-list blocks bad shapes; in-process buffer caps at 1000 events and drops oldest on overflow | `apps/sim-capacity/tests/` |
| Silver notebook | `pytest` + local PySpark | Allow-list survives; quarantine row when PII shape fails; idempotent MERGE | `infra/modules/fabric/notebooks/tests/` |
| Gold notebook | Same | Both paths land in `gold.demand_encounter`; `provenance.source` distinguishes them | Same |
| Semantic Model | `semantic-link-labs` DAX | Each measure returns a value for known fixture; no null on empty filter | `infra/modules/fabric/semantic-model/tests/` |
| Bicep | `az bicep build`, `what-if`, PSRule for Azure | All resources `switzerlandnorth`; MI assigned; private endpoint configured; tags present | `infra/tests/` |
| Residency | `infra/scripts/verify-residency.ps1` (Resource Graph) | No resource outside `switzerlandnorth` | CI gate before `azd up` |
| E2E smoke | `pytest` after deploy | KIS row -> `gold.demand_encounter` in under 10 min; kickstart -> simulator events in `gold.demand_encounter` in under 90 s | `tests/e2e/` |

TDD order is mandatory: test -> red -> implementation -> green -> refactor.
No notebook cell, Bicep module, or producer function lands without a failing
test first.

Local-first: every test must run on a laptop without an Azure account.
PySpark local session for notebooks, `azurite` if storage emulation is
needed, Eventstream client mocked.

### 7.2 CI gates

| Gate | Workflow | Blocks |
| ---- | -------- | ------ |
| Markdown lint | `markdown-lint.yml` | All doc PRs |
| Bicep build | `bicep-build.yml` | PR with `infra/**` |
| Bicep what-if | `bicep-whatif.yml` | PR with `infra/**` (actual deploy needs `approved-to-apply`) |
| PySpark unit tests | `pyspark-tests.yml` | PR with notebooks |
| Producer unit tests | `simulator-tests.yml` | PR with `apps/sim-capacity/**` |
| Residency check | `residency-check.yml` | Post-deploy gate |
| E2E smoke | `e2e-smoke.yml` | Post-deploy; must pass before sprint exit |
| Superpowers compliance | `superpowers-compliance.yml` (existing) | Every PR |

## 8. Sprint Slicing

### 8.1 Week 1 - Walking Skeleton (parallel PRs)

| PR | Branch | Delivery issue | Scope | Acceptance |
| -- | ------ | -------------- | ----- | ---------- |
| W1.1 | `s08-source-sql` | child of `#66` | Bicep `infra/modules/source-sql/` + seed for ONE episode row | `kis.episode` has 1 row in SIT |
| W1.2 | `s08-fabric-foundation` | child of `#66` | Bicep for Fabric capacity, workspace, Lakehouse, Mirror config | Mirror replicates `kis.episode` -> `bronze.kis_episode` |
| W1.3 | `s08-silver-gold-thin` | child of `#66` | `nb_silver_transform.py` + `nb_gold_publish.py` for ONE table path only | `gold.demand_encounter` shows 1 row from mirror path |
| W1.4 | `s08-semantic-model-thin` | child of `#66` | Direct Lake Semantic Model with ONE measure (`Encounter Count`) | Power BI shows `1` |
| W1.5 | `s08-simulator-thin` | child of `#66` | ACA producer emits ONE event, no scenarios | `gold.demand_encounter` shows 1 simulator-source row; Power BI shows `2` |

End-of-W1 demo: Power BI shows `Encounter Count = 2` (1 mirror + 1
simulator). Walking skeleton complete.

### 8.2 Week 2 - Widen

| PR | Scope |
| -- | ----- |
| W2.1 | Full KIS-shape schema in source (5 tables) |
| W2.2 | Silver/gold notebooks for Encounter, Diagnosis, Procedure |
| W2.3 | Simulator situational profiles (`baseline`, `winter-flu-peak`, `surgery-strike`) + kickstart job |
| W2.4 | Semantic Model measures matching `DC-DEMAND-ENCOUNTER-v1` (Encounter Count, Avg LOS, Discharges Today, Forecast Demand 24h) |
| W2.5 | Quarantine tables + Log Analytics workbook + alerts |
| W2.6 | E2E smoke test, residency check, KPI weekly report |

Sprint exit: 11 merged PRs under umbrella `#66`. Demo: insert KIS row ->
visible in Power BI in under 10 min; kickstart simulator scenario -> events
in Power BI in under 90 s.

## 9. Out of Scope

- PROD deployment (SIT only).
- Real KIS data of any kind.
- Power BI reports beyond the validation report used in the demo.
- Removing or weakening any approval gate.
- Cross-region replication or failover for planning data.
- New data contracts (Sprint 08 implements; it does not author).

## 10. Open Questions

- Fabric capacity SKU floor: F2 is assumed; confirm in W1.2 PR via what-if cost output.
- Whether the seed step should run as a Bicep `deploymentScript` or a separate GitHub Actions job - decided in W1.1 PR.
- Whether ACR is a new resource or reuses an existing registry - decided in W1.5 PR.

## 11. References

- [Sprint baseline](../../sprints/sprint-08-data-platform-resources-and-ingestion-pipeline.md)
- [docs/PRD.md](../../PRD.md)
- [docs/ARCHITECTURE.md](../../ARCHITECTURE.md)
- [docs/DATA.md](../../DATA.md)
- [docs/COMPLIANCE.md](../../COMPLIANCE.md)
- [docs/SECURITY.md](../../SECURITY.md)
- [docs/INFRASTRUCTURE.md](../../INFRASTRUCTURE.md)
- [docs/INTEGRATION.md](../../INTEGRATION.md)
- [docs/ALM_PLAN.md](../../ALM_PLAN.md)
- [docs/TEST.md](../../TEST.md)
- [docs/sprints/sprint-07/brainstorming-ingestion-pipeline-slice.md](../../sprints/sprint-07/brainstorming-ingestion-pipeline-slice.md)
- [docs/sprints/sprint-07/brainstorming-policy-evidence-slice.md](../../sprints/sprint-07/brainstorming-policy-evidence-slice.md)
- [ADR-0003](../../adr/0003-swiss-regional-inference-for-phi.md)
- [ADR-0004](../../adr/0004-block-global-and-data-zone-for-phi.md)
