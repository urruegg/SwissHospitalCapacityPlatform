# Fabric F2 Capacity Lifecycle Runbook

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | n/a |

Runbook for pausing and resuming Fabric F2 capacities in SIT and PROD environments per Sprint 09 v2.0.0 DX.2 and design spec [§4.8](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md).

## When to use

- **Resume** before running any Fabric workload (dashboard load, notebook run, Data Agent query, semantic model refresh).
- **Suspend** immediately after workload completion in SIT to stop cost accrual.
- PROD should generally stay Active during business hours; suspend only during extended maintenance windows.

## Cost hygiene expectations per environment

| Env | Baseline stance | Weekend / off-hours | On-demand |
| --- | --- | --- | --- |
| SIT | **Paused** by default | Paused | Resume → run → Suspend cycle per demo/test session |
| PROD | **Active** during business hours | Suspend for maintenance windows only | n/a |

## Fixed values

- Subscription: `66a9953a-df37-4c51-856c-9971b9bf3e03`
- SIT resource group: `rg-ihzhhpf-sit` — capacity `fabricihzhhpfsit`
- PROD resource group: `rg-ihzhhpf-prod` — capacity `fabricihzhhpfprod`
- Region: `westus2` per [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md) (demo scope; sunset to `switzerlandnorth` when target services reach Swiss GA)

## Approach A — `az` CLI (preferred)

Both scripts are **idempotent** — safe to re-run. They check current state first via `az resource show` and no-op when already in the target state.

```powershell
# Resume SIT
./infra/scripts/Resume-FabricCapacity.ps1 -Environment sit

# Suspend SIT after work
./infra/scripts/Suspend-FabricCapacity.ps1 -Environment sit

# Same pattern for PROD (only with explicit approval — see cost hygiene table above)
./infra/scripts/Resume-FabricCapacity.ps1  -Environment prod
./infra/scripts/Suspend-FabricCapacity.ps1 -Environment prod
```

Under the hood both scripts call the proven Sprint 00 pattern:

```powershell
az resource invoke-action `
  --ids /subscriptions/66a9953a-df37-4c51-856c-9971b9bf3e03/resourceGroups/rg-ihzhhpf-sit/providers/Microsoft.Fabric/capacities/fabricihzhhpfsit `
  --action resume   # or suspend
```

## Approach B — Playwright admin-portal fallback (when CLI unavailable)

1. Navigate to `https://app.fabric.microsoft.com/admin-portal/capacities/capacitiesList`.
2. Select the target capacity (`fabricihzhhpfsit` or `fabricihzhhpfprod`).
3. Click **Resume** or **Pause** in the top action bar.
4. Confirm the state change via the state indicator (`Active` / `Paused`).

Screenshot markers to capture for evidence (when running the fallback manually):

- `evidence/fabric-lifecycle/<env>-before.png` — capacities list showing current state
- `evidence/fabric-lifecycle/<env>-action.png` — action confirmation dialog
- `evidence/fabric-lifecycle/<env>-after.png` — capacities list showing new state

Playwright automation stub (deferred to Sprint 10):

```typescript
await page.goto('https://app.fabric.microsoft.com/admin-portal/capacities/capacitiesList');
await page.getByRole('link', { name: 'fabricihzhhpfsit' }).click();
await page.getByRole('button', { name: 'Resume' }).click();
await expect(page.getByText('Active')).toBeVisible({ timeout: 30_000 });
```

## GitHub Actions

Manual dispatch via [`fabric-capacity-lifecycle.yml`](../../.github/workflows/fabric-capacity-lifecycle.yml) — pick action (`resume` / `suspend`) and environment (`sit` / `prod`). The workflow authenticates via OIDC using repo secrets `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID`.

## Verification checklist

- [ ] `az account show` reports logged-in identity
- [ ] `az account set --subscription 66a9953a-df37-4c51-856c-9971b9bf3e03` runs clean
- [ ] Script exit code `0`
- [ ] `az resource show --ids <capacityId> --query properties.state -o tsv` returns the expected state (`Active` after resume, `Paused` after suspend)
- [ ] Portal indicator matches CLI-reported state

## References

- Design spec §4.8: [`docs/superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md`](../superpowers/specs/2026-07-02-sprint-09-v2-refinement-design.md)
- Implementation plan §DX.2: [`docs/superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md`](../superpowers/plans/2026-07-02-sprint-09-v2-refinement-plan.md)
- ADR-0013 westus2 demo scope: [`docs/adr/0013-temporary-us-region-demo-scope.md`](../adr/0013-temporary-us-region-demo-scope.md)
- Sprint 00 tenant migration proof: `az resource invoke-action --action suspend` executed successfully against `fabricihzhhpfsit` at Sprint 00 close
