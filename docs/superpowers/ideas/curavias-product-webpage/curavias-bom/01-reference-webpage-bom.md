# Step 1 — Reference Webpage Artefact BOM

**Reference:** *AI-Powered Solutions for Healthcare* — https://www.microsoft.com/en-us/health-solutions
**Purpose:** Deconstruct the Microsoft for Healthcare page into a reusable
Corporate-Design / Corporate-Identity (CD/CI) component inventory. Every artefact
below is a **pattern Curavias will reuse** (Step 4 fills them with Curavias content).

**Legend — Priority:** P0 = must-have for launch · P1 = important · P2 = enhancement.

---

## 1.1 Page-section artefacts (top → bottom)

| ID | Section artefact | Reference content | Reused for Curavias as | Media | Priority |
| -- | ---------------- | ----------------- | ---------------------- | ----- | -------- |
| REF-01 | Global navigation bar + product mega-menu | Solutions / Products menus, utility "Read the blog" | Sticky top nav: Plattform · Agenten · Erlebnisse · Sicherheit · Wert · Demo | — | P0 |
| REF-02 | Hero band | "Accelerate innovation and improve healthcare experiences" + primary CTA ("Experience Dragon Copilot") + secondary ("Watch the video") + hero visual | Curavias hero: positioning line, north-star subhead, "Demo ansehen" + "Video ansehen", hero animation | Image/video | P0 |
| REF-03 | Trust / value-pillar strip | "Achieve more with AI you can trust" — 4 tiles: Better experiences / insights / care / Empower workforce | KPI + value strip (3.5 Mio CHF · 127 % ROI · 7 Copiloten) | Icons | P0 |
| REF-04 | Alternating feature rows (image + text + "Learn more") | Increase value of data · Accelerate research · Safeguard data · Enhance patient experiences | Curavias capability rows: Vorschau · Erklärbarkeit · Human-in-the-Loop · Swiss residency | Image | P0 |
| REF-05 | Product showcase cards | Dragon Copilot · Dragon Medical One · PowerMic Mobile · Radiology — icon + title + desc + "Explore the product" | Seven-agent card grid (BMCA, OOA, DCA, ORSA, SBA, CSA, DQ) | Icon/image | P0 |
| REF-06 | Real-world impact / testimonial | Customer quote (Clinton Hull, MD) + stat counters (88 %, 22k) | Evidence band: review quotes + BVA stat counters (3.5M / 127 % / 7) | Portrait/quote | P1 |
| REF-07 | Products index / grid | "Products" listing | "Die drei Erlebnisse" grid + agent index | Icons | P1 |
| REF-08 | Closing CTA band | "Start achieving more in healthcare" → "Explore healthcare solutions" | "Nächste Schritte" CTA → Review-Session / Discovery / Roadmap | — | P0 |
| REF-09 | Social / follow bar | "Follow Microsoft" | Contact + MIH Zürich attribution | Social icons | P2 |
| REF-10 | Global footer | Microsoft universal footer (legal, privacy, sitemap) | Curavias footer + showcase disclaimer + "Powered by Microsoft · curavias.ch" | — | P0 |

---

## 1.2 Design-system artefacts (CD/CI to inherit)

| ID | Design artefact | Microsoft reference standard | Curavias adaptation | Priority |
| -- | --------------- | ---------------------------- | ------------------- | -------- |
| REF-DS-01 | Typography scale | Segoe UI family; large light-weight display headings; clear body hierarchy | Segoe UI / system stack; DE display headings | P0 |
| REF-DS-02 | Colour system | Microsoft blue primary, neutral greys, generous white space | Curavias teal→green brand + Microsoft blue accents; Swiss-cross red used sparingly | P0 |
| REF-DS-03 | Fluent components | Rounded cards, soft shadows, pill buttons, iconography | Fluent UI React components (matches app, Step 2) | P0 |
| REF-DS-04 | Grid & layout | 12-col responsive grid, full-bleed bands, max-width content | Same responsive grid | P0 |
| REF-DS-05 | Photography style | Real people, clinical/operational settings, warm & human | Swiss hospital operations stock (Brand Central) + generated illustrations | P1 |
| REF-DS-06 | Motion / video | Autoplay muted hero video, "Watch the video" pattern | Hero patient-path animation + agent micro-demos | P1 |
| REF-DS-07 | CTA pattern | Primary + secondary button pairing, "Explore the product" repeated | "Demo ansehen" / "Mehr erfahren" pairing | P0 |
| REF-DS-08 | Accessibility | WCAG 2.1 AA, alt text, keyboard nav, contrast | WCAG 2.1 AA target; DE/EN alt text | P0 |
| REF-DS-09 | Responsive breakpoints | Mobile-first; card grids reflow to 1-col | Same; agent grid 4→2→1 | P0 |
| REF-DS-10 | SEO / metadata pattern | Title, meta description, OpenGraph, structured headings | Curavias metadata (Step 4 copy deck) | P1 |

---

## 1.3 Reusable content-block types (component library)

| ID | Block type | Description | Instances needed on Curavias site |
| -- | ---------- | ----------- | --------------------------------- |
| REF-CB-01 | Hero block | Headline + subhead + dual CTA + media | 1 |
| REF-CB-02 | Stat-counter tile | Big number + label | 3–4 (KPIs + BVA) |
| REF-CB-03 | Feature row | Image left/right + heading + copy + link | 4–6 |
| REF-CB-04 | Product/agent card | Icon + title + one-liner + link | 7 (agents) + 3 (experiences) |
| REF-CB-05 | Quote / testimonial card | Portrait + quote + attribution | 2–3 (reviews) |
| REF-CB-06 | Comparison table | Two-column "before/after" | 1 (7 decisions) |
| REF-CB-07 | Trust list | Icon bullets | 1 (6 sovereignty pillars) |
| REF-CB-08 | Data/value table | Rows + emphasised totals | 1 (BVA) |
| REF-CB-09 | CTA band | Headline + button on colour field | 2 (mid + closing) |
| REF-CB-10 | Disclaimer banner | Highlighted advisory notice | 1 (persistent) |

---

## 1.4 Gap notes vs. reference

- Reference page is **product-marketing** led (Dragon Copilot). Curavias is a
  **showcase** — every product/agent card must carry advisory-only + synthetic-data framing.
- Reference uses named real customers; Curavias reviews must use **synthetic personas**.
- Add a **persistent disclaimer banner** (REF-CB-10) that the reference page does not have.
