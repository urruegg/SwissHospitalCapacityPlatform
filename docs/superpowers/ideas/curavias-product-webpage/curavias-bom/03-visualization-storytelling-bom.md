# Step 3 — Visualization & Storytelling Artefact BOM

**Basis:** the Curavias flyer (`Curavias-Produktuebersicht-DE.pdf`) + the
**patient journey (KEPT as-is)**. This BOM enumerates every visual asset and idea
needed to tell the Curavias story across the app and website: **product design,
architecture, product team (incl. GitHub agents), demo organisation/hospitals, and
reviews.**

**Legend — Format:** SVG (scalable, preferred for diagrams/icons) · PNG (raster) ·
MP4 (video) · Interactive (in-app component). **Origin:** Recreate (from flyer) ·
Generate (AI image) · Brand Central (Microsoft asset) · Data-driven (from repo).

---

## 3.1 Product design visuals

| ID | Visual artefact | Description | Format | Origin | Priority |
| -- | --------------- | ----------- | ------ | ------ | -------- |
| VIZ-PD-01 | **Curavias logo lockup** | Patient-path mark + wordmark + "Swiss Hospital Capacity Copilot" + tagline | SVG | Recreate | P0 |
| VIZ-PD-02 | Logo variants | Horizontal, stacked, mark-only, mono, reversed (dark bg) | SVG | Recreate | P0 |
| VIZ-PD-03 | **"Die drei Erlebnisse" triptych** | 3 tiles: Copilot-Drawer · Whiteboard · Human-in-the-Loop | SVG/PNG | Recreate | P0 |
| VIZ-PD-04 | Copilot-Drawer mockup | "Wo baut sich morgen Druck auf?" → 3 stations, 3 candidates, grounded answer + "mit Quelle" | PNG/Interactive | Recreate | P0 |
| VIZ-PD-05 | Whiteboard mockup | Live command-center KPI cards (94 % · +3 · 12 · OK) per role | PNG/Interactive | Recreate | P0 |
| VIZ-PD-06 | HITL approval mockup | "Freigabe erforderlich" checkmark shield, action log | PNG | Recreate | P0 |
| VIZ-PD-07 | Colour & type style tile | Brand palette (teal/green + MS blue + Swiss red), Segoe UI scale | SVG | Recreate | P1 |
| VIZ-PD-08 | UI kit / component sheet | Buttons, cards, tables, badges in Curavias theme | Figma/SVG | Generate | P1 |

---

## 3.2 Patient-journey visuals (KEEP)

| ID | Visual artefact | Description | Format | Priority |
| -- | --------------- | ----------- | ------ | -------- |
| VIZ-PJ-01 | **Curavias Patienten-Pfad — hero infographic** | Full path: Notfall→Bettenzuweisung→OP→Pflege&Personal→Entlassung→Erfolg, with role + agent under each node | SVG (scalable) | P0 |
| VIZ-PJ-02 | Cross-cutting lanes overlay | CSA (Krisen & Szenarien) + DQ (Datenqualität/Gates) spanning the path | SVG | P0 |
| VIZ-PJ-03 | HITL governance band | "Der Mensch entscheidet" band beneath path | SVG | P0 |
| VIZ-PJ-04 | Interactive journey (web) | Hover/click each phase → agent detail popover | Interactive | P1 |
| VIZ-PJ-05 | Animated journey (hero) | Node-by-node reveal of patient path, ~20–30 s | MP4 | P1 |
| VIZ-PJ-06 | Per-phase node icons (6) | Notfall (pulse), Bett (bed), OP (scalpel), Personal (people), Entlassung (home), Erfolg (check) | SVG | P0 |

---

## 3.3 Architecture diagrams

| ID | Diagram | Source | Format | Priority |
| -- | ------- | ------ | ------ | -------- |
| VIZ-AR-01 | Layered architecture (7 layers) | ARCHITECTURE §Layered View | SVG (mermaid→export) | P0 |
| VIZ-AR-02 | Component topology (Identity / Core / Security-governance) | ARCHITECTURE §Component Topology | SVG | P0 |
| VIZ-AR-03 | End-to-end flow (source→normalize→forecast→serve→orchestrate→writeback→trace) | ARCHITECTURE §E2E Flow / SD §E2E | SVG | P0 |
| VIZ-AR-04 | CI/CD promotion flow (PR→CI what-if→SIT→Gate→PROD→Evidence) | ARCHITECTURE mermaid / README | SVG | P0 |
| VIZ-AR-05 | Network hub-spoke + private endpoints | SECURITY §Network | SVG | P1 |
| VIZ-AR-06 | Bronze→Silver→Gold data pipeline + PHI gates | Flyer + SECURITY data-plane | SVG | P0 |
| VIZ-AR-07 | Fabric-to-Foundry grounding seam (Data Agent → copilots) | PRD FR-ONT-008, ADR-0033 | SVG | P1 |
| VIZ-AR-08 | Swiss residency / region map (CH North + West failover) | ARCHITECTURE §Residency | SVG/PNG | P1 |
| VIZ-AR-09 | Zero Trust layered-controls diagram | SECURITY §Layered Pattern | SVG | P1 |
| VIZ-AR-10 | Ontology stack (reference OWL/RDF ↔ operational Fabric IQ ↔ FHIR/SNOMED crosswalk) | PRD §Ontology | SVG | P2 |

---

## 3.4 Product-team & AI-agent visuals

### 3.4.a The seven Curavias product agents (customer-facing)

| ID | Visual artefact | Description | Format | Priority |
| -- | --------------- | ----------- | ------ | -------- |
| VIZ-AGT-01 | Seven-agent card set | One card per agent: name, code, role, delivers, HITL gate, icon | SVG/PNG | P0 |
| VIZ-AGT-02 | Agent icon family | BMCA (bed), OOA (pulse/forecast), DCA (home/handoff), ORSA (scalpel/OR), SBA (people), CSA (shield/crisis), DQ (gate/quality) | SVG | P0 |
| VIZ-AGT-03 | Agent-to-journey map | Which agent acts at which patient-path phase | SVG | P0 |
| VIZ-AGT-04 | HITL-gate matrix | Agent × gate (Bettenverlegung, Kapazität, Handoff, Slate, Personal, Politik, PHI) | SVG/table | P1 |

### 3.4.b Engineering / GitHub delivery agents (how it's built)

| ID | Visual artefact | Description | Source | Priority |
| -- | --------------- | ----------- | ------ | -------- |
| VIZ-TEAM-01 | GitHub-native delivery model diagram | Docs-first → agent workflows → evidence-in-release-path | README §Delivery Model | P1 |
| VIZ-TEAM-02 | Engineering-agent roster | GitHub Copilot coding agent (repo control-plane runtime, ADR-0001/0002) + agent registry (`AGENTS.md`) | AGENTS.md | P1 |
| VIZ-TEAM-03 | Sprint timeline / delivery trace | Sprints 02→16 milestone ribbon (infra baseline, onboarding, ontology, dashboards, CSA what-if) | repo commit history | P2 |
| VIZ-TEAM-04 | RACI incl. semantic/ontology owner | Governance roles incl. nominated ontology owner | OPERATIONS.md / FR-GOV-ONT-001 | P2 |
| VIZ-TEAM-05 | Human ↔ agent responsibility split | Deterministic service vs. agentic flow (advisory, HITL-gated) | SD §FR-ONB-004 | P1 |

---

## 3.5 Demo organisation & hospitals

| ID | Visual artefact | Description | Source | Priority |
| -- | --------------- | ----------- | ------ | -------- |
| VIZ-DEMO-01 | Demo-org chart | Synthetic MCAPS demo tenant, hospital org + 7 operational roles | Entra demo-org master data (ADR-0012) | P1 |
| VIZ-DEMO-02 | Demo hospital profiles | **Hirslanden** & **Zollikerberg** capacity profiles (specialty-tagged) | `DC-ONB-CAPACITY-*-v1`, SD.md | P1 |
| VIZ-DEMO-03 | Rollout-sequence graphic | USZ-first / LUKS-first patterns; one-provider-at-a-time | PRD FR-OM-003 | P1 |
| VIZ-DEMO-04 | Seven operational personas | Synthetic role personas (Bettenmanagement, Notfall-Leitung, OP-Koordination, Personalplanung, Entlassungskoordination, Krisen-Diensthabende, Data/Ontology Steward) | Flyer agent roles | P1 |
| VIZ-DEMO-05 | Synthetic demo scenario board | "Morgen baut sich Druck auf Station X auf" walkthrough (no PHI) | ADR-0016 demo scope | P1 |
| VIZ-DEMO-06 | Demo-scope / residency callout | westus2 demo vs. switzerlandnorth PROD, no-PHI-in-demo badge | ADR-0013/0016 | P2 |

---

## 3.6 Review & evidence visuals

| ID | Visual artefact | Description | Source | Priority |
| -- | --------------- | ----------- | ------ | -------- |
| VIZ-REV-01 | **BVA value-lever chart** | Bar/waterfall: 1.65M + 0.98M + 0.62M + 0.22M → 3.47M gross | Flyer BVA | P0 |
| VIZ-REV-02 | ROI / 3-year net scorecard | 127 % ROI · 6.41M 3-yr net · ±30 % ROM band | Flyer BVA | P0 |
| VIZ-REV-03 | KPI stat-counter set | 3.5 Mio CHF · 127 % · 7 Copilots | Flyer hero | P0 |
| VIZ-REV-04 | "7 decisions — Heute vs. Mit Curavias" comparison graphic | Before/after two-column visual | Flyer CIO table | P0 |
| VIZ-REV-05 | Review timeline | AMA HCC / North Star review, CAF/WAF alignment, sprint reviews | PRD §Traceability, ARCHITECTURE §CAF/WAF | P2 |
| VIZ-REV-06 | Compliance-readiness badge strip | DSG · ISO 27001 · Swiss residency · advisory-only | Flyer Kernaussage | P1 |
| VIZ-REV-07 | Synthetic testimonial cards | 2–3 quotes from synthetic operational personas (advisory-only framed) | New (persona-based) | P1 |
| VIZ-REV-08 | Evidence/traceability chain graphic | Source event → model output → answer → partner trigger | ARCHITECTURE §Observability | P2 |

---

## 3.7 Iconography & motif system (shared)

| ID | Asset | Description | Format | Priority |
| -- | ----- | ----------- | ------ | -------- |
| VIZ-ICO-01 | Swiss-cross node motif | Red cross used as path/brand accent | SVG | P0 |
| VIZ-ICO-02 | Success checkmark motif | Green "Erfolg / Freigabe" mark | SVG | P0 |
| VIZ-ICO-03 | HITL shield icon | "Freigabe erforderlich" | SVG | P0 |
| VIZ-ICO-04 | Data-gate icons (Bronze/Silver/Gold) | Quality-tier badges | SVG | P1 |
| VIZ-ICO-05 | Trust-pillar icons (6) | Deployment, region, PHI, FHIR, Entra, advisory | SVG | P1 |

---

## 3.8 Storytelling ideas (narrative devices to reuse)

1. **The CIO Challenger question** as the site's central hook (Section framing).
2. **"Heute vs. Mit Curavias"** before/after as the core value narrative.
3. **Follow one patient down the path** — each phase reveals the responsible role + agent.
4. **"Der Mensch entscheidet"** repeated as the trust refrain (advisory-only).
5. **Bronze→Silber→Gold** as the visual metaphor for data trust + PHI gates.
6. **Three experiences** as the "how it feels to use it" proof.
7. **Evidence-ready** — every claim traces to a source (mirrors the app's citations).
