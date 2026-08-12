# Sprint 44 — Microsoft Web IQ as a Governed External Signal Channel

| Field | Value |
|-------|-------|
| **Version** | 1.2.0 |
| **Date** | 2026-08-12 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Build complete · provider-runner deployed to SIT + PROD (keyless MI, Event Hub ingress proven) · live Web IQ content + downstream Fabric/app wiring pending (see §6) |
| **Previous Version** | 1.1.0 (recorded build completion incl. Q1 hospital-service hazard scoping, corroboration + promote-to-watch wiring, i18n, golden task, channel-readiness scorecard); this bump adds §6 recording the 2026-08-12 SIT + PROD provider-runner deployment, keyless-MI + Event Hub ingress evidence, and the downstream-wiring open finding |
| **Design spec** | [`docs/superpowers/specs/2026-08-12-sprint-44-webiq-external-signal-channel-design.md`](../superpowers/specs/2026-08-12-sprint-44-webiq-external-signal-channel-design.md) |
| **Implementation plan** | [`docs/superpowers/plans/2026-08-12-sprint-44-webiq-external-signal-channel-plan.md`](../superpowers/plans/2026-08-12-sprint-44-webiq-external-signal-channel-plan.md) |
| **Governance ADR** | [`docs/adr/0060-webiq-external-signal-channel.md`](../adr/0060-webiq-external-signal-channel.md) |
| **Predecessors** | Sprint 21 (trusted external signals + provider-plugin architecture, ADR-0036) · Sprint 32 (signal-channel lifecycle, ADR-0054) |
| **Owner agents** | [`signal-agent`](../../agents/signal-agent/AGENT.md) (intake) · [`signal-triage-agent`](../../agents/signal-triage-agent/AGENT.md) (runtime) |
| **Workflow** | Trunk-based — [`docs/DEV_WORKFLOW.md`](../DEV_WORKFLOW.md) |

---

## 1. Sprint goal

Integrate **[Microsoft Web IQ](https://webiq.microsoft.ai/)** — Microsoft's AI-native
web-grounding API suite (fresh web pages, news, images, video) — as **one additional
external-signal channel** in Curavias that:

1. ingests hospital-material web/news signals as an earliest-warning channel,
2. uses that data to inform recommendations (advisory, human-gated), and
3. shows the signal on the Curavias app signal screen as one more channel.

Web IQ is a **commercial, preview-access, non-authority** web-grounding source — a new
*class* of source next to the Trust-A Swiss authority feeds. Under
[ADR-0036](../adr/0036-external-trigger-governance.md) it is therefore **Trust-B**:
advisory, human-curated, and it never auto-arms a lever, auto-triggers CSA, or enters the
forecast overlay.

## 2. Scope

- New provider plugin `data-platform/scripts/external-signals/providers/webiq/`
  (manifest + simulator + parse + gated live-adapter stub), auto-discovered by
  `registry.py`.
- `DC-EXT-SIGNAL-v1` → **v1.1.0**: optional `webCitations[]` grounded-evidence field
  (additive, backward-compatible).
- App: extend the shared `BoardSignal` + `ExternalSignal` model, render the Web IQ card
  with a Trust-B badge, clickable web citations, a HITL **promote-to-watch** action, and a
  display-only **corroboration** helper on the OOA + CSA boards.
- Governance: [ADR-0060](../adr/0060-webiq-external-signal-channel.md) records the new
  source class and the narrow, sandboxed lift of the ADR-0054 web-discovery deferral.

Out of scope: real/live Web IQ calls in CI/SIT/demo (GA + credential-gated); Trust-A
promotion; lever-arming or forecast-overlay contribution; any new agent or MCP-allow-list
change.

## 3. Requirements

`FR-EXT-021`, `FR-EXT-022`, `FR-EXT-023`, `NFR-EXT-WEBIQ-001`, `NFR-EXT-WEBIQ-002`
(see [PRD](../PRD.md) §7). Reuses `FR-EXT-015/017/019/020`, `FR-EXT-GOV-001`,
`NFR-EXT-PLG-001/002`, `NFR-EXT-GOV-001/002`, `FR-SIG-003/004/007/009/010`, `NFR-SIG-001`.

## 4. Milestones

- **M0 — Governance:** ADR-0060 + `DC-EXT-SIGNAL-v1` v1.1.0 + new FR/NFR IDs.
- **M1 — Provider plugin:** `webiq/` manifest + simulator + parse + gated live-adapter (TDD).
- **M2 — Pipeline wiring:** auto-discovery + data-quality gate + Trust-B triage guard.
- **M3 — App surface:** model + fixtures + Web IQ card + Trust-B badge + web-citation affordance.
- **M4 — Recommendation glue:** display-only corroboration helper + HITL promote-to-watch.
- **M5 — signal-agent intake evidence:** channel-readiness scorecard on the curated simulator feed.
- **M6 — Verify + document:** full suite green, lint, PRD traceability consistent.

## 5. Definition of Done

- All new + existing signal tests green (`data-platform/scripts/external-signals`).
- App typecheck + unit suite green (Web IQ fixtures, corroboration, golden parity).
- `DC-EXT-SIGNAL-v1` v1.1.0 backward-compatible (existing records still validate).
- Trust-B guard proven: a Web IQ signal never fires a trigger.
- Live binding remains disabled by default; no external network calls in CI.
- Docs versioned per §9; PRD §7 traceability consistent.

## 6. Deployment & live-activation status (2026-08-12)

The provider-runner was deployed to both environments this session (each gated by
`approved-to-apply`), moving Web IQ from a build artefact to a running channel.

### Live and proven

- **SIT** — `ca-signal-runner-ihzhhpf-sit` (in `cae-sim-ihzhhpf-sit`) on the real
  `signal-runner:f821621` image, `webiqEntraEnabled=true`,
  `signalResidency=demo-westus2`. Keyless managed-identity token acquisition + Event
  Hub publish proven; `IncomingMessages` on `evh-ihzhhpf-sit-y26y/events` = **21
  messages** across two 900 s cycles.
- **PROD** — `ca-signal-runner-ihzhhpf-prod` (in the VNet-integrated
  `cae-ihzhhpf-prod`) on the same image imported to `crihzhhpfprod`,
  `signalResidency=CH` (the PROD Event Hub is genuinely `switzerlandnorth`). Logs
  show **11 records/cycle** to `evh-ihzhhpf-prod-i62t/events` via keyless MI.
- Two deploy blockers were fixed en route: the root `.dockerignore` allowlist
  (`fix(ci)` `f821621b`) and MI-based ACR pull in the provider-runner Bicep
  (`feat(infra)` `6a020afb`).

### Pending (tomorrow's restart)

1. **Web IQ content is still `simulated`** in both environments — the live binding
   falls back because the runner UAMI client id is not yet bound in the Web IQ portal.
   Bind (Profile Management → Application (Client) IDs): **SIT
   `cfc3f90d-6536-4a91-b070-0af1e7daee97`**, **PROD
   `5800b7e0-ad87-4f32-b414-56ce139d2213`**. Data-owner/portal action; flips to live on
   the next cycle with no redeploy.
2. **Downstream is not wired to the live stream (open finding).** Events land in the
   Event Hub, but there is no `es-ihzhhpf-events` Eventstream / Eventhouse
   `ExternalSignal` route deployed (gated by
   [ADR-0060](../adr/0060-webiq-external-signal-channel.md) live gate +
   [ADR-0014](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md)); the
   `external-signals` medallion notebooks read the synthetic `signals_synth` seed, not
   the Event Hub; and the app `SignalsPanel` renders the Web IQ tile from static demo
   data (`occupancy-data.ts`). So live envelopes are provably in the Event Hub but do
   **not** yet reach a Fabric table or the app.
3. **Observability gap:** `providers/runner.py` `run_provider` swallows the
   live-binding exception on fallback, so a live 401 (identity-not-bound) is invisible.
   A one-line `logger.warning` with the reason is the recommended first step tomorrow.

### Decision needed before further work

To make live events visible in Fabric + the app, pick the depth: (a) build/ungate the
`es-ihzhhpf-events` Eventstream → Eventhouse route, or (b) repoint the bronze medallion
notebook at the Event Hub (or its Capture); (c) wire `SignalsPanel` to the live
Gold/semantic model; plus (d) the portal binding above. Paths (a)/(b) touch the ADR-0014
GA gate and PROD data, so they were deliberately not done autonomously.

> Note: the shipped provider directory is `providers/webiq/` (hyphen-free
> `sourceId: webiq`, required by `import_module`), not the `microsoft_webiq/` name used
> in the planning specs.
