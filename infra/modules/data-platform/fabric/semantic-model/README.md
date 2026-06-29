# Semantic Model — `sm_capacity_data_product` (W1.4 thin slice)

Direct Lake Power BI semantic model that exposes `lh_chhealthpf_sit.gold.demand_encounter` to Power BI without a refresh step. This is the walking-skeleton scope from spec §8.1 W1.4: one table, one measure (`Encounter Count`). The W2.4 widen slice adds the remaining `DC-DEMAND-ENCOUNTER-v1` measures.

## File layout

```text
sm_capacity_data_product/
  .platform                                 # Fabric item metadata (type, displayName, logicalId)
  definition.pbism                          # Power BI semantic model project pointer
  definition/
    database.tmdl                           # Tabular database header (compatibilityLevel 1604)
    model.tmdl                              # Model header + table reference
    dataSources.tmdl                        # OneLake Direct Lake datasource (placeholders substituted at deploy time)
    tables/
      demand_encounter.tmdl                 # Table + Direct Lake partition + Encounter Count measure
```

## Direct Lake binding

The partition reads directly from the Delta files of `gold.demand_encounter` in the lakehouse — no import, no refresh schedule. Power BI queries hit OneLake in near real time.

```tmdl
partition 'demand_encounter' = directLake
    mode: directLake
    source = entity 'gold.demand_encounter'
```

`dataSources.tmdl` carries two placeholders, `[WORKSPACE_GUID]` and `[LAKEHOUSE_GUID]`, that the deploy script substitutes with the workspace and lakehouse IDs created earlier in `configure-fabric.ps1`.

## Why `patient_id` is intentionally NOT exposed

`gold.demand_encounter` carries a pseudonymised `patient_id` (`pseudo-[a-z0-9]{16}`). The pseudonym is not direct PII, but exposing it in the report layer would still allow analysts to count distinct patients across reports, which is a re-identification surface this thin slice does not need. The semantic model therefore **omits `patient_id`** entirely. If a future measure needs patient-level distinct counts, that requires a separate `data-design-agent` review and an addition to `DC-DEMAND-ENCOUNTER-v1` exposure rules.

A pytest enforces that `patient_id` does not appear in any TMDL file under this folder: see [`tests/test_tmdl_definition.py::test_no_patient_id_in_any_tmdl_least_disclosure`](tests/test_tmdl_definition.py). A Pester case mirrors the invariant on the base64-encoded deploy payload.

## Measures (this slice)

| Measure | Expression | Format |
|---------|------------|--------|
| `Encounter Count` | `COUNTROWS('demand_encounter')` | `#,##0` |

Forward work (W2.4): `Avg LOS`, `Discharges Today`, `Forecast Demand 24h`.

## Deploy

This folder is consumed by `infra/modules/data-platform/fabric/post-deploy/configure-fabric.ps1` step 4. The script reads the four TMDL files, substitutes the OneLake GUID placeholders, base64-encodes each, and POSTs to `https://api.fabric.microsoft.com/v1/workspaces/{wsId}/items` with `type=SemanticModel` and `definition.format=tmdl`.

```powershell
. .\configure-fabric.ps1 -CapacityName 'fabricchhealthpfsit' -ConnectionId '<guid>'
```

The semantic model is created after the workspace, lakehouse, and mirror exist.

## Test commands

```powershell
# TMDL definition shape (plain-text asserts, no Spark, no Fabric)
.\.venv-sprint08\Scripts\python.exe -m pytest `
    infra/modules/data-platform/fabric/semantic-model/tests/ -v

# PowerShell payload builder (Pester)
Invoke-Pester -Path infra/modules/data-platform/fabric/post-deploy/tests/configure-fabric.Tests.ps1 -Output Detailed
```

Acceptance per spec §8.1 W1.4: after deploy, opening the semantic model in Power BI and dragging `Encounter Count` onto a card returns `1` (the single row seeded by W1.1 plus the mirror path from W1.2/W1.3).
