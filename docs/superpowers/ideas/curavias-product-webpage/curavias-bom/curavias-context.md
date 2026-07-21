# Curavias — Enclosed Context Pack

> Canonical context for every artefact in this BOM. All copy, visuals, and
> components must stay consistent with the brand, north star, and disclaimer below.

---

## 1. Identity & Brand

| Field | Value |
| ----- | ----- |
| **Product name** | Curavias |
| **Descriptor** | Swiss Hospital Capacity Copilot |
| **Brand promise (tagline)** | *Every patient's path, in Swiss hands.* |
| **North star** | *Verlässliche Vorschau. Erklärbare Empfehlung. Der Mensch entscheidet.* (Reliable preview. Explainable recommendation. The human decides.) |
| **Positioning line** | Die AI-Copilot-Plattform für den operativen Alltag im Spital |
| **Owner / origin** | Microsoft Innovation Hub Zürich — Showcase |
| **Web** | curavias.ch |
| **Primary language** | German (DE-CH); English secondary |
| **Logo mark** | Stylised patient path (teal→green) with a red Swiss cross node and a green success checkmark |

### Showcase disclaimer (MUST appear on flyer, app, and website)
> **Kein reales Produkt.** Curavias ist ein Showcase des Microsoft Innovation Hub
> Zürich — synthetische Daten, beratende KI (advisory-only), kein Medizinprodukt
> und nicht für den klinischen Einsatz.

*(EN: Not a real product. Curavias is a Microsoft Innovation Hub Zürich showcase —
synthetic data, advisory-only AI, not a medical device, not for clinical use.)*

---

## 2. Hero KPIs (headline proof points)

| KPI | Value | Label |
| --- | ----- | ----- |
| Annual target benefit (ROM) | ≈ 3.5 Mio. CHF | CHF jährl. Zielnutzen |
| 3-year ROI | 127 % | ROI über 3 Jahre |
| Specialised AI copilots | 7 | spezialisierte AI-Copiloten |

---

## 3. The Curavias Patient Path (KEEP — hero infographic)

> "Vom Eintritt zum Erfolg — Rollen und AI-Agenten entlang der Behandlung."

| # | Phase | Role | Agent | Agent focus |
| - | ----- | ---- | ----- | ----------- |
| 1 | Notfall & Aufnahme | Notfall-Leitung | **OOA** | 72-h-Forecast |
| 2 | Bettenzuweisung | Bettenmanagement | **BMCA** | Bettendruck & Kandidaten |
| 3 | OP & Behandlung | OP-Koordination | **ORSA** | OP-Slate-Steuerung |
| 4 | Pflege & Personal | Personalplanung | **SBA** | Roster vs. Forecast |
| 5 | Entlassung | Entlassungskoordination | **DCA** | Ranking & Handoff |
| 6 | Erfolg | — | — | Patient ist genesen ✓ |

**Cross-cutting lanes (span the whole path):**
- **CSA** — Krisen & Szenarien
- **DQ** — Datenqualität (Gates)

**Governance band (under the whole path):**
- **Human-in-the-Loop** — jede Aktion mit Aussenwirkung wird freigegeben. Der Mensch entscheidet.

---

## 4. The Seven Curavias Agents

| Agent | Code | Target role | What it delivers | HITL gate |
| ----- | ---- | ----------- | ---------------- | --------- |
| Bettenmanagement-Copilot | **BMCA** | Bettenmanagement | Belegung, Bettendruck, Verlegungs-/Same-Day-Kandidaten — erklärbar | Bettenverlegung |
| Belegungs- & Forecast-Copilot | **OOA** | Notfall-Leitung, Ops Lead | 72-h-Prognose von Ankünften & Belegung je Fachbereich | Kapazität |
| Entlassungs-Copilot | **DCA** | Entlassungskoordination | Ranking der Entlassungskandidaten mit Blockern & Handoff-Status | Cross-org. Handoff |
| OP-Steuerungs-Copilot | **ORSA** | OP-Koordination | Leere OP-Slots, Slate-Umverteilung, Absagerisiko | OP-Slate-Änderung |
| Personal-Balance-Copilot | **SBA** | Personalplanung | Heatmap der Personallücken, Roster-vs-Forecast-Delta | Personal |
| Krisen- & Szenario-Copilot | **CSA** | Krisen-/Diensthabende | Szenario-Bewertung gegen den Schweizer Lage-Klassifikator | Politik-Ausnahme |
| Datenqualitäts-Agent | **DQ** | Data / Ontology Steward | Bronze→Silber→Gold-Gates, Drift-Alarme; PHI-Gates nicht deaktivierbar | PHI-Ausnahme |

---

## 5. The Three Experiences (*Die drei Erlebnisse*)

1. **Copilot-Drawer** — Frage in natürlicher Sprache, geerdete Antwort mit Quelle.
2. **Whiteboard** — konfigurierbares Live-Command-Center pro Rolle.
3. **Human-in-the-Loop** — jede Aktion mit Aussenwirkung wird protokolliert & freigegeben.

---

## 6. The CIO Challenger Question (framing device)

> *"Welche operativen Entscheidungen könnten heute besser getroffen werden, wenn
> die zukünftige Kapazitäts- und Auslastungssituation 3 bis 7 Tage im Voraus mit
> hoher Zuverlässigkeit bekannt wäre?"*

**Seven operational decisions — Heute vs. Mit Curavias-Vorschau:**

| # | Operative Entscheidung | Heute | Mit Curavias-Vorschau |
| - | ---------------------- | ----- | --------------------- |
| 1 | Bettenzuweisung | Reaktiv am Aufnahmemorgen, unter Zeitdruck | 3–7 Tage vorausschauend — geplant statt improvisiert |
| 2 | OP-Slot-Nutzung | Absagen/Leerslots werden am OP-Tag entdeckt | Ausfallrisiko & Umverteilung Tage im Voraus sichtbar |
| 3 | Personalabdeckung | Kurzfristiger Pool, teure Agenturzuschläge | Dienstpläne auf prognostizierten Bedarf abgestimmt |
| 4 | Entlassungssteuerung | Am Vormittag nicht abschätzbar | Kandidaten mit Blockern & Handoff 24–72 h vorher |
| 5 | Verlegungen / Aufnahmestopp | Ad-hoc, Kommunikation unter Zeitdruck | Kaskaden simuliert, Partner früh eingebunden |
| 6 | Krisen- & Szenario-Antworten | Doktrin liegt im Ordner | Doktrin-basierte Empfehlungen, szenariogetrieben |
| 7 | Datenqualitäts-Alarme | Fallen erst im KPI-Report auf | Gates alarmieren, bevor eine Kennzahl in Entscheidungen fliesst |

---

## 7. Data Sovereignty, Security & Regulatory (trust pillars)

- **Provider-internes Deployment** — eine Instanz pro Spital-Provider, keine geteilte Tenancy.
- **Schweizer Region** — Betrieb auf Microsoft Azure in Schweizer Rechenzentren (Switzerland North); Datenresidenz gelöst.
- **PHI-Schutz eingebaut** — Bronze→Silber→Gold-Pipeline mit nicht überschreibbaren PHI-Gates; geerdete Copilot-Antworten.
- **HL7 FHIR-nativ** — standardisierte Interoperabilität mit KIS, Labor und Nachversorgungs-Partnern.
- **Entra-basierte Identität** — Spital-Rollen auf App-Rollen abgebildet; jede Aktion authentifiziert & im Audit-Log nachweisbar.
- **Advisory-only-Doktrin** — Agenten entscheiden nicht, sie beraten die entscheidungsbefugte Person.

> **Kernaussage:** Verlässliche Vorschau + erklärbare Empfehlung + Human-in-the-Loop
> = belastbar für DSG, ISO 27001 und Schweizer Compliance ab Tag 1.

---

## 8. Business Value (BVA — 3-year ROM, ±30 %)

| Werthebel | Jahresnutzen (CHF) | Begründung |
| --------- | ------------------ | ---------- |
| Weniger blockierte Bett-Tage & Entlassungs-Verzögerungen | 1'650'000 | Schnellere Koordination, frühere Handoffs |
| Produktivität im Command-Center | 980'000 | 120 Spitzennutzer, weniger manuelle Triage |
| Weniger Überstunden & Agentur-Zuschläge | 620'000 | Prognoseinformierte Personalplanung |
| Effizienz in Compliance & Audit | 220'000 | Evidence-ready Controls |
| **Jährlicher Bruttonutzen** | **≈ 3'470'000** | Werthebel-Summe |
| **3-Jahres-Nettowert** | **6'410'000** | nach TCO für 3 Jahre |
| **ROI (Base-ROM, 3 Jahre)** | **127 %** | Balanced-Adoption-Profil |

*ROM-Werte für Business-Case-Gespräche, nicht als finale Angebots-Grundlage.*

---

## 9. Demo Organisation & Hospitals

| Item | Value | Source |
| ---- | ----- | ------ |
| Demo tenant model | Entra demo-org master data (MCAPS demo-user model, ADR-0012) | repo `data/`, Sprint 12 |
| Demo hospitals (capacity contracts) | **Hirslanden** (`DC-ONB-CAPACITY-HIRSLANDEN-v1`), **Zollikerberg** (`DC-ONB-CAPACITY-ZOLLIKERBERG-v1`) | SD.md |
| Rollout patterns (named) | **USZ-first** or **LUKS-first** implementation sequence | PRD `FR-OM-003` |
| Demo data | Synthetic / non-production only (no PHI in demo scope, ADR-0016) | repo `data/synthetic/` |
| Demo region carve-out | `westus2` demo scope permitted (ADR-0013); `switzerlandnorth` for PROD/PHI | PRD `FR-ONT-002` |

---

## 10. Delivery Model & Engineering Agents (GitHub-native)

- Governance and requirements are **documented first**.
- **Agent-based workflows** generate and review solution artefacts (GitHub Copilot coding agent is the repository control-plane runtime, ADR-0001/0002).
- Security, compliance, and test evidence are **built into the release path** (Git-first, DEV→SIT→PROD with approval gates, OIDC).
- Agent registry: `AGENTS.md`; semantic/ontology owner named in `OPERATIONS.md`.

---

## 11. Regulatory / usage guardrails for all content

- Always show the **showcase disclaimer**; never imply a real, sold, or clinical product.
- Advisory-only framing everywhere ("berät", "Vorschlag", not "entscheidet/diagnostiziert").
- No real patient data, no real named clinicians; synthetic personas only.
- Microsoft brand and product marks must follow Brand Central usage rules (see `05-brand-central-assets-bom.md`).
