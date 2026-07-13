# Entra provisioning scripts

Helper scripts that pair with the Bicep modules under [`../../infra/modules/entra/`](../../infra/modules/entra/).

## When to use

The Bicep module is the source of truth for the identity model (17 app roles,
17 security groups, 17 group-based app-role assignments). Scripts in this folder
fill the gaps the Microsoft Graph Bicep extension **cannot** cover — currently
that is user creation and per-user group membership, because
`Microsoft.Graph/users` is intentionally read-only in the extension (see
[ADR-0027](../../docs/adr/0027-mcaps-demo-users-full-group-membership.md)).

## Scripts

### `assign-demo-users-all-groups.ps1`

Adds `admin@mngenvmcap164444.onmicrosoft.com` and
`urruegg@MngEnvMCAP164444.onmicrosoft.com` as members of all 17 HCC.\* security
groups. Idempotent — reruns are safe and skip already-member cases.

Runs against whichever tenant the current `az` context is signed into. Verify
before running:

```powershell
az account show --query "{tenantId: tenantId, user: user.name}" -o table
```

Then:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\entra\assign-demo-users-all-groups.ps1
```

Runs after `entra-sit-groups-<timestamp>` has completed successfully — see the
Sprint 12 apply artefacts in the audit checklist for the concrete deployment
names.
