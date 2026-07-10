# Adoption telemetry ingest (Sprint 12 · T5)

Bronze ingest of Entra sign-in telemetry that feeds the Sprint 15 BVA "adoption %"
KPI. Nightly, the [`adoption-refresh.yml`](../../../.github/workflows/adoption-refresh.yml)
workflow triggers the Fabric notebook below, which lands the last 24h of
`ihzhhpf-app` sign-ins as raw JSON in the lakehouse Bronze layer.

- Design contract: [`docs/superpowers/specs/2026-07-09-sprint-12-org-design.md`](../../../docs/superpowers/specs/2026-07-09-sprint-12-org-design.md) §7.
- Diagnostic routing: [`infra/modules/entra/adoption-telemetry.bicep`](../../../infra/modules/entra/adoption-telemetry.bicep) (Entra `SignInLogs` → `log-ihzhhpf-sit`).

## Layers

| Notebook | Layer | Writes |
| --- | --- | --- |
| `01_adoption_ingest.ipynb` | Bronze | `Files/Bronze/adoption/YYYY-MM-DD/signins.json` (one raw JSON file per sign-in day) |

Silver typing (deduplication + role/hospital join + `env` tag) and the Gold
`Fact_ValueRealization` join are owned by the [BVA medallion](../bva/README.md).

## Bronze adoption contract

Each row in `signins.json` carries these fields (design spec §7), redacting the
IP to a `/24`. **No PHI** — sign-in metadata carries UPN + IP only.

```text
userId, upn, appDisplayName, appId, signInTimestamp, env, resultType,
ipAddress (/24), clientAppUsed, deviceDetailTrustType,
locationCountryOrRegion, appRole
```

The shape is **identical** to the synthetic backfill emitted by
[`data-platform/scripts/adoption_seed_synthetic.py`](../../../data-platform/scripts/adoption_seed_synthetic.py),
so real and seeded telemetry are interchangeable for the downstream BVA
consumer [`data-platform/notebooks/bva/ingest_bronze_adoption.py`](../bva/ingest_bronze_adoption.py).

## Single tested implementation

The row-mapping logic lives in the pure, framework-agnostic
[`adoption_transforms.py`](adoption_transforms.py) (no PySpark, no I/O) so it is
unit-testable in CI — the same convention as the BVA medallion's
`bva_transforms.py`. The notebook reads `SigninLogs` from Log Analytics,
`collect()`s the rows to the driver, applies the pure functions, and writes one
JSON file per sign-in day. The same functions work unchanged against a Microsoft
Graph `auditLogs/signIns` projection.

Run the tests:

```bash
python3 -m unittest discover -s data-platform/notebooks/adoption/tests -v
```

CI gate: [`.github/workflows/adoption-ingest.yml`](../../../.github/workflows/adoption-ingest.yml).

## Wiring the nightly workflow (operator step)

`adoption-refresh.yml` triggers this notebook by ID and needs two repository
variables. After the notebook is imported into `ws-ihzhhpf-sit-data` and has a
stable GUID, set them once (repo admin / `gh` with `repo` scope):

```powershell
gh variable set FABRIC_WORKSPACE_ID --body f3af9733-9503-4e92-98f9-a901d96f1c87
gh variable set FABRIC_ADOPTION_NOTEBOOK_ID --body <notebook-guid-after-import>
```

`AZURE_CLIENT_ID` (secret) and `AZURE_TENANT_ID` (variable) are already provided
by the `sit` environment. Triggering the Fabric run is a `deploy`-ceiling action
gated by `approved-to-apply` (AGENTS.md §4).
