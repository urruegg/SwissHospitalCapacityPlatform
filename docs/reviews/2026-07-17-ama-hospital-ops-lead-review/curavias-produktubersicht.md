<p align="center">
  <img src="../../brandkit/logo/curavias-logo-tagline.svg" alt="Curavias" width="360"/>
</p>

# Curavias — die AI-Copilot-Plattform für den operativen Alltag im Spital

| Feld | Wert |
| ------ | ------ |
| **Zielgruppe** | CEO, CIO, COO, Leitung Betrieb / Bettenmanagement / OP-Koordination |
| **Version** | 1.0.0 |
| **Datum** | 2026-07-14 |
| **Sprache** | Deutsch |
| **Freigabe für** | Business-Review Spital Zollikerberg 2026-07-17 |

---

## 1. Executive Summary

**Curavias** ist eine Schweizer AI-Copilot-Plattform für den operativen Alltag im Spital. Sie beantwortet die zentrale Frage jeder Klinikleitung: *„Wo werden wir morgen und übermorgen unter Druck stehen — und was können wir heute schon tun?"*

Curavias liefert eine **verlässliche 3- bis 7-Tage-Vorschau** auf Bettenauslastung, OP-Belegung, Notfallankünfte, Entlassungspotenzial und Personalabdeckung. Aus dieser Vorschau werden **konkrete, erklärbare Handlungsvorschläge** für sieben Rollen im Spital abgeleitet — Bettenmanager, ED-Lead, Entlassungskoordination, OP-Koordination, Personalplanung, Krisenmanagement und Datenqualität — jeweils über einen eigenen AI-Copiloten.

Jeder Vorschlag ist **beratend, nicht autonom**: die Umsetzung bleibt beim Menschen und wird über transparente **Human-in-the-Loop-Kontrollen (HITL)** protokolliert und freigegeben. Datenhoheit, DSG-Konformität und Schweizer Betriebsdatenschutz sind eingebaut, nicht nachgerüstet.

Der wirtschaftliche Nutzen einer verlässlichen 3–7-Tage-Vorschau ist erheblich: **jährlicher Zielnutzen im ROM-Modell rund CHF 3.5 Mio.** pro Spital (weniger blockierte Bett-Tage, weniger teure Kurzfrist-Ersatzeinsätze, produktivere Command-Center-Arbeit, effizientere Compliance-Nachweise) bei einem **3-Jahres-Nettowert von rund CHF 6.4 Mio.** und einem ROI von **127 %**.

---

## 2. Warum jetzt — die CIO-Challenger-Frage

> *„Welche operativen Entscheidungen könnten heute besser getroffen werden, wenn die zukünftige Kapazitäts- und Auslastungssituation 3 bis 7 Tage im Voraus mit hoher Zuverlässigkeit bekannt wäre?"*

Curavias adressiert diese Frage direkt. Sieben operative Entscheidungen im Spital gewinnen bei 3–7 Tagen Vorschau messbar an Qualität und Wirtschaftlichkeit:

| Nr. | Operative Entscheidung | Heutiger Zustand | Mit Curavias-Vorschau |
| --- | ---------------------- | ----------------- | ---------------------- |
| 1 | **Bettenzuweisung** über Stationen und Fachbereiche | Reaktiv am Aufnahmemorgen, häufig unter Zeitdruck | 3–7 Tage vorausschauend — Bettenumbauten und Verlegungen werden geplant, nicht improvisiert |
| 2 | **OP-Slot-Nutzung** und Slate-Rebalancing | Absagen und Leerslots werden am OP-Tag entdeckt | Ausfallrisiko und Umverteilungspotenzial werden Tage im Voraus sichtbar |
| 3 | **Personalabdeckung** in Pflege und Ärzteschaft | Kurzfristiger Poolzugriff, teure Agenturzuschläge | Dienstpläne werden auf prognostizierten Bedarf abgestimmt statt auf Durchschnittsannahmen |
| 4 | **Entlassungssteuerung** und Nachversorgungs-Handoffs | Entlassungen sind am Vormittag nicht abschätzbar, Nachversorger reagieren spät | Entlassungskandidaten mit Blockern und Handoff-Status sind 24–72 h vorher sichtbar |
| 5 | **Verlegungen** und Aufnahmestopp-Entscheidungen | Ad-hoc, Kommunikation unter Zeitdruck | Kaskaden werden simuliert, betroffene Partner werden früh eingebunden |
| 6 | **Krisen- und Szenario-Antworten** (Ausbruch, IT-Ausfall, Personalengpass) | Doktrin liegt im Ordner, wird im Ernstfall gesucht | Doktrin-basierte Handlungsempfehlungen werden szenariogetrieben vorgeschlagen und dokumentiert |
| 7 | **Datenqualitäts-Alarme** vor Fehlentscheidungen | Datenprobleme fallen erst im KPI-Report auf | Bronze→Silber→Gold-Gates alarmieren, bevor eine Kennzahl in eine Entscheidung fliesst |

Die Vorschau selbst basiert auf einem **72-Stunden-Prognosemodell** für Notfallankünfte und Belegungsdruck (Curavias-Kernfähigkeit `FR-FC-001`), das stündlich refresht wird und pro Fachbereich und Zeitfenster ausrollt.

---

## 3. Die sieben Curavias-Agenten — Fähigkeiten und Zielrollen

Curavias liefert seine Fähigkeiten über sieben spezialisierte AI-Copiloten, jeweils für eine klar umrissene Rolle im Spital. Alle Agenten sind **beratend** — sie erklären ihre Empfehlung und ihre Quellen, aber jede Aktion mit Aussenwirkung läuft über eine HITL-Freigabe.

| Agent | Zielrolle im Spital | Was er liefert | HITL-Gate |
| ------ | ------------------- | -------------- | --------- |
| **Bettenmanagement-Copilot (BMCA)** | Bettenmanager | Antworten auf Fragen zur Belegung, zum Bettendruck und zu Kandidaten für Verlegung oder Same-Day-Entlassung — mit erklärbaren Rankings | HITL-02 Bettenverlegung / Repriorisierung |
| **Belegungs- & 72-h-Forecast-Copilot (OOA)** | ED-Lead, Operations Lead | Prognose von Ankünften, Saisonalität und Belegung 72 h voraus, aufgeschlüsselt nach Fachbereich | HITL-05 Prognosegetriebene Personal- / Kapazitätsentscheidung |
| **Entlassungs-Copilot (DCA)** | Entlassungskoordination, Care-Transition | Ranking der Entlassungskandidaten mit Blockern, Nachversorger-Handoff-Status | HITL-03 Cross-organisationaler Handoff |
| **OP-Steuerungs-Copilot (ORSA)** | OP-Koordination | Erkennung von leeren OP-Slots, Vorschläge zur Slate-Umverteilung, Absagerisiko | HITL-01 Änderung am OP-Slate |
| **Personal-Balance-Copilot (SBA)** | Personalplanung / Staffing Coordinator | Heatmap der Personallücken und Roster-vs-Forecast-Delta durch Verknüpfung von Dienstplan und Prognose | HITL-05 Personal- / Kapazitätsentscheidung |
| **Krisen- & Szenario-Copilot (CSA)** | Krisen- / Diensthabender Manager | Bewertung hypothetischer Szenarien (Nachfrageschock, Kapazitätsverlust, Systemstörung) gegen den Schweizer *Lage*-Klassifikator und doktrin-konforme Handlungsempfehlungen | HITL-04 Politik-Ausnahme (nur bei Bedarf) |
| **Datenqualitäts-Agent (DQ)** | Data Engineer, Ontology Steward | Bronze→Silber→Gold-Qualitätsgates mit Drift-Alarmen; PHI-Gates sind nicht deaktivierbar | HITL-04 Politik-Ausnahme bei PHI-Maskierung |

Die Personazuordnung ist **keine Marketingfolie**, sondern in unseren Betriebsartefakten (`agents/<name>/AGENT.md` §1 Identity) fest verankert und mit Golden-Task-Fixtures getestet.

---

## 4. Wie Curavias arbeitet — die drei Erlebnisse

**1. Copilot-Drawer.** Aus jedem Bildschirm im operativen Alltag ist der zuständige Copilot einen Klick entfernt. Frage in natürlicher Sprache stellen, geerdete Antwort mit Quellenverweisen erhalten. Beispiel Bettenmanager: *„Wo werden wir morgen zwischen 14 und 18 Uhr unter Druck stehen?"* → BMCA nennt die drei betroffenen Stationen, die drei besten Entlassungskandidaten und den prognostizierten Belastungsgrad.

**2. Whiteboard.** Ein visuelles Command-Center pro Rolle: Bettenpressure, OP-Slate, Entlassungspipeline, 72-h-Forecast, Personallücken, Krisenszenarien und Datenqualitätsstatus als konfigurierbare Karten auf einer Fläche. Alle Karten sind live, alle KPIs mit Curavias-Ontologie verknüpft — ein Klick zeigt die Quelle jeder Zahl.

**3. Human-in-the-Loop-Governance.** Jede Empfehlung, die eine Aktion mit Aussenwirkung auslöst (Verlegung, OP-Änderung, Personaltrigger, Cross-Organisation-Handoff, Politik-Ausnahme), wird über eine der fünf HITL-Gates (`HITL-01` bis `HITL-05`) protokolliert, mit Verantwortlichem, Zeitstempel und Entscheidungsgrund. Ohne HITL-Nachweis wird die Aktion **deny-by-default** blockiert — das ist DSG-, ISO-27001- und CH-Compliance-belastbar von Tag 1 (siehe [ADR-0007](../../adr/0007-mvp-agent-runtime-and-hitl-release-gates.md)).

---

## 5. Datenhoheit, Sicherheit, Regulatorik

- **Provider-internes Deployment.** Eine Curavias-Instanz pro Spital-Provider. Keine geteilte Tenancy, keine Cross-Provider-Datenflüsse. Ihre Daten bleiben in Ihrer Umgebung.
- **Schweizer Region.** Curavias läuft auf Microsoft Azure in Schweizer Rechenzentren (Switzerland North). Datenresidenz-Fragen des Kantons und der Aufsicht sind gelöst.
- **PHI-Schutz eingebaut.** Bronze→Silber→Gold-Datenpipeline mit PHI-Gates, die nicht überschrieben werden können. Copilot-Antworten sind auf Ontologie-Entitäten geerdet — keine PHI-Leaks aus Modellen.
- **HL7 FHIR-native.** Standardisierte Interoperabilität mit KIS-Systemen, Labor, Nachversorgungs-Partnern.
- **Entra-basierte Identität.** Rollen aus dem Spital (Bettenmanager, OP-Koordination, etc.) sind auf App-Rollen abgebildet; jede Aktion ist einem authentifizierten Nutzer zugeordnet und im Audit-Log nachweisbar.
- **Advisory-only-Doktrin.** Curavias-Agenten treffen keine operativen Entscheidungen — sie **beraten** die Person, die entscheidungsbefugt ist. Diese Trennung ist auf Architekturebene festgeschrieben (`NFR-AI-001`) und in jedem Agenten-Prompt reproduziert.

---

## 6. Wirtschaftlicher Nutzen im Überblick

Auf Basis unseres validierten Business-Value-Assessments ([`docs/BVA.md`](../../BVA.md), 3-Jahres-Planungshorizont, ROM-Konfidenz ±30 %):

| Werthebel | Jahresnutzen (CHF, ROM) | Begründung |
| --------- | ----------------------- | ---------- |
| Weniger blockierte Bett-Tage und Verzögerungen bei der Entlassung | **1'650'000** | Schnellere Koordination, frühere Handoffs an Nachversorger |
| Produktivität im Command-Center (Bettenmanagement, OP-Koordination) | **980'000** | 120 Spitzennutzer mit weniger manueller Triage und schnelleren Entscheidungen |
| Weniger Überstunden und Agentur-Zuschläge durch bessere Bedarfsprognose | **620'000** | Prognoseinformierte Personalplanung reduziert teure Ad-hoc-Deckung |
| Effizienz in Compliance- und Audit-Vorbereitung | **220'000** | Evidence-ready Controls reduzieren wiederkehrende Prüfaufwände |
| **Jährlicher Bruttonutzen** | **≈ 3'470'000** | Werthebel-Summe (Referenz für ROI-Modell) |
| **3-Jahres-Nettowert** | **6'410'000** | Nach TCO für 3 Jahre |
| **Year-1-Nettowert** | **1'270'000** | Bereits im ersten Jahr positiv |
| **ROI (Base-ROM, 3 Jahre)** | **127 %** | Balanced-Adoption-Profil |

Diese Werte sind **Rough-Order-of-Magnitude** und für Business-Case-Gespräche gedacht, nicht als finale Angebots-Grundlage.

---

## 7. Nächste Schritte

1. **Review-Session am 2026-07-17** (60 min) — gemeinsame Validierung des Funktionsumfangs gegen Ihre operative Realität. Vorbereitung: Interview-Briefing (separates Dokument).
2. **Discovery-Fragen** entlang der sieben Curavias-Agenten — welche Entscheidungen bei Ihnen heute im Blindflug laufen, welche Vorbedingungen (KIS-Anbindung, Datenverfügbarkeit) bestehen bereits.
3. **Roadmap-Skizze** — welcher Agent bringt bei Ihnen als erstes messbaren Nutzen, welche Rollout-Sequenz macht Sinn.

<p align="center">
  <img src="../../brandkit/logo/curavias-symbol.svg" alt="Curavias Symbol" width="60"/>
  <br/>
  <em>Curavias — verlässliche Vorschau. Erklärbare Empfehlung. Mensch entscheidet.</em>
</p>
