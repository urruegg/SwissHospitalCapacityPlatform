# Fabric IQ release train — reproducible fabric-cicd deploy

> **Version** 1.2.0 · **Date** 2026-07-29 · **Author** Urs Rüegg · **Status** Reviewed · **Previous Version** 1.1.0 (added the reproducible medallion rebuild + gold-parity proof section)

Runbook for the **Fabric IQ release train**: a parameterized
[`fabric-cicd`](https://microsoft.github.io/fabric-cicd/) deploy that takes the
SIT-pinned PBIP source under `data-platform/reports/` and publishes the
`capacity-dashboard` semantic model (+ report) into a chosen environment's
Fabric workspace, rewriting the Direct Lake OneLake path so the same source
tree targets a different workspace by changing `--environment` only.

Implements decisions **D5** (deploy via fabric-cicd) and **D7** (build the
release train before deploying PROD) of the
[Fabric IQ → Foundry readiness design](../../../docs/superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md).

**Scope guard:** synthetic data only, no PHI
([ADR-0013](../../../docs/adr/0013-temporary-us-region-demo-scope.md),
[ADR-0016](../../../docs/adr/0016-no-phi-in-mvp-demo-scope.md)). Both SIT and
PROD Fabric run in **westus2**
([ADR-0035](../../../docs/adr/0035-fabric-iq-layer-region-westus2.md)) because
the subscription has 0 CU Fabric quota in eastus2.

## What the train deploys (and what it does not)

`fabric-cicd` reproducibly deploys **only** the Git-serializable PBIP items:

* `capacity-dashboard.SemanticModel` (Direct Lake, 13 gold tables, RLS roles)
* `capacity-dashboard.Report`

Everything else in the Fabric IQ layer stays a portal/REST/notebook step
(tracked in the readiness design as Phase 2), because those artefacts are not
PBIP source items:

* Lakehouse **data** (gold tables) — loaded by the simulator/notebooks first;
  the Direct Lake model resolves against them, so the tables must exist
  **before** a publish succeeds.
* Fabric IQ **ontology** (`ont_hospital_capacity`) — Fabric REST
  `updateDefinition`.
* **Data Agent** (`da_hospital_capacity`) — portal-only
  (see [`create_data_agent.md`](create_data_agent.md)).
* OneLake **Data Product** + healthcare **Domain** — portal (tenant-admin).

The unrelated `evidence` and `bva-boardroom` items that also live under
`data-platform/reports/` are excluded from this train
(`item_name_exclude_regex`).

## Files

| File | Role |
| ---- | ---- |
| [`../../fabric/environments.yml`](../../fabric/environments.yml) | Variable library — SIT/PROD → workspace + lakehouse coordinates. |
| [`../../reports/parameter.yml`](../../reports/parameter.yml) | fabric-cicd `find_replace` for the OneLake workspace + lakehouse GUIDs, keyed by environment. |
| [`deploy_fabric_cicd.py`](deploy_fabric_cicd.py) | Orchestrator — `--mode validate` (network-free) and `--mode publish` (live). |
| [`../../../.github/workflows/fabric-cicd-deploy.yml`](../../../.github/workflows/fabric-cicd-deploy.yml) | CI: `validate` on PR/push, gated `publish` on `workflow_dispatch`. |

The repository files stay **SIT-pinned**. `find_replace` substitutes in-memory
during a publish only, so the SIT GUIDs committed in the Direct Lake
`expressions.tmdl` and the `verify-semantic-model.yml` exact-count gate both
stay valid.

## Environment coordinates (as-built)

| Environment | Workspace | Lakehouse | Capacity | Region |
| ----------- | --------- | --------- | -------- | ------ |
| SIT | `ws-ihzhhpf-sit-data` `f3af9733-9503-4e92-98f9-a901d96f1c87` | `lh_ihzhhpf_sit` `30594c20-46ba-40ea-91fa-4701b105e0b9` | `fabricihzhhpfsit` | westus2 |
| PROD | `ws-ihzhhpf-prod-data` `1c8408f4-6eb7-401f-aee9-77fe4c8a515e` | `lh_ihzhhpf_prod` `57bd6e02-5248-439c-9f31-16bf9ee83cb4` | `fabricihzhhpfprod` | switzerlandnorth |

## Local prerequisites

* **Python < 3.13** — `fabric-cicd` caps below 3.13. On this workstation use
  `py -3.11`. `--mode validate` is network-free and needs only PyYAML, so it
  runs on any Python.
* For `--mode publish` locally: `az login` (the script uses
  `AzureCliCredential`) with an identity that is a **Member/Admin of the target
  Fabric workspace**.

```powershell
py -3.11 -m pip install --user fabric-cicd azure-identity pyyaml
```

## Validate (network-free, safe anywhere)

Cross-checks the variable library against the fabric-cicd parameter file,
asserts every `find_value` is present in the semantic-model TMDL, and confirms
the deployable item folders exist on disk.

```powershell
py -3.11 data-platform/scripts/fabric/deploy_fabric_cicd.py --environment PROD --mode validate
py -3.11 data-platform/scripts/fabric/deploy_fabric_cicd.py --environment SIT  --mode validate
```

## Publish (live — deploy-class, gated)

Prefer the CI workflow so the deploy runs under the OIDC service principal with
an audited approval, rather than an interactive session.

* **CI (preferred):** run the `fabric-cicd-deploy` workflow via
  `workflow_dispatch`, choose the environment, and type `approved-to-apply` in
  the confirm input. A `PROD` publish is additionally gated by the GitHub
  `prod` environment reviewer.
* **Local (break-glass):**

```powershell
az login
py -3.11 data-platform/scripts/fabric/deploy_fabric_cicd.py --environment PROD --mode publish
```

### CI publish prerequisite (one-time)

The OIDC service principal `gh-oidc-ihzhhpf`
(`secrets.AZURE_CLIENT_ID` = `cbecd109-2ac5-466b-b08e-2a97556274d2`) must be a
**Member** (or Admin) of the target Fabric workspace so `fabric-cicd` can call
the Fabric REST APIs. Grant it once per workspace (Fabric portal → workspace →
Manage access → Add people/groups → the SP → Member). Without this the publish
job fails on the first Fabric REST call with a 401/403.

## Ordering constraint (important)

The `capacity-dashboard` semantic model is **Direct Lake**. A publish binds it
to the target lakehouse's gold tables, so **load the lakehouse first**:

1. Create the workspace + lakehouse (done for PROD:
   `ws-ihzhhpf-prod-data` + `lh_ihzhhpf_prod`).
2. Run the simulator/notebooks to populate the gold tables.
3. `--mode publish` the semantic model + report.
4. Portal/REST: ontology → endorsement → Data Agent → Data Product + Domain.

## Reproducible medallion rebuild (step 2, git-only)

Step 2 above — "populate the gold tables" — is itself fully **git-reproducible**
via [`run_medallion.py`](run_medallion.py). It create-or-updates the eight
canonical operational notebooks in the target workspace from their committed
`.ipynb`, injects the target lakehouse as the run-time default (so the same
source binds to SIT or PROD by `--environment` only), and runs them in
dependency order:

1. `01_bronze_master_data` → `02_silver_master_data` → `03_gold_master_data`
2. `04_load_or_samples`
3. `00_seed_eventstream_raw` → `01_bronze_eventstream` →
   `02_silver_eventstream` → `03_gold_eventstream`

The patient-flow lane (steps under 3) has **no live Eventstream dependency**:
[`00_seed_eventstream_raw.ipynb`](../../notebooks/eventstream/00_seed_eventstream_raw.ipynb)
materialises `Tables/bronze_eventstream_raw` from the committed synthetic
corpus [`data/synthetic/eventstream/eventstream_raw.json`](../../../data/synthetic/eventstream/eventstream_raw.json)
(generated deterministically by
[`gen_eventstream_seed.py`](../gen_eventstream_seed.py); 840 FK-consistent,
PHI-clean envelopes across 4 hospitals × 7 eventKinds). Batch bronze overwrites
with `overwriteSchema` so a rebuild replaces any stale live-Eventstream
partitions; gold `_flatten_payload` reads the JSON-string payload via
`get_json_object`.

Upload the source once per environment, then run and verify parity:

```powershell
# 1) source data (master-data CSVs + OR JSON + eventstream seed) → Files/
py -3.11 data-platform/scripts/upload_to_onelake.py --workspace-id <ws> --lakehouse-id <lh> --source-root data/synthetic/master-data/capacity --target master-data/capacity
py -3.11 data-platform/scripts/upload_to_onelake.py --workspace-id <ws> --lakehouse-id <lh> --source "data/synthetic/eventstream/*.json" --target eventstream-seed

# 2) plan-first (no writes), then apply (deploy-class, approved-to-apply gate)
py -3.11 data-platform/scripts/fabric/run_medallion.py --environment SIT
py -3.11 data-platform/scripts/fabric/run_medallion.py --environment SIT --apply

# 3) prove 13-table gold parity
py -3.11 data-platform/scripts/fabric/list_gold_tables.py --environment SIT > produced.txt
py -3.11 data-platform/scripts/verify_gold_schema.py --produced produced.txt
```

### Task 14 proof (2026-07-20, issue #254 / closes #253)

Both environments rebuilt the schemas-enabled gold layer to full contract
parity from git only (committed notebooks + committed synthetic seed, no live
Eventstream):

| Environment | Notebooks | Gold parity | Patient-flow lane |
| ----------- | --------- | ----------- | ----------------- |
| SIT | 8/8 `[ok]` | `OK: gold parity (13 contract tables covered).` | `encounter` + `bed_assignment` freshly produced from the seed |
| PROD | 8/8 `[ok]` | `OK: gold parity (13 contract tables covered).` | `encounter` + `bed_assignment` freshly produced (were the 2 tables missing at the prior 11/13) |

## Related

* [Fabric IQ → Foundry readiness design](../../../docs/superpowers/specs/2026-07-17-fabric-iq-foundry-readiness-design.md)
* [ADR-0035 — Fabric IQ layer region westus2](../../../docs/adr/0035-fabric-iq-layer-region-westus2.md)
* [Create + publish the Fabric Data Agent](create_data_agent.md)
