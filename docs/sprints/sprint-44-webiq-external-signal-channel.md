# Sprint 44 — Microsoft Web IQ as a Governed External Signal Channel

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-08-12 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Complete (all milestones + follow-ups A–D shipped and pushed to `main`) |
| **Previous Version** | 1.0.0 (initial sprint page, implementation in progress); this bump records completion incl. Q1 hospital-service hazard scoping, corroboration + promote-to-watch wiring, i18n, golden task, and channel-readiness scorecard |
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
