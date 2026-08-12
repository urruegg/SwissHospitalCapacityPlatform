# ADR-0060: Microsoft Web IQ as a Governed Trust-B External Signal Channel

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-08-12 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related issue** | (Sprint 44) |

## Context

External signals (Sprint 21, [ADR-0036](0036-external-trigger-governance.md))
ingest only Trust-A Swiss public-authority hazard feeds (MeteoSwiss, SED-ETH,
BAG/FOPH, Alertswiss/BABS). [Microsoft Web IQ](https://webiq.microsoft.ai/) is a
commercial, preview/limited-access web-grounding API returning free-form
web/news/image/video content — a new *class* of source: non-authority,
non-Swiss, preview-gated, and free-form rather than a CAP-Suisse envelope.
[ADR-0054](0054-signal-channel-lifecycle.md) explicitly defers "live web-search
discovery." This ADR governs a narrow, sandboxed lift of that deferral so Web IQ
can act as an advisory early-warning channel without weakening the existing
human-in-the-loop and trust-tier controls.

## Decision

* Web IQ is classified **Trust-B**: advisory, human-curated, and never
  auto-evaluated against trigger rules, never auto-arms a lever, never
  auto-triggers a CSA handoff, and never enters the forecast-uplift overlay
  (consistent with [ADR-0036](0036-external-trigger-governance.md): only Trust-A
  auto-evaluates).
* The [ADR-0054](0054-signal-channel-lifecycle.md) "web-discovery deferred"
  boundary is lifted **only** for this governed case: onboarding runs the full
  `signal-agent` lifecycle with a sandbox Channel Readiness Scorecard and a HITL
  data-owner + compliance/DPO activation gate; no autonomous activation.
* The live Web IQ binding is **GA- and credential-gated** (parallel to
  [ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md)); demo and SIT
  run simulator-only, and CI always mocks the live binding (`NFR-EXT-PLG-001`).
* Outbound Web IQ queries contain **no PHI** ([ADR-0016](0016-no-phi-in-mvp-demo-scope.md));
  returned web content is untrusted and re-validated at every boundary
  (`NFR-SIG-001`), with only typed fields extracted and no free text forwarded
  into a tool or query.

## Consequences

### Positive

* Adds an earliest-warning, web-grounded situational-awareness channel without
  weakening HITL or trust-tier governance.
* Establishes a reusable pattern for future non-authority grounding sources.
* Reuses the entire Sprint 21 provider-plugin pipeline; no new agent and no MCP
  allow-list change.

### Live activation (Sprint 44 follow-up)

* The Web IQ live binding calls `POST https://api.microsoft.ai/v3/search/web`.
  **Auth is keyless-first**: the runner's user-assigned managed identity
  (`id-signal-runner-ihzhhpf-<env>`) acquires a Web IQ app-only token (scope
  `https://api.microsoft.ai/.default`, `Authorization: Bearer`) once its client
  id is bound in the Web IQ portal; enabled with `webiqEntraEnabled=true`. This
  matches the platform's RBAC-only / keyless posture (the PO-agent vault holds
  no secrets) and needs no Key Vault. An `x-apikey` from `WEBIQ_API_KEY` (Key
  Vault secret `webiq-api-key`) is retained only as a local/eval fallback.
* **Why keyless is primary here (network finding):** the platform Key Vaults are
  private-only. `kv-ihzhhpf-prod-swn1` has a private endpoint + `vaultcore` DNS
  zone (reachable from the VNet-integrated `cae-ihzhhpf-prod`), but
  `kv-ihzhhpf-sit-y26y` has **no private endpoint and public access disabled**,
  so a Container App Key Vault secret reference cannot resolve it on SIT. Keyless
  managed-identity auth sidesteps the vault entirely.
* **Config presence is the enablement gate**: with neither `webiqEntraEnabled`
  nor `WEBIQ_API_KEY` set, the live binding raises and the runner falls back to
  the simulator, so CI (`NFR-EXT-PLG-001`) and un-provisioned environments stay
  simulator-only with no code change.
* Enabling live is a **provider-runner infrastructure change** (real
  `signal-runner` image + `webiqEntraEnabled=true`, or the gated Key Vault secret
  path). The SIT/PROD deploy stays gated by `approved-to-apply`.
* Live Web IQ stays compatible with [ADR-0016](0016-no-phi-in-mvp-demo-scope.md):
  Web IQ returns public web content (no PHI), and the outbound query guard
  (`parse.build_query`) rejects any PHI-shaped term.

### Negative / risks

* Web content is untrusted (prompt-injection surface) — mitigated by the Trust-B
  classification, typed-field-only extraction, and the no-free-text-forwarding
  rule.
* No live entitlement in demo scope — mitigated by the simulator-first design and
  the credential/GA gate.

## Related

[ADR-0036](0036-external-trigger-governance.md) (external trigger governance),
[ADR-0054](0054-signal-channel-lifecycle.md) (signal-channel lifecycle),
[ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md) (GA-gating
pattern), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) (no PHI in demo scope).
