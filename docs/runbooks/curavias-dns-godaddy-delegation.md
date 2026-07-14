# Runbook — curavias.ch DNS delegation from GoDaddy to Azure DNS

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-14 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (initial Phase 1 + Phase 2 sequence) |
| **Related** | [ADR-0030](../adr/0030-curavias-dns-strategy.md), [`infra/modules/dns/curavias.bicep`](../../infra/modules/dns/curavias.bicep), [`infra/modules/apps/hcc-app-fluent/main.bicep`](../../infra/modules/apps/hcc-app-fluent/main.bicep) |

## When to use this runbook

Follow this after the SIT deploy provisions the Azure DNS zone for
`curavias.ch` but before flipping `appFluentEnableCustomDomainCert = true`.
This is the one-time delegation step — subsequent deploys / hostname
additions don't require you to touch GoDaddy again.

## Prerequisites

- SIT deploy has landed the DNS zone (`az network dns zone show -g rg-ihzhhpf-sit -n curavias.ch` returns a resource)
- GoDaddy account with admin rights on `curavias.ch`
- ~30-60 min for propagation

## Step 1 — Get the Azure DNS name servers

```powershell
az network dns zone show `
  --resource-group rg-ihzhhpf-sit `
  --name curavias.ch `
  --query nameServers `
  --output tsv
```

Expected output: four hostnames like:

```text
ns1-XX.azure-dns.com.
ns2-XX.azure-dns.net.
ns3-XX.azure-dns.org.
ns4-XX.azure-dns.info.
```

The exact `XX` varies per zone. Copy all four **without the trailing dot** —
GoDaddy adds it automatically.

Alternative source: the top-level `az deployment group create` output
includes `curaviasNameServers` in the outputs block.

## Step 2 — Update NS records at GoDaddy

1. Sign in to GoDaddy — https://dcc.godaddy.com/domains
2. Select `curavias.ch` → **DNS** → **Nameservers**
3. Choose **Change → I'll use my own nameservers**
4. Paste the four Azure name servers, one per row (no trailing dots)
5. Save

GoDaddy typically shows a "changes are being applied" banner. Propagation is
generally under 1 hour but can take up to 24 hours worst case.

## Step 3 — Verify propagation

Run every ~5 min until all four Azure name servers appear:

```powershell
nslookup -type=NS curavias.ch 8.8.8.8
# or:
Resolve-DnsName curavias.ch -Type NS -Server 8.8.8.8
```

Successful output:

```text
curavias.ch  nameserver = ns1-XX.azure-dns.com
curavias.ch  nameserver = ns2-XX.azure-dns.net
curavias.ch  nameserver = ns3-XX.azure-dns.org
curavias.ch  nameserver = ns4-XX.azure-dns.info
```

Also verify Azure DNS is authoritative for the CNAME/TXT records:

```powershell
Resolve-DnsName appsit.curavias.ch -Type CNAME -Server 8.8.8.8
Resolve-DnsName asuid.appsit.curavias.ch -Type TXT -Server 8.8.8.8
```

The CNAME should resolve to `ca-app-fluent-ihzhhpf-sit.<CAE-domain>.westus2.azurecontainerapps.io`.
The TXT record should contain the Container App's `customDomainVerificationId`.

## Step 4 — Flip the cert flag

Edit [`infra/environments/sit.bicepparam`](../../infra/environments/sit.bicepparam):

```diff
- param appFluentEnableCustomDomainCert = false
+ param appFluentEnableCustomDomainCert = true
```

Open a small PR (2-line change), merge → auto-triggers `cd-infra-deploy-sit`.
Approve at the `sit` env gate.

The deploy will:

1. Provision `Microsoft.App/managedEnvironments/managedCertificates` named
   `cert-appsit-curavias-ch` on the app-fluent CAE.
2. Azure Container Apps validates domain ownership via the `asuid.appsit`
   TXT record (Phase 1 already registered the hostname on the CA as
   `bindingType: Disabled`, which is required for the cert to validate).
3. A managed certificate is issued (~15–30 min). Azure Container Apps
   currently issues via **DigiCert / GeoTrust TLS RSA CA G1** in most
   commercial regions (was Let's Encrypt historically) — both are
   publicly-trusted CAs, outcome identical.
4. Container App ingress upgrades the binding from `Disabled` to
   `SniEnabled` and points to the new cert.

## Step 5 — Verify the custom hostname is live

```powershell
# DNS resolves to the CA
Resolve-DnsName appsit.curavias.ch

# HTTPS works with a valid cert
Invoke-WebRequest -Uri https://appsit.curavias.ch/ -UseBasicParsing | Select-Object StatusCode, Headers
```

Expected: HTTP 200, `Content-Type: text/html`, and the browser (or PowerShell)
should not complain about the certificate chain.

Optional cert-chain inspection:

```powershell
openssl s_client -connect appsit.curavias.ch:443 -servername appsit.curavias.ch < NUL 2>NUL | openssl x509 -noout -issuer -subject -dates
```

Issuer should read one of the Azure-managed PKI chains — in commercial
regions today typically `DigiCert Inc / GeoTrust TLS RSA CA G1`. In older
deploys or some regions the issuer may still be `Let's Encrypt` with
intermediates `E5`/`E6`/`R3`. Both are publicly-trusted CAs and both
auto-renew via Azure Container Apps.

## Rollback

If anything goes wrong, revert in this order:

1. **Set `appFluentEnableCustomDomainCert = false`** in `sit.bicepparam`,
   redeploy. Custom domain binding is removed from the CA; managed cert
   resource is deleted. CA continues serving the Azure-provided hostname.
2. **Revert GoDaddy NS records** to GoDaddy's default nameservers. `curavias.ch`
   goes back to GoDaddy DNS control. The Azure DNS zone still exists in
   `rg-ihzhhpf-sit` but is no longer authoritative on the public internet.
3. **Delete the Azure DNS zone** if desired (fully undoes the ADR-0030
   deployment): `az network dns zone delete -g rg-ihzhhpf-sit -n curavias.ch --yes`.

## Troubleshooting

### Managed cert stuck at `provisioningState: Failed`

- Verify DNS propagation is complete (Step 3)
- Verify the `asuid.appsit.curavias.ch` TXT record is exactly the CA's
  `customDomainVerificationId`. If the CA was recreated, the ID may have
  changed — trigger a `cd-infra-deploy-sit` redeploy to refresh the TXT
  record before retrying the cert issuance.
- Manual retry: `az containerapp env certificate create --managed-certificate --resource-group rg-ihzhhpf-sit --name cae-app-fluent-ihzhhpf-sit --hostname appsit.curavias.ch --validation-method CNAME`

### Browser shows cert warning after deploy succeeded

- Wait 5-10 min after the deploy — cert propagation to the ACA edge is
  eventual.
- Clear browser HSTS cache if you tested a self-signed cert on the same
  hostname earlier.

### MSAL redirect URI still points to the old azurecontainerapps.io hostname

- That's Follow-up 2 in ADR-0030 — the Entra Bicep needs a separate manual
  apply. Not covered by `cd-infra-deploy-sit`. Track separately after this
  runbook is complete.
