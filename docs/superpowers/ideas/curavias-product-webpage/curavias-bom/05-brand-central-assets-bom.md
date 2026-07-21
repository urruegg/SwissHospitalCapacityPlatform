# Brand Central Assets BOM — Microsoft Logos & Stock Imagery

**Source:** Microsoft Brand Central — https://brandcentral.microsoft.com/
**Use:** official Microsoft logos + approved stock images for the Curavias showcase
(app + website): architecture/product visuals, storytelling, and hero/section imagery.

> ⚠️ **Acquisition note.** Brand Central requires Microsoft corporate sign-in, so the
> binary assets can't be pulled programmatically here. This BOM specifies **exactly
> what to download** and how to use it. Urs (or any signed-in MIH Zürich team member)
> downloads each item from Brand Central and drops it into the asset folders below.

**Legend — Priority:** P0 launch · P1 · P2. **Format:** prefer SVG (marks/icons), PNG (raster), JPG (photos).

---

## 5.1 Microsoft corporate & product logos

| ID | Asset | Where used | Format | Priority |
| -- | ----- | ---------- | ------ | -------- |
| BRD-LOGO-01 | Microsoft master logo (full-colour + mono + reversed) | Footer, "Powered by Microsoft", partner attribution | SVG | P0 |
| BRD-LOGO-02 | "Microsoft Innovation Hub" / MIH lockup (if available) | Hero attribution, footer, disclaimer | SVG/PNG | P0 |
| BRD-LOGO-03 | Microsoft for Healthcare lockup | Reference/CD alignment, evidence section | SVG | P1 |
| BRD-LOGO-04 | Microsoft Azure logo | Architecture diagrams, "runs on Azure" trust line | SVG | P0 |
| BRD-LOGO-05 | Microsoft Fabric logo + workload icons (Lakehouse, Eventstream, Eventhouse, Data Agent, Semantic Model) | Architecture, data-platform visuals (VIZ-AR-*) | SVG | P0 |
| BRD-LOGO-06 | Azure AI Foundry logo | AI-runtime diagrams | SVG | P1 |
| BRD-LOGO-07 | Azure OpenAI Service icon | AI layer diagrams | SVG | P0 |
| BRD-LOGO-08 | Power BI logo + icon | Dashboard/embed visuals | SVG | P0 |
| BRD-LOGO-09 | Microsoft Entra ID logo + icon | Identity/security diagrams | SVG | P0 |
| BRD-LOGO-10 | Microsoft Purview icon | Governance/lineage diagrams | SVG | P1 |
| BRD-LOGO-11 | Azure service icons set (Key Vault, Logic Apps, Container Apps, Health Data Services/FHIR, Monitor/Log Analytics, Policy, Service Bus, Storage) | Architecture/component topology (VIZ-AR-01/02) | SVG | P0 |
| BRD-LOGO-12 | GitHub logo + Actions/Copilot marks | Delivery-model & engineering-agent visuals (VIZ-TEAM-*) | SVG | P1 |

---

## 5.2 Stock photography (categories to pull)

Approved Brand Central photography, human/warm, matching REF-DS-05.

| ID | Category | Where used | Count | Priority |
| -- | -------- | ---------- | ----- | -------- |
| BRD-IMG-01 | Hospital operations / command-center | Hero (S1), Kurzüberblick (S4) | 2–3 | P0 |
| BRD-IMG-02 | Clinicians & care teams (collaborative, non-clinical-procedure) | Feature rows, agent section | 3–4 | P0 |
| BRD-IMG-03 | Nurses / bed & ward management context | Patient-path, BMCA/DCA sections | 2–3 | P1 |
| BRD-IMG-04 | Data / analytics / people-at-screens | Whiteboard, dashboards, DQ | 2–3 | P0 |
| BRD-IMG-05 | Swiss / Zürich context (city, Alpine, neutral hospital exterior) | Residency & MIH Zürich framing | 1–2 | P1 |
| BRD-IMG-06 | Security / trust / abstract governance | Sicherheit/Regulatorik (S9) | 1–2 | P1 |
| BRD-IMG-07 | Meeting / advisory / human-decision moments | HITL, "Der Mensch entscheidet" | 1–2 | P1 |
| BRD-IMG-08 | CTA / forward-looking / innovation | Nächste Schritte (S12) | 1 | P2 |

---

## 5.3 Brand system references (for CD/CI compliance)

| ID | Asset | Purpose | Priority |
| -- | ----- | ------- | -------- |
| BRD-SYS-01 | Microsoft brand guidelines (logo clear-space, min-size, don'ts) | Correct logo usage across app/site | P0 |
| BRD-SYS-02 | Segoe UI font package / web-font guidance | Typography (REF-DS-01) | P0 |
| BRD-SYS-03 | Microsoft colour tokens (blue + neutrals) | Accent palette alongside Curavias teal/green | P1 |
| BRD-SYS-04 | Fluent 2 design assets / icon library | UI kit + iconography (VIZ-PD-08) | P1 |
| BRD-SYS-05 | Azure architecture icon set (official) | Consistent architecture diagrams | P0 |
| BRD-SYS-06 | Co-branding / partner-showcase usage rules | "Powered by Microsoft" + MIH showcase attribution | P0 |

---

## 5.4 Usage & licensing guardrails

- All Microsoft marks used per **Brand Central usage rules** (clear-space, min-size,
  no recolouring, no distortion) — see BRD-SYS-01.
- Curavias is a **Microsoft Innovation Hub Zürich showcase**, not a Microsoft product:
  use **"Powered by Microsoft"** / showcase attribution, never imply a shipping product.
- Stock photography: internal showcase/demo use; verify each asset's Brand Central
  usage rights before any external publication of `curavias.ch`.
- Do **not** place Microsoft product logos in a way that implies certification,
  endorsement of clinical use, or a real medical device.
- Keep the **showcase disclaimer** visible wherever Microsoft marks appear.

---

## 5.5 Suggested asset folder layout (for the downloaded binaries)

```text
assets/
  brand/curavias/        ← Curavias marks (recreate, VIZ-PD-01/02)
  brand/microsoft/       ← BRD-LOGO-01..03, BRD-SYS-*
  logos/azure-services/  ← BRD-LOGO-04..11 (SVG icons)
  logos/github/          ← BRD-LOGO-12
  photography/           ← BRD-IMG-01..08 (JPG/PNG)
  diagrams/              ← VIZ-AR-*, VIZ-PJ-*, VIZ-REV-* exports (SVG/PNG)
  video/                 ← VID-01..04
```
