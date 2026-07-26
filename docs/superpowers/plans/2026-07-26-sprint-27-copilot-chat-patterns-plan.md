# Sprint 27 — Copilot Chat Response Patterns + Polish Loop

| Field | Value |
|-------|-------|
| **Version** | 1.3.0 |
| **Date** | 2026-07-26 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | Draft |
| **Previous Version** | 1.2.0 (A12 follow-up chips delivered) |
| **Sprint** | 27 (Curavias App UX Polish, tracker #365) |
| **Applies to** | `apps/hcc-app-fluent` Copilot pane (`copilot-drawer/**`, `copilot-rail/**`) |
| **Related** | [IQ data-access pattern](../../architecture/app-iq-data-access-pattern.md), [Fabric to Foundry grounding contract](../../architecture/fabric-foundry-grounding-contract.md), [ADR-0033](../../adr/0033-fabric-data-agent-as-foundry-grounding-tool.md), [ADR-0044](../../adr/0044-app-data-access-via-iq-layer.md); chat-artefact rendering commit `302f679` |

> Goal: a **reusable catalogue of Copilot chat response artefacts** (identified
> from the simulated mockup) that every Foundry-agent reply renders through, and a
> **fine-tuning loop** (Step 1 → 2 → 3, loop 2↔3 until convinced) to validate and
> refine them against real live agent responses.

## 0. Where we are

The mockup established a rich **proactive reco** artefact ([`RecoPanel`](../../../apps/hcc-app-fluent/src/copilot-rail/RecoPanel.tsx) over
[`GroundedReco`](../../../apps/hcc-app-fluent/src/copilot-rail/reco.ts)); commit `302f679` made
**conversational replies** render through the same block stack (a Foundry
structured reply's `reco` renders as artefacts, not a flat text bubble). This doc
formalises that vocabulary as the standard pattern set and the loop to fine-tune
it.

Data path: replies come through the IQ gateway (ADR-0044) — Foundry agent host
(`VITE_AGENT_HOST_URL`) primary; a deterministic grounded **mock** when the host
is unconfigured (dev/CI). Live validation (Step 3) requires the agent host wired.

## 1. Step 1 — Identify + define the design-pattern artefacts

The response is an **ordered stack of typed artefact blocks**, not a paragraph.
Each block below maps to a `GroundedReco` field already rendered by `RecoPanel`,
so the catalogue is a formalisation, not an invention.

| # | Artefact | Context (when / what it conveys) | Action | Source field | Fluent primitive |
|---|----------|----------------------------------|--------|--------------|------------------|
| A1 | **Agent attribution** | Which agent answered + its side-effect ceiling + provenance (live/simulated). Trust anchor, per-message. | none (metadata) | `agentLabel` + ceiling + provenance | `CopilotIcon` + `Body1` + `Badge` |
| A2 | **Context chip** (situation pill) | What the reply is about: subject · qualifiers · status, RAG-toned. | (future) focus/filter | `contextChip` | `RagBadge` / `chipBadgeColor` |
| A3 | **Grounded read** (narrative) | The 1–2 sentence plain-language answer. The only free-text block. | none | `read` | `Body1` |
| A4 | **Metric trio** (now → forecast → gap) | The numbers behind the read (e.g. 81% → 93% → −16). | (future) drill | derived / payload | `ds` stat row + RAG delta |
| A5 | **Lever list** (ranked options) | The signature artefact: numbered options each with an impact delta (−6 beds). | select a lever (future: act/expand) | `levers[]` + `impact` | `CounterBadge` + `Body2` + impact `Badge` |
| A6 | **Projection** (before → after) | Expected outcome if the lever/CTA is taken (102% → 94%). | none | `projection` | `Caption1` |
| A7 | **Primary CTA + approval gate** | The recommended action + kind (handoff/action/navigate) + HITL approval-required gate + hint; disabled refused state. | click → handoff / action / navigate (gated by `approved-to-apply`) | `primaryCta` + `requiresApproval` | `Button` + gate `Badge` + `Caption1` |
| A8 | **Handoff baton** | Cross-agent continuity ("carried from ooa → dca"). | follow the handoff | `primaryCta.kind='handoff'` + `target` | inline chip / `ArrowRight` |
| A9 | **Signal / evidence list** | What feeds the answer: leading icon + RAG + provenance flask. | (future) inspect signal | signals payload | icon + `RagBadge` + provenance icon |
| A10 | **Citation footer** | Grounding evidence — `hcp:*` / `gold.*` source pills (no-fabrication rule). | (future) open source | `citations[]` | source pills (`Caption1`, `data-testid="citations"`) |
| A11 | **Refusal / guardrail** | Why the agent will not act (HITL gate blocked / policy). | none (blocked) | `refused` | `Badge color="danger"` + reason |
| A12 | **Follow-up prompts** (chips) | Suggested next asks. Starter chips (board-level) before a conversation; per-reply "what next" chips under the latest agent answer. | click → send prompt | `GroundedReco.followUps` (per-reply) + board `askAbout` (starter) | `InteractionTag` |
| A13 | **Evidence popover** (on impact badge) | Hover/focus an impact badge → why-summary + context/impact detail + citations. Responsible UI: understand before acting. | hover/focus → popover | `RecoLever.evidence` | `Popover` + `Badge` |
| A14 | **People popover** (staffing) | Who is affected/involved — roster names + role + shift. Specialisation of A13. | hover/focus → popover | `RecoLever.evidence.people` | `Popover` + `Badge[]` |
| A15 | **External-action trigger** (Work IQ) | Action *outside* the platform with clear context (Teams call, email draft, downstream EPIC/KIS/SAP invoke-draft). Design-only for now. | click → Work IQ action (HITL-gated, draft first) | `RecoCta` + Work IQ | `Button` + Work IQ |

### Message composition grammar (fixed order for scan consistency)

```text
AgentMessage =
  A1 header
  → [A2 context chip]
  → A3 read
  → [A4 metric trio]
  → [A5 lever list]
  → [A6 projection]
  → [ A7 CTA + gate  |  A11 refusal ]
  → [A8 handoff baton]
  → [A9 signal/evidence]
  → [A10 citations]
  → [A12 follow-ups]
```

A plain informational reply = `A1 + A3 + A10`. A recommendation lights up the full
stack. Same renderer, same tokens, same a11y — so all agents inherit it.

### Cross-agent applicability

| Agent | Ceiling | Typical stack |
|-------|---------|---------------|
| `ooa` | read | A2 · A4 · A5 · A6 · **A8** CTA |
| `bmca` | write | A2 · A5 · **A7 gated** |
| `dca` | write | A2 · A4 · A5 · A7 |
| `orsa` | write | A5 · A6 · **A7 gated** |
| `sba` | write | A4 · A5 · A7 |
| `csa` | deploy | A2 · A5 · **A7 deploy-gated** · A11 |
| `data-quality` | write | **A9** · A11 · A10 (no CTA) |

## 2. Step 2 — Refine (polish) each artefact until UX-convinced

For every artefact A1–A12, iterate on the running app + the `/brand` gallery until
it meets the acceptance bar. Per-artefact checklist:

1. **Fidelity** to the mockup (spacing, tone, iconography via `ds` tokens; brand RAG colours; dark text on green/amber).
2. **A11y** — role/aria, icon-only blocks carry `aria-label`; AA contrast; keyboard reachable.
3. **i18n** — block labels via `t()`; grounded numbers pass through untranslated.
4. **Governance** — A7 shows the approval gate for `deploy`/`write`; A11 propagates refusals verbatim; A10 always present for grounded answers.
5. **Provenance** — live vs simulated always visible.

Polish surface: add a **"Chat response artefacts" section to `/brand`** rendering
each block with sample data, so we can eyeball + axe-scan them in isolation.

**Gate:** UX sign-off per artefact. If not convinced, keep iterating in Step 2.

## 3. Step 3 — Validate against real live Foundry-agent responses

Prerequisite: `VITE_AGENT_HOST_URL` wired to the eastus2 Foundry agent host
(ADR-0032). Then, for a set of real asks:

1. Send a real ask (e.g. "Welche Stationen kippen in 72h?", "Wie ist die Auslastung auf Station B?").
2. Capture the live `GroundedReply` (answer + citations + `reco`).
3. **Map** the response onto the A1–A12 catalogue: which blocks does it populate?
4. **Score**: (a) does every claim carry an `hcp:*`/`gold.*` citation? (b) is the HITL gate present for side-effecting CTAs? (c) do refusals propagate verbatim? (d) any content that does NOT fit an existing artefact?
5. **Outcome:**
   - All content maps + renders well → validated.
   - New content shape found (no artefact fits) → **loop back to Step 2**: define/refine an artefact, polish it, then re-run Step 3.

Capture each validated ask/response as a **golden fixture** (input ask → expected
artefact stack) so regressions are caught.

## 4. The loop

```mermaid
flowchart LR
  S1[Step 1 define catalogue] --> S2[Step 2 polish each artefact]
  S2 --> S3[Step 3 validate vs live Foundry]
  S3 -->|convinced| DONE[fine-tuned]
  S3 -->|new/needs work| S2
```

## 5. Test protocol (prepared asks)

| # | Ask | Expected artefact stack | Key assertions |
|---|-----|-------------------------|----------------|
| T1 | "Welche Stationen kippen in 72 h?" | A1 · A2(OVER) · A3 · A5 · A6 · A10 | ≥1 `hcp:*` citation; RAG tone = over |
| T2 | "Wie ist die Auslastung auf Station B?" | A1 · A2 · A3 · A7(approval) · A10 | HITL gate visible; no PHI; citations `gold.*` |
| T3 | "Verlege 2 Betten in die Notaufnahme" (side-effecting) | A1 · A3 · A7(approval) or A11 | CTA gated by `approved-to-apply`, or refusal propagated verbatim |
| T4 | An ask the agent must refuse | A1 · A11 · A10 | refusal verbatim; no chat-model fallback |

## 6. Step-2 additions (2026-07-26)

### Evidence popover (A13 / A14) — delivered

Hovering or focusing a lever's impact badge (e.g. `-6 Betten`, `+2 FTE`, `0.5 FTE`)
opens a popover with the grounding behind the number: a why-summary, context /
impact detail, **affected people** (the staffing roster, A14), and `hcp:*` /
`gold.*` citations. Responsible UI — the user decides and approves on a clear
understanding of context and who is involved. Delivered in `RecoPanel` via
`RecoLever.evidence`; the trigger is keyboard-reachable (focus opens it too).
Populated on occupancy (evidence) and staffing (people) levers, chat + board.

### External-action triggers via Work IQ (A15) — design only

When a lever / CTA implies an action **outside** the platform with a clear action
context, the CTA routes to a **Work IQ** trigger, HITL-gated (`approved-to-apply`)
and **draft-first** (nothing is sent/executed until the human reviews the draft):

- **Teams call** — initiate a call to the responsible person / role (e.g. ICU charge nurse).
- **Email draft** — draft an email to the affected team (recipients from the A14 roster people).
- **Downstream service** — invoke an action *draft* in EPIC / KIS / SAP via a custom Work IQ service.

UX contract: `action context -> Work IQ trigger -> HITL approve -> draft -> send`.
The CTA shows the destination + a "draft only" affordance; execution is gated.
Implementation is deferred to a dedicated sprint — this entry fixes the UX pattern.

### Follow-up prompts (A12) — delivered

Every grounded reply can carry `GroundedReco.followUps` — contextual "what next"
prompts rendered as `InteractionTag` chips **under the latest agent answer only**
(history stays uncluttered; the chips always reflect the current answer). Clicking
a chip sends it as the next ask, so the conversation advances without retyping.
The board-level `askAbout` chips now act as **starter** suggestions shown only
before a conversation begins (`turns.length === 0`); once the exchange starts,
per-reply follow-ups take over. Populated per role agent (ooa/bmca/dca/orsa/sba/csa)
with grounded, PHI-free prompts. Delivered in `ConversationView` (fed by
`AgentPlane` + the Copilot `Drawer` via `onFollowUp`); the chips are keyboard
reachable. Covered by `tests/unit/follow-ups.test.tsx` (render + last-turn-only +
click-to-send + per-agent coverage).

### Metric trio (A4) + guardrail refusal (A11) — delivered

**A4** — `GroundedReco.metrics` renders a **now → forecast → gap** stat row in
`RecoPanel` (arrow-separated cells; the gap cell is RAG-toned via
`impactBadgeColor`). Populated per role agent with grounded values (e.g. occupancy
`96% → 102% → -6 Betten`, staffing `6.5 → 5.0 → -1.5 FTE`). Sits between the read
(A3) and the lever list (A5) per the composition grammar.

**A11** — the dev/CI mock (`invokeAgent`) now returns a **verbatim guardrail
refusal** for a destructive / no-approval ask (HITL-02 gate) or a PHI request
(PHI-Gate): a `blocked` context chip, red refusal read, refused badge, **no
levers, no CTA**, and a policy citation. Happy-path recos are unaffected (the
triggers are narrow). Covered by `tests/unit/agent-recos.test.ts` (metric trio +
destructive refusal + PHI refusal + never-refuse-normal) and
`tests/unit/reco-panel.test.tsx` (metric-trio render).

### `/brand` chat-artefacts gallery (A1–A14) — delivered

The dev-only `/brand` design-system route gained a **Chat response artefacts**
section: a *Recommendation* card (a `ConversationView` turn rendering A1–A10 +
A12 + A13/A14 in one stack) and a *Guardrail refusal* card (A11). English sample
data, isolated so we can eyeball + axe-scan each block. The axe suite
(`tests/e2e/a11y.spec.ts`) now scans `/brand` at WCAG 2.1 AA (0 serious/critical);
`tests/unit/brand-gallery.test.tsx` asserts the metric trio, follow-ups, and the
no-lever refusal render.

## 7. Definition of done

- [ ] Catalogue A1–A12 rendered by a single shared `AgentMessage`/`RecoPanel` renderer (Step 1).
- [x] `/brand` "Chat response artefacts" section renders every block; axe-clean (Step 2).
- [ ] Each artefact passes its Step 2 checklist with UX sign-off.
- [ ] Step 3 run against live Foundry responses for T1–T4; each maps to the catalogue; new shapes fed back to Step 2.
- [ ] Golden fixtures for T1–T4 (ask → expected artefact stack).
- [ ] No PHI; provenance + citations always visible; governance gates enforced.
