# Review-Report — Curavias-Follow-up-Review mit Dr. med. Marco Rossi (2026-08-10)

| Feld | Wert |
| ---- | ---- |
| **Version** | 1.0.0 |
| **Datum** | 2026-08-10 |
| **Autor** | @urruegg |
| **Status** | Draft |
| **Previous Version** | n/a (initial version) |
| **Intake-Kind** | `session` (informelles Follow-up-Gespräch, ~55 Min, Deutsch, Bildschirm-Demo der aktuellen Implementierung) |
| **Quelle** | [`2026-08-10-ama-curavias-ops-review-transcript-summary.md`](2026-08-10-ama-curavias-ops-review/2026-08-10-ama-curavias-ops-review-transcript-summary.md) (normalisierte Meeting-Notizen) |
| **Review-Pack** | [`README.md`](2026-08-10-ama-curavias-ops-review/README.md) |
| **Namenskonvention** | **Bewusste Abweichung** von der sonst üblichen Anonymisierung (vgl. `2026-07-24-ama-coo-review.md`, `2026-07-17-ama-hospital-ops-lead-review.md`): Dr. med. Marco Rossi wird **namentlich** referenziert. Er ist bereits ein realer, öffentlich genannter, mit seiner Zustimmung kreditierter Reviewer **im Produkt selbst** (`BackstageNarrativeSections.tsx` PRACTITIONERS-Roster, `start-content.ts` CHALLENGER_PERSONAS, Attribution-Hinweis: *"Named practitioners are shown with their consent to be credited"*). Die namentliche Nennung hier setzt diese bestehende, konsentierte Behandlung fort statt ihr zu widersprechen. |

> Erstellt durch den [`review-session-agent`](../../agents/review-session-agent/AGENT.md) nach der
> Struktur in [`docs/reviews/README.md`](README.md) § *Minimum Review Report Structure*.

---

## 1. Session-Metadaten

| Feld | Wert |
| ---- | ---- |
| Session-Datum | 2026-08-10 |
| Dauer / Format | ~55 Min, informelles Follow-up-Gespräch (Bildschirm-Demo + offene Diskussion), Deutsch |
| Teilnehmende (Reviewer) | **Dr. med. Marco Rossi** — Infektiologe und ehemaliger Chefarzt, LUKS Luzern |
| Teilnehmende (unsere Seite) | **@urruegg** (Moderation, Facharchitektur) |
| Kontinuität | Dies ist Marcos **zweites** Review-Gespräch. Das erste war Teil des gebündelten "Hospital Operations"-Feldinterviews mit Christian Ernst und Dr. Regula Adams am **17.07.2026** (Datum bestätigt in `start-content.ts` `CHALLENGER_PERSONAS.ops.reviewers[2]` und im Backstage-Roster). Dieses Follow-up vertieft dieselbe Perspektive ("Time for patient care") mit Marcos eigener klinischer Erfahrung. |

---

## 2. Geprüfte Inputs

1. **Roh-Transcript** (primäre Quelle) — [`AMA Review Curavias Showcase.vtt`](2026-08-10-ama-curavias-ops-review/AMA%20Review%20Curavias%20Showcase.vtt) (4606 Zeilen, WEBVTT, vollständig gelesen) und die begleitende `.docx`-Fassung.
2. **Transcript-Summary** — normalisierte Meeting-Notizen, siehe Quelle oben.
3. **Erstes Marco-Rossi-Review (17.07.2026)** — [`2026-07-17-ama-hospital-ops-lead-review.md`](2026-07-17-ama-hospital-ops-lead-review.md) — als Kontinuitäts-Baseline; insbesondere die dort bereits bestätigte Kernfrage *"Wie bekommen wir ein System, das uns Zeit für die Patientenbetreuung zurückgibt?"*.
4. **Produkt-Narrative** — [`start-content.ts`](../../apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts) (`CHALLENGER_PERSONAS.ops`), [`BackstageNarrativeSections.tsx`](../../apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative/BackstageNarrativeSections.tsx) (`ReviewSessionsSection`, `PRACTITIONERS`-Roster) und `en/de/fr/it.json` (`start.frontier.challenger.personas.ops`, `backstage.story.narrative.reviews.*`).
5. **Repository-Baseline** — [`docs/PRD.md`](../PRD.md), `agents/{bmca,ooa,dca,orsa,sba,csa}-agent/AGENT.md`, [`docs/adr/0007`](../adr/0007-mvp-agent-runtime-and-hitl-release-gates.md) (HITL), [`docs/adr/0016`](../adr/0016-no-phi-in-mvp-demo-scope.md) (kein PHI).
6. **Repository-Suche** — Bestätigt: es existiert **keine** bestehende "Intake-/Aufnahme-Triage-Agent"-Definition im Repository (`signal-triage-agent` und `signal-agent` betreffen ausschliesslich externe Hazard-/Datensignale, nicht die klinische Patientenaufnahme) — Marcos Vorschlag ist ein **neuer** Namensraum ohne Kollision.

---

## 3. Outcome-Summary (die drei Kernpunkte)

1. **"Zeit zurückgeben" braucht eine Differenzierung, keine Pauschale.** Marco widerspricht der naiven Gleichung *Bildschirmzeit = unnötige Administration*. Sein Beispiel: eine dreifache Kostengutsprache für dieselbe Leistung ist Unsinn — aber Datenauswertung mit KI zur Diagnosefindung, interdisziplinäre Absprachen und die Dokumentation für einen sauberen Übergabepunkt **sind Patientenarbeit**, auch wenn sie am Bildschirm stattfinden. *(VTT ~10:45–13:58)*
2. **Prep · Perform · Recap als gemeinsam geschärfte Qualitätszeit-Formel.** Im Gespräch wird gemeinsam (Urs formuliert, Marco bestätigt ausdrücklich mit *"Ich bin einverstanden"*) die Zielgrösse präzisiert: Zeit ist dann Qualitätszeit, wenn sie der **Vorbereitung**, der **Durchführung** und der **Nachbereitung** eines Patiententermins dient und einen sauberen Übergabepunkt zwischen Disziplinen ermöglicht. *(VTT ~14:06–14:55)*
3. **Intake-Triage als Hebelpunkt Nr. 1 — der Kern-Impuls dieser Session.** Marco identifiziert die Ersteinschätzung in der Notaufnahme als unterschätzten Hebel: heute oft von den am wenigsten erfahrenen Kräften getroffen, sollte sie umgekehrt von einer Kaderärztin/einem Kaderarzt mit Schichtleitung geführt werden — unterstützt durch einen KI-Triage-Assistenten, der anhand von Mustern vergleichbarer Fälle früh einschätzt, ob ein Fall "schnell wieder raus" oder "bleibt lange" ist. Bestätigt durch die Simulation: **"Je besser man die Triage macht, desto optimaler läuft es danach für alle Beteiligten."** *(VTT ~33:27–39:35)*

> **Schlüssel-Outcome (Design-Konsequenz):** Alle drei Punkte sind Verfeinerungen derselben, im ersten Interview (17.07.2026) bereits bestätigten Kernthese — *"gib uns Zeit für den Patienten zurück"* — nicht neue, unabhängige Anforderungen. §6 unten bewertet für jeden Punkt konkrete Lösungsansätze; §9 verankert die Kontinuität zum ersten Interview.

---

## 4. Key Findings

### 4.1 "Zeit zurückgeben" ist nicht gleich "Bildschirmzeit reduzieren"

Marco widerspricht der vereinfachten Team-interne Lesart, dass jede administrative Entlastung automatisch gut sei: *"Unnötige Administration ist, wenn ein Arzt das dritte Mal eine Kostengutsprache zur gleichen Leistung machen muss"* — das ist reiner Leerlauf. Aber: *"Ein Teil der Patientenarbeit ist im Büro am Bildschirm … ich will als Patient, dass mein Behandlungsteam sich auch nicht nur am Patienten [aufhält], sondern auch im Büro"* — durch interdisziplinäre Absprachen und KI-gestützte Diagnosefindung. Sein Schluss: *"Es ist nicht ganz einfach zu trennen, was unnötige Administration ist."* *(VTT ~10:52–13:58)*

**Verdikt:** relevant, verschärft eine bestehende Annahme. Die START-Narrative der `ops`-Persona sprach bereits generisch von *"time for patient care"*; dieser Befund liefert die fehlende Differenzierung zwischen **Verschwendung** (Wiederholungs-Bürokratie) und **legitimer Bildschirmarbeit** (KI-gestützte Fallarbeit, Übergabe-Dokumentation).

### 4.2 Prep · Perform · Recap — die Qualitätszeit-Formel

In direkter Fortsetzung von 4.1 präzisiert das Gespräch die Zielgrösse: *"Es geht … primär auch [darum], dass sie sich optimal vorbereiten können auf den Termin, den optimal durchführen kann [und] optimal nachbearbeiten kann, und somit auch … einen sauberen Handoff von einer Disziplin oder Arzt … zum anderen [gibt]."* Marco bestätigt ausdrücklich: *"Ich bin einverstanden."* *(VTT ~14:06–14:55)*

**Verdikt:** relevant, neue explizite Formel. Dies ist keine neue Idee, sondern die **Operationalisierung** der bereits im ersten Interview genannten "Share of Time"-KPI (siehe §4.1 dort) in drei messbare Phasen.

### 4.3 Intake-Triage als höchster Hebel — der Kern-Impuls dieser Session

Dies ist Marcos substanziellster, klinisch am tiefsten begründeter Beitrag:

- **Strukturkritik:** *"So wie wir aufgestellt sind, haben wir ja überall Lehrlinge in allen Positionen … und dann kommen erst nachher die Erfahrenen. Eigentlich muss man das umgekehrt machen: eine erste Triage muss eigentlich [von] einem Kaderarzt/einer Kaderärztin zusammen mit der Schichtleitung [und] der Pflege"* gemacht werden. *(VTT ~33:50–34:24)*
- **Was diese Ersteinschätzung leisten muss:** nicht Laborwerte lesen, sondern früh und korrekt abschätzen, wie komplex ein Fall ist und was er an Ressourcen/Verweildauer braucht — sein Beispiel-Kontrast: ein Schrittmacher-Patient kann ggf. am gleichen Tag nach Hause; ein Patient mit drei chronischen Erkrankungen, der sich über zwei Wochen verschlechtert hat, braucht mehrstufige Abklärungen und bleibt sicher mehrere Tage. *(VTT ~34:36–36:35)*
- **Sein Befund:** *"Solche Weichenstellungen werden von mir aus gesehen im Moment noch in unseren Notfallstationen zu wenig getroffen."* *(VTT ~36:36–36:44)*
- **Sein Lösungsvorschlag — ein KI-Triage-Assistent:** *"Kann ein KI … die ersten Daten vom Patienten, die man nach einer halben Stunde hat, mal sichten … aufgrund von Vergleichsdatensätzen … nicht einmal nur die Inhalte … sondern nur schon das Muster der Untersuchung … [und sagen] 'Oh, das kommt mir bekannt vor, das sind Patienten, die sind schnell wieder draussen, oder das sind Patienten, welche lange bleiben.'"* *(VTT ~36:49–37:22)*
- **Ergänzender Befund — Entlassplanung beginnt zu spät:** *"Auch wenn der Patient zuerst auf die Abteilung kommt, dann kommt am Abend … oder am nächsten Tag das erste Mal jemand und sagt … was brauchen wir jetzt noch alles? … für das Spital ist es ein Problem, dass wir nicht von den Notfallpforten an bereits den Austritt planen."* *(VTT ~38:12–38:36)*
- **Bestätigung durch die Simulation (Urs, reflektiert von Marco bestätigt):** *"Je besser man die Triage macht, desto optimaler läuft es danach für alle Beteiligten."* — Marco: *"Ja, da bin ich tief überzeugt, und dort sind wir auch noch nicht dort, wo wir sein können."* *(VTT ~39:16–39:38)*

**Verdikt:** **neue, gut begründete Idee** — kein Namenskonflikt mit bestehenden Agenten (§2 Punkt 6). Wird in §6.3 als bewerteter Lösungsansatz (Intake-Triage-Assistent) dokumentiert.

### 4.4 Prozess-Parallele: gute Discovery = gute Triage

Ein methodischer Nebenbefund mit Substanz: Marco lobt explizit den im Gespräch verwendeten Discovery-Ansatz — *"Active Listening"* und *"Peel the Onion"* (Trennung von Annahme und Fakt, "don't jump to the solution", Ziel/Mehrwert vor Lösung definieren) — und zieht selbst die Parallele: *"Das ist interessant, eigentlich bei der Patientenbehandlung dasselbe, oder?"* Urs bestätigt: *"Genau, du machst bei der Triage genau das gleiche."* *(VTT ~49:08–49:51)*

**Verdikt:** bestätigt methodisch, dass der Intake-Triage-Assistent (4.3) kein Fremdkörper ist, sondern strukturell demselben Muster folgt wie die bereits etablierte Discovery-Methodik dieses Programms.

### 4.5 Ergänzender Kontext — Datenschutz-Selbstblockade und funktionale Machbarkeit zuerst

Nicht Teil der drei Kernideen, aber mit Substanz für §5/§8: Marco reflektiert selbstkritisch, dass übervorsichtige Auslegung von Datenschutz-/Swissmedic-Vorgaben teils zur Selbstblockade führt (*"Ich glaube, wir tun uns selber auch im Weg stehen"*, *"Ein Nein muss immer eine Alternativlösung bieten"*), bestätigt aber gleichzeitig die bereits gültige Doktrin (No-PHI/Metadaten). Er verweist zudem auf den validierten Ansatz, fachliche Machbarkeit zuerst mit Beispieldaten (SwissNOSO) zu beweisen, bevor Infrastruktur-/Cloud-Fragen diskutiert werden — deckungsgleich mit der bestehenden No-PHI-/Metadaten-Doktrin. *(VTT ~44:10–53:21)* **Requires validation**, da nicht vertieft: ob dies eine neue Anforderung an das Onboarding-Playbook auslösen soll.

---

## 5. Gaps und Risiken

| # | Kategorie | Gap / Risiko | Auswirkung | Wahrsch. | Mitigation |
| - | --------- | ------------ | ---------- | -------- | ---------- |
| G1 | Produkt-Narrative | START-`ops`-Persona sprach bisher nur generisch von "Zeit für Patientenbetreuung" ohne die Prep/Perform/Recap-Differenzierung | Marketing-Text unterschätzt die Tiefe des validierten Kundendialogs | M | §6.2 — Text erweitern (dieser PR) |
| G2 | Roadmap | Kein bestehender Agent/keine Ontologie-Komponente deckt "Intake-Triage-Unterstützung" ab | Marcos höchster Hebelpunkt bleibt unadressiert, falls nicht aufgenommen | H | §6.3 — als "discovered idea" mit FR-Stub dokumentieren, Sprint-Intake vorschlagen |
| G3 | Daten | Die genannte "Muster-Erkennung ähnlicher Fälle" würde reale historische Fall-Metadaten (Untersuchungsmuster, nicht Inhalte) benötigen — Datenverfügbarkeit nicht geprüft | Machbarkeits-Unsicherheit für eine künftige Intake-Triage-Komponente | M | Datenverfügbarkeits-Assessment als Vorbedingung, analog zum 17.07.-Review (§5 dort) |
| G4 | Messung | "Share of Time" / Prep-Perform-Recap ist als Konzept bestätigt, aber noch nicht als messbare Grösse operationalisiert (Marco selbst: *"Gerade am Überlegen, ist das so einfach zu messen"*) | KPI bleibt qualitativ, nicht quantitativ nachweisbar | M | Kontaktpunkt-Messung (Urs' Vorschlag, VTT ~10:18) als Startpunkt aufnehmen — **Requires validation** |
| G5 | Governance | Kein zusätzlicher HITL-Bezug für eine Intake-Triage-Komponente formal geprüft (Marco bestätigt aber implizit advisory-only: *"KI, der einfach mal … sichtet"*, nicht entscheidet) | Governance-Rahmen (ADR-0007) müsste explizit auf einen neuen Agenten-Typ angewendet werden, falls umgesetzt | L | Bei Sprint-Intake: HITL-Gate wie bei allen bestehenden Agenten verbindlich vorschreiben |
| G6 | Kontinuität | Kein formaler Vermerk im Backstage-"Review sessions on record" für dieses zweite Gespräch vor diesem PR | Governance-Nachvollziehbarkeit unvollständig | H | §6 dieser PR — neue Tabellenzeile + i18n-Einträge (Task 3) |

---

## 6. Bewertete Lösungsansätze & Empfehlungen (Evaluate solutions to address the ideas)

### 6.1 Idee 1 — "Zeit zurückgeben" differenzieren

**Bewertung:** Kein neuer Agent nötig. Die bestehende Delegations-Doktrin (Routinearbeit → Agenten, Entscheidung → Mensch) deckt den Mechanismus bereits ab (DCA/SBA/BMCA/ORSA). Was fehlt, ist die **Sprache**: die Produkt-Narrative muss die Unterscheidung "Verschwendung vs. legitime Bildschirmarbeit" explizit machen, statt implizit zu lassen.
**Empfehlung (H):** START-`ops`-Persona-Text erweitern, um diese Differenzierung aufzunehmen (umgesetzt in diesem PR, §Task 2).

### 6.2 Idee 2 — Prep/Perform/Recap als KPI-Rahmen

**Bewertung:** Drei Optionen wurden evaluiert:

| Option | Beschreibung | Aufwand | Empfehlung |
| ------ | ------------ | ------- | ---------- |
| A | Rein narrativ (Marketing-Text erweitern, keine neue Messgrösse) | Niedrig | **Gewählt für diesen PR** — konsistent mit Scope (Task 2 verlangt Text-Erweiterung, keine neue Metrik-Implementierung) |
| B | Neue Gold-Kennzahl `share_of_patient_facing_time` (prep/perform/recap-Anteil), gespeist aus Kontaktpunkt-Messung (Marco/Urs' Vorschlag) | Hoch (neue Datenquelle, neue Semantik-Modell-Kennzahl) | Für künftigen Sprint vorschlagen — **Requires validation**, ob Rohdaten (Kontaktpunkte je Rolle/Patient) überhaupt verfügbar sind |
| C | Qualitative Erweiterung der bestehenden BVA-Nutzenerzählung (kein neues Datenmodell) | Niedrig-Mittel | Ergänzend zu A, kein Widerspruch |

**Empfehlung (M):** Option A jetzt (dieser PR); Option B als Folge-Sprint-Kandidat mit vorgelagertem Datenverfügbarkeits-Assessment (analog G3).

### 6.3 Idee 3 — Intake-Triage-Assistent (discovered idea)

**Bewertung:** Dies ist die substanziellste neue Idee der Session. Sie folgt exakt dem etablierten Muster "advisory-only, HITL, kein PHI" und benötigt **keinen** neuen Namensraum-Konflikt (§2 Punkt 6 bestätigt). Vorschlag für eine künftige Sprint-Intake, **nicht** in diesem PR implementiert (ausserhalb des angefragten Scopes: Dokumentation, Text-Erweiterung, Deployment — keine neue Agenten-Implementierung):

- **Arbeitstitel:** Intake-Triage-Assistent (ITA) — sitzt konzeptionell vor/neben dem bestehenden Notaufnahme-Fluss (OOA-Signal → Bettenzuweisung), unterstützt die Kaderarzt/Kaderärztin-geführte Ersteinschätzung.
- **Kernfunktion:** Mustererkennung anhand von Untersuchungsmustern (nicht -inhalten) vergleichbarer historischer Fälle → früh-Indikator "kurzer Aufenthalt" vs. "komplexer/langer Fall"; Empfehlung zur Entlassplanung **ab Notaufnahme-Eintritt**, nicht erst nach Abteilungsübergabe.
- **Governance-Passform:** advisory-only, kein PHI (nur Untersuchungs-*Muster*-Metadaten, keine Befundinhalte — konsistent mit ADR-0016); Kaderarzt/Schichtleitung behält die Entscheidung (ADR-0007 HITL).
- **Nächster Schritt:** als Kandidat in einer künftigen Sprint-Planung aufnehmen (`docs/sprints/`), mit Datenverfügbarkeits-Assessment (G3) als Vorbedingung — **kein FR/NFR-Eintrag in `docs/PRD.md` in diesem PR**, da Scope hier Dokumentation + Narrative + Deployment ist, nicht Anforderungs-Aufnahme.

---

## 7. Artefakt-Traceability

| Aussage / Outcome | Repository-Artefakt |
| ------------------ | -------------------- |
| Erstes Marco-Rossi-Review, Kernfrage "Zeit für Patientenbetreuung" | [`2026-07-17-ama-hospital-ops-lead-review.md`](2026-07-17-ama-hospital-ops-lead-review.md) §3, §4 |
| `ops`-Persona (START), Datum 17.07.2026 für Marco Rossi | [`start-content.ts`](../../apps/hcc-app-fluent/src/workspaces/start/frontier/start-content.ts) `CHALLENGER_PERSONAS.ops.reviewers[2]` |
| Backstage-Roster, Marco-Rossi-Eintrag | [`BackstageNarrativeSections.tsx`](../../apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative/BackstageNarrativeSections.tsx) `PRACTITIONERS` |
| Backstage "Review sessions on record" (6 Sitzungen vor diesem PR) | [`BackstageNarrativeSections.tsx`](../../apps/hcc-app-fluent/src/workspaces/backstage/tabs/story/narrative/BackstageNarrativeSections.tsx) `REVIEW_SESSIONS` |
| Advisory-only / HITL-Doktrin | [`docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md`](../adr/0007-mvp-agent-runtime-and-hitl-release-gates.md) |
| Kein PHI / Metadaten-Ansatz | [`docs/adr/0016-no-phi-in-mvp-demo-scope.md`](../adr/0016-no-phi-in-mvp-demo-scope.md) |
| Kein Namenskonflikt: `signal-triage-agent` / `signal-agent` betreffen externe Hazard-Signale, nicht Patienten-Intake | [`agents/signal-triage-agent/AGENT.md`](../../agents/signal-triage-agent/AGENT.md), [`agents/signal-agent/AGENT.md`](../../agents/signal-agent/AGENT.md) |
| Bestehende 7-Agenten-Kette (OOA→BMCA→ORSA→SBA→DCA), inkl. Notaufnahme-Einordnung | `agents/{ooa,bmca,orsa,sba,dca}-agent/AGENT.md` |

---

## 8. Requires Validation

- Datenverfügbarkeit für eine künftige Intake-Triage-Komponente (Untersuchungsmuster historischer Fälle) — nicht geprüft (G3).
- Ob "Share of Time" / Prep-Perform-Recap als quantitative Gold-Kennzahl in einem künftigen Sprint operationalisiert werden soll (G4) — Marco selbst unsicher, ob einfach messbar.
- Ob die Datenschutz-Selbstblockade-Reflexion (§4.5) eine Anpassung am Onboarding-/Compliance-Playbook auslösen soll.
- Ob ein künftiger Intake-Triage-Assistent als eigenständiger Agent (`agents/<name>/`) oder als Erweiterung eines bestehenden Agenten (z. B. OOA) modelliert werden soll — bewusst offen gelassen, da ausserhalb des Scopes dieses PRs.

---

## 9. Kontinuität zum ersten Interview (17.07.2026)

Dieses Follow-up widerspricht keinem Befund des ersten Interviews, sondern **vertieft** ihn:

| Erstes Interview (17.07.2026) | Follow-up (10.08.2026) |
| ------------------------------ | ------------------------ |
| *"Wie bekommen wir ein System, das uns Zeit für Patientenbetreuung zurückgibt?"* (gemeinsame Kernfrage aller drei Reviewer) | Präzisiert zu Prep/Perform/Recap (§4.2) — die Frage wird operational, nicht ersetzt |
| Spezialisierte Teams — Personalausfall schwer kompensierbar | Nicht erneut vertieft in dieser Session — bleibt gültig |
| Gekoppelte OP-/Betten-/Personal-Steuerung als Kernschmerzpunkt (Ernst) | Ergänzt um einen vorgelagerten Hebel: Intake-Triage-Qualität beeinflusst alle drei nachgelagerten Steuerungsgrössen (§4.3) |
| "Fundamentally accurate"-Verdikt zum agentenbasierten Patientenfluss | Bestätigt erneut implizit durch Marcos Zustimmung zur Simulation (§4.3, VTT ~39:16) |

Diese Kontinuität wird in der Backstage-"Review sessions on record"-Tabelle als **separate, zweite Sitzung** (nicht als Überschreibung der ersten) geführt — siehe Task 3 dieses PRs.
