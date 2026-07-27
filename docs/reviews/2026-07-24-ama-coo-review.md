# Review Report — Curavias Showcase Interview with COO (customer side) (2026-07-24)

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Datum** | 2026-07-27 |
| **Autor** | @urruegg |
| **Status** | Draft |
| **Previous Version** | 1.0.0 (added Sprint 30 closed-loop-learning alignment) |
| **Intake-Kind** | `session` (moderated showcase interview, originally German) |
| **Source** | [`2026-07-24-ama-coo-review-transcript-summary.md`](2026-07-24-ama-coo-review/2026-07-24-ama-coo-review-transcript-summary.md) (anonymised, normalised meeting notes; raw Teams-AI notes + VTT transcript retained locally only, not committed, as they carry the participant name) |
| **Discovered Ideas** | [`Sprint-Signal-and-DataQuality-Agents.md`](2026-07-24-ama-coo-review/Sprint-Signal-and-DataQuality-Agents.md) (Signal Agent + Data Quality Agent) |

> Produced by the [`review-session-agent`](../../agents/review-session-agent/AGENT.md) following the
> structure in [`docs/reviews/README.md`](README.md) § *Minimum Review Report Structure*.
>
> **Anonymisation note:** Participant names have been replaced throughout with
> **role designators** (same convention as the 2026-06-09 reviews). The customer's
> operational leadership is referred to as **COO**; the presenting/moderating side
> as **@urruegg**. Commercial product and system names (Epic, Polypoint,
> Microsoft 365) are public references and remain unchanged. The working title
> "Guravias" from the raw transcript is a neutral placeholder and is referred to
> here as **Curavias**.

---

## 1. Session Metadata

| Field | Value |
| ----- | ----- |
| Session date | 2026-07-24 |
| Duration / format | Moderated showcase interview, German |
| Location | Microsoft Technology Center (Innovation Hub), Zurich |
| Participants (customer side) | **COO** (operational leadership) |
| Participants (our side) | **@urruegg** (moderation, Solution Owner / solution architecture) |
| Objective | Present the Curavias approach (AI agents + metadata for capacity planning without transferring PHI to the cloud) and gather an operational reality-check from the hospital's perspective |

---

## 2. Inputs Reviewed

1. **Meeting notes** (primary source) — anonymised, normalised Teams AI transcript incl. follow-up tasks (see the transcript summary; the raw notes + VTT are kept local only).
2. **Raw transcript (VTT)** — verbatim transcript of the showcase interview, used locally as the basis of the anonymisation; **not committed** (carries the participant name).
3. **Discovered-ideas document** — [`Sprint-Signal-and-DataQuality-Agents.md`](2026-07-24-ama-coo-review/Sprint-Signal-and-DataQuality-Agents.md): proposal for two new agents (**Signal Agent / SGA** and **Data Quality Agent / DQA**) with `FR-SIG-*` / `FR-DQA-*` requirements and new data contracts (`DC-REF-CERTIFICATION-v1`, `DC-DQ-TRUSTSCORE-v1`, `DC-DQ-GAP-v1`).
4. **Repository baseline** — `docs/PRD.md`, `agents/*/AGENT.md`, `docs/adr/0007` (HITL), `docs/adr/0016` (no PHI), `docs/BVA.md`, existing external-signal work (`DC-EXT-SIGNAL-v1`, [`signal-triage-agent`](../../agents/signal-triage-agent/AGENT.md), [`data-quality-agent`](../../agents/data-quality-agent/AGENT.md)).

---

## 3. Outcome Summary (the three key points)

1. **Approach confirmed, data quality flagged as the critical path.** The COO confirms the metadata / deep-link approach (no PHI in the cloud) as viable, but names **data quality** and the **human factor** (acceptance, training, change management) as the actual success-or-failure factors — not the technology.
2. **Integration reality is differentiated.** Interfaces are heterogeneous: **Epic** offers good APIs, **Polypoint** (staff rostering) is hard to integrate. The business case (publicly available hospital data, 3 hospitals / different cantons, target **OR utilisation ≥ 85 %**, 2 people / 90 days) is plausible; implementation typically fails on IT resources, cost and data quality.
3. **Follow-up agreed.** (a) Clarify whether, under **NDA**, work instructions / job descriptions from the departments can be made available for agent fine-tuning; (b) identify the right internal contact / office to formally initiate the document sourcing.

> **Key outcome (design consequence):** The central finding — *data quality is the
> single point of failure* — is directly addressed by the two **discovered ideas**:
> a **Data Quality Agent (DQA)** that proactively detects gaps, scores them (Trust
> Score) and routes them to data owners for remediation, plus a **Signal Agent
> (SGA)** that controllably onboards missing golden-source channels (e.g.
> certification / competency registries). Together they form a closed loop (*DQA
> finds → SGA onboards → DQA re-scores*), turning the quality weakness named by the
> COO into a measurable, self-healing golden-source layer.

---

## 4. Key Findings

### 4.1 Privacy and integration model holds up

* **Metadata-only + deep link.** Matching and planning run exclusively on metadata; patient data stays in the local KIS and is only referenced via deep link. Consistent with `docs/adr/0016` (no PHI in the cloud) and the metadata architecture.
* **Competency matching from M365.** Competency information already stored in Microsoft 365 / Office is used for staff assignment — a pragmatic, already-available data point.
* **Heterogeneous interfaces.** Epic offers good APIs; Polypoint (staff rostering) is hard to integrate. **Consequence:** the integration roadmap must treat Polypoint as a risk path with a fallback (e.g. export / manual attestation), not as a self-evident API connection.

### 4.2 Data quality + human factor = the critical path

* **Data quality as an acceptance lever.** Insufficient data quality causes reports/analyses to be **rejected** and systems to be used only in a limited way — a self-reinforcing negative loop.
* **Proactive quality checking wanted.** The COO welcomes agents that **proactively** flag erroneous/missing data and prompt the responsible people to remediate — exactly the DQA concept.
* **The human decides.** Willingness, training and acceptance remain decisive; even experienced staff revert to traditional ways of working when overwhelmed (Epic, M365). Confirms the **advisory-only + HITL** posture (`docs/adr/0007`).
* **Relief as the value promise.** Delegating routine tasks to agents should free clinical staff for direct patient care.

### 4.3 Business case and economics

* **Public data basis.** Business case built on publicly available hospital data; 3 hospitals from different cantons analysed to cover regulatory differences and scalability.
* **Target figures.** OR utilisation **≥ 85 %** with minimal waiting times; the biggest challenge is the **emergency department** (no beds explicitly held free).
* **Implementation proposal.** 2 internal people / 90 days; main cost is staff effort. Typical failure causes: lack of IT resources, high implementation cost, poor data quality.

### 4.4 Scenario and crisis simulation confirmed

* The presented **scenario agent** (what-if / crisis cases such as outages, staff shortages) meets a clear need. Consistent with the existing `csa-agent` (Crisis/Scenario) and its Prepare/Run/Evaluate/Recommend cycle.

### 4.5 Discovered ideas — Signal Agent (SGA) & Data Quality Agent (DQA)

Derived from the session and worked out in the discovered-ideas document — designed as **advisory, HITL, GA-only**:

* **Data Quality Agent (DQA):** continuous assessment of the gold/serving layer, gap detection with impact quantification, a **Trust Score** per domain (`DC-DQ-TRUSTSCORE-v1`), owner-routed remediation (`DC-DQ-GAP-v1`) and grounding-readiness certification behind the GA gate. Directly addresses the COO's core point of "data quality as the single point of failure".
* **Signal Agent (SGA):** a controlled lifecycle for external signal channels (discover → classify → adapter → contract → ontology → test → activate), flagship example **certification register → skills/competency baseline** (`DC-REF-CERTIFICATION-v1`). Connects to the competency matching mentioned in the session and to the existing external-signal work (`DC-EXT-SIGNAL-v1`, `signal-triage-agent`).
* **Closed loop:** DQA states *what* is missing and *why it matters*; SGA supplies the *how* (the channel); DQA re-scores and certifies grounding readiness — a measurable, self-healing golden-source layer.

---

## 5. Gaps and Risks

| # | Gap / risk | Impact | Reference |
| - | ---------- | ------ | --------- |
| G1 | **Polypoint integration** hard/costly | Staffing-planning slice (SBA) blocked or delayed | §4.1 |
| G2 | **Data quality** currently insufficient | Acceptance + usage decline; reports discarded | §4.2 / DQA |
| G3 | **Change management & training** under-resourced | Adoption fails despite content quality | §4.2 |
| G4 | **NDA access** to work instructions / job descriptions unresolved | Agent fine-tuning stays generic without real process documents | Follow-up |
| G5 | **Internal ownership** for document sourcing unclear | Formal sourcing chain missing | Follow-up |
| G6 | **Certification / competency register** machine-readable + licensable? | SGA flagship (skills baseline) blocked | DQA/SGA doc G1 |
| G7 | **Emergency capacity** (no beds held free) | Hardest optimisation case; model must carry uncertainty | §4.3 |

---

## 6. Recommendations / Next Actions

1. **Prioritise DQA as the next MVP slice.** The quality weakness named by the COO is the biggest value lever. Publish a Trust Score for ≥ 1 gold domain, route one gap to a named owner and close it (discovered-ideas §6.4). Governance ADR (trust-score model + thresholds) in parallel.
2. **Set up the SGA worked example "certification register → skills baseline".** One channel end-to-end (`DC-REF-CERTIFICATION-v1`), HITL approval + provenance, pseudonymised work ID (do not treat staff PII as "non-PHI"). Define the integration seam to DQA (`DC-DQ-GAP-v1` "new-source-needed") first.
3. **Differentiate the integration roadmap.** Epic as API-first; document **Polypoint as a risk path** with a fallback (export / manual attestation) — do not plan it as a self-evident connection.
4. **Include a change-management / training track** explicitly in the offering (adoption, role onboarding, minimally invasive UX) — technology is not the bottleneck.
5. **Drive the follow-ups.** (a) NDA clarification for work instructions / job descriptions; (b) identify the right internal contact / office for official document sourcing. Both are prerequisites for agent-specific fine-tuning.
6. **Harden the business case.** Underpin the ≥ 85 % OR-utilisation target and the emergency special case (no free beds) with a forecast backtest harness to quantify the real effect of closing a data gap (discovered-ideas G4).

---

## 7. Artefact Traceability

| Session point | Repository artefact | Status |
| ------------- | ------------------- | ------ |
| No PHI in cloud / metadata-only | `docs/adr/0016`, metadata architecture | Confirmed |
| Advisory-only + HITL | `docs/adr/0007`, `agents/*/AGENT.md` | Confirmed |
| Proactive data-quality checking | [`data-quality-agent`](../../agents/data-quality-agent/AGENT.md) + DQA proposal (`DC-DQ-TRUSTSCORE-v1`, `DC-DQ-GAP-v1`) | Extension proposed |
| External signals / competency register | [`signal-triage-agent`](../../agents/signal-triage-agent/AGENT.md), `DC-EXT-SIGNAL-v1` + SGA proposal (`DC-REF-CERTIFICATION-v1`) | Extension proposed |
| Scenario / crisis simulation | [`csa-agent`](../../agents/csa-agent/AGENT.md) | Confirmed |
| Business case / economics | `docs/BVA.md` | Reconciliation recommended |
| New requirements (SGA/DQA) | `FR-SIG-*` / `FR-DQA-*` → `docs/PRD.md` §7 | Open (sprint intake) |

---

## 8. Requires Validation

* **NDA document access** (work instructions, job descriptions) — open (follow-up, customer side).
* **Internal sourcing ownership** — right contact / office still to be identified.
* **Polypoint integration effort** — technical feasibility + fallback to be verified.
* **Certification register** — machine-readability + production licence (SGA flagship).
* **Forecast backtest harness** — does not yet exist; needed to quantify the impact of data gaps.
* **Foundry IQ Swiss-region GA** — scope + date open; grounding-readiness certification behind the GA gate.

---

## 9. Alignment with the closed-loop learning (Sprint 30)

The closed loop confirmed in this session (DQA finds → SGA onboards → DQA
re-evaluates) is the **data-quality twin** of a second, complementary loop that the
[Sprint 30 design](../superpowers/specs/2026-07-27-sprint-30-closed-loop-learning-foundation-design.md)
establishes: an **agent-quality loop** (Capture → Evaluate → Curate → Improve →
HITL approval). The two loops interlock:

* **DQA trust score as an evaluation input signal.** Groundedness and
  citation-coverage scores of agent answers depend directly on data quality — so
  the DQA trust score (`DC-DQ-TRUSTSCORE-v1`) becomes an input signal to agent
  evaluation, and the agent loop's uncited-claim findings feed the DQA/SGA backlog
  in return.
* **Agent fine-tuning = the Improve stage (newly in Sprint 30 scope).** The
  follow-up „work instructions / job descriptions under NDA for agent
  fine-tuning" (§3.3 / §5 G4 / §6.5 / §8) is exactly the fuel for the **Improve
  stage** — knowledge refresh + fine-tune (SFT/DPO/RFT) — now in scope for
  Sprint 30: advisory, HITL, offline-regression gate + `approved-to-apply`.
* **Forecast backtest harness = evaluation harness.** The backtest harness flagged
  as missing in §8 is the same evaluation infrastructure Sprint 30 builds (`evals/`
  extended with online + offline scoring for groundedness, citation coverage,
  refusal correctness).

**Consequence.** The two loops should be governed as **one** pattern: the
data-quality loop (DQA/SGA) secures the *foundation*, the agent-quality loop
(Sprint 30) secures *answer quality and continuous improvement* — both advisory,
HITL, and `approved-to-apply`.

### 9.1 Traceability addendum

| Session point | Repository artefact | Status |
| ------------- | ------------------- | ------ |
| Agent quality / continuous improvement | [Sprint 30 design](../superpowers/specs/2026-07-27-sprint-30-closed-loop-learning-foundation-design.md) (`FR-LEARN-*`) | Newly proposed |
| Agent fine-tuning (NDA documents) | Sprint 30 Improve stage (knowledge refresh + fine-tune SFT/DPO/RFT) | Interlocked |
| Forecast backtest harness | Sprint 30 evaluation harness (`evals/`) | Converging |
