# Sprint 19 — PROD network parity live verification (2026-07-24)

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | — |

This evidence verifies that PROD Switzerland North network parity for the Curavias
platform was applied to `rg-ihzhhpf-prod` via commits `8213dd7` and `cb6b56c`,
and is the live verification record for
[ADR-0039](../../../adr/0039-prod-network-parity-vnet-private-endpoints.md).

## Live az evidence (2026-07-24)

```text
# az network vnet list -g rg-ihzhhpf-prod
vnet-platform-ihzhhpf-prod  addressSpace 10.70.0.0/16

# az network private-endpoint list -g rg-ihzhhpf-prod
pe-cosmos-csa-ihzhhpf-prod   group Sql    connectionState Approved
pe-cosmos-ihzhhpf-prod       group Sql    connectionState Approved
pe-kv-ihzhhpf-prod-swn1      group vault  connectionState Approved

# az containerapp env show -n cae-ihzhhpf-prod -g rg-ihzhhpf-prod
provisioningState Succeeded
vnetConfiguration.infrastructureSubnetId .../vnet-platform-ihzhhpf-prod/subnets/snet-cae
vnetConfiguration.internal false

# az keyvault show -n kv-ihzhhpf-prod-swn1
properties.publicNetworkAccess Disabled

# az acr list -g rg-ihzhhpf-prod
crihzhhpfprod  sku Basic  publicNetworkAccess Enabled

# az containerapp show -n ca-signal-runner-ihzhhpf-prod -g rg-ihzhhpf-prod
provisioningState Succeeded  identity.type UserAssigned
```

## Interpretation

The live evidence matches the SIT network baseline for the network parity scope:
`vnet-platform-ihzhhpf-prod` exists with the PROD `10.70.0.0/16` address space;
the platform Cosmos, CSA Cosmos, and Key Vault private endpoints are all
`Approved`; `cae-ihzhhpf-prod` is VNet-integrated on `snet-cae` with
`provisioningState Succeeded`; and `kv-ihzhhpf-prod-swn1` has public network
access disabled. Together, this confirms the PROD VNet + three private endpoints
+ VNet-integrated Container Apps Environment + Key Vault public-access-disabled
posture now matches the SIT network posture.

Note: ACR `crihzhhpfprod` still has `publicNetworkAccess Enabled`, and ACR is
referenced by name rather than created by a module. This remains tracked under
issue #252 Gap 3 as a follow-up, not a network parity blocker for the
synthetic-only, no-PHI, no-data-plane scope.
