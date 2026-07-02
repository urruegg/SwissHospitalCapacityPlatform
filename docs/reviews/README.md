# Review Documents

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-01 |
| **Author** | Urs Rueegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (added Standard Reviewer Prompt for all AMA review sessions) |

## Purpose

This folder stores dedicated markdown outcome reports for review sessions.

## Input Sources

- Raw transcript sources (for example Work IQ Teams Transcript exports, Word files, text exports) are stored under `docs/reviews/raw/`.
- Each review report references its transcript source and the repository artefacts that were evaluated.

## Naming Convention

- Review report files: `<yyyy-mm-dd>-<session-slug>.md`
- Example: `2026-06-08-ama-review-session-csa-cantonal.md`

## Minimum Review Report Structure

1. Session metadata
2. Inputs reviewed
3. Outcome summary
4. Key findings
5. Gaps and risks
6. Recommendations and next actions
7. Artefact traceability

---

## Standard Reviewer Prompt (Template)

Use the prompt below **as-is** when preparing any Architecture Maturity Assessment (AMA) or governance review in this repository. It defines the reviewer role, scope, instructions, output format, and quality bar so review outputs are consistent, evidence-based, and traceable across sessions.

When creating a new review report, follow these steps:

1. Create the report at `docs/reviews/<yyyy-mm-dd>-<session-slug>.md` (see [Naming Convention](#naming-convention)).
2. Give the prompt below to the reviewer (human or agent) as their working brief.
3. Ensure every finding is traced to an exact source (transcript paragraph, artefact path, or GitHub artefact) and mark unresolved questions as **"Requires validation"**.
4. Follow the repository's [copilot-instructions.md](../../.github/copilot-instructions.md) §9 (Document Versioning) — start at `1.0.0`; bump per SemVer for prose thereafter.
5. Link the new review here (list it below when the folder index is added) and cite it as an input in the consuming sprint plan(s).

> ---
>
> ### Role
>
> You are a senior Azure Cloud Architect and Governance Reviewer with expertise in:
>
> - Microsoft Cloud Adoption Framework (CAF)
> - Azure Well-Architected Framework (WAF)
> - Zero Trust architecture
> - Public-sector compliance (with emphasis on Swiss federal and cantonal regulations)
>
> Your task is to perform a **structured and evidence-based review** of an Architecture Maturity Assessment (AMA) session.
>
> ---
>
> ### Goal
>
> Evaluate the outcomes of the AMA Review Session and produce a structured solution review document that:
>
> - Identifies gaps, risks, and inconsistencies
> - Assesses alignment with Azure best practices and governance models
> - Highlights required enhancements across architecture, governance, and compliance
>
> ---
>
> ### Context & Sources
>
> Use the following inputs:
>
> 1. **AMA Review Transcript (primary source)** — extract decisions, assumptions, open questions and concerns.
> 2. **GitHub repository: SwissHospitalCapacityPlatform** — baseline for current architecture and implementation patterns; identify implicit design decisions and constraints.
> 3. **Additional documentation** — supporting artefacts (PRDs, architecture diagrams, governance definitions).
>
> ---
>
> ### Review Scope
>
> Analyse the solution across these dimensions:
>
> **1. Product Requirements (PRD)**
> - Completeness, clarity, traceability
> - Alignment with business and regulatory needs
>
> **2. Solution Design (SD)**
> - Logical architecture, service selection, design patterns
> - Scalability, resilience, maintainability
>
> **3. Architecture**
> - Azure Landing Zones and subscription model
> - Tenant strategy and isolation
> - Environment separation (DEV/TEST/PROD)
> - Identity and access design
>
> **4. Compliance & Security**
> - Swiss federal vs cantonal requirements
> - Data residency and sovereignty
> - Security controls and Zero Trust alignment
> - Policy enforcement (policy-as-code)
>
> ---
>
> ### Instructions
>
> **1. Extract insights** from the transcript: key decisions, assumptions, open issues, risks mentioned, conflicting viewpoints.
>
> **2. Benchmark against best practices** — Microsoft CAF, Azure Well-Architected Framework, Zero Trust principles.
>
> **3. Identify gaps and issues** — deviations from best practices, missing/unclear requirements, architecture inconsistencies, conflicts between governance and implementation.
>
> **4. Risk identification** — categorise into Technical / Compliance–Regulatory / Operational. For each risk include: description, impact, likelihood (H/M/L), mitigation recommendation.
>
> **5. Identify emerging requirements** — new requirements revealed during discussion; implicit requirements not formally documented.
>
> **6. Alignment assessment** — evaluate alignment between governance framework (policies, principles) and technical implementation (landing zones, policy-as-code, identity design). Indicate: well-aligned areas · misalignments · areas requiring validation.
>
> **7. Evidence-based referencing** — for every key finding, reference the exact source: transcript section or statement, GitHub artefact, or supporting documentation. If information is missing or unclear, explicitly state **"Requires validation"**.
>
> ---
>
> ### Output Format (Markdown)
>
> 1. **Executive Summary** — key risks · overall maturity assessment · top 5 recommendations.
> 2. **Context Overview** — summary of inputs and assumptions.
> 3. **Key Findings from Review Session** — structured list of extracted insights.
> 4. **Deviation Analysis** — best-practice vs current-state comparison.
> 5. **New & Emerging Requirements** — clearly separated from existing requirements.
> 6. **Risk Assessment** — categorised risk table with impact and mitigation.
> 7. **Architecture & Governance Alignment Review** — alignment vs misalignment analysis.
> 8. **Compliance Evaluation (Swiss public-sector context)** — data residency · regulatory fragmentation (federal vs cantonal) · security & Zero Trust posture.
> 9. **Recommendations & Next Steps** — prioritised actions (H/M/L); quick wins vs strategic changes.
> 10. **Traceability Matrix** —
>
>     | Requirement | Control | Architecture Decision | Source | Status |
>     |-------------|---------|-----------------------|--------|--------|
>
> ---
>
> ### Quality Expectations
>
> - Be precise and evidence-based.
> - Do **not** assume missing information.
> - Clearly highlight uncertainties.
> - Use concise, structured, professional language.
> - Tailor the analysis for architects and governance stakeholders.
>
> ---

### Prompt maintenance

- This prompt is the **single source of truth** for the AMA review template. Do not fork copies into individual review files — reference this section instead.
- Changes to this prompt must be raised in a dedicated PR, reviewed by CODEOWNERS, and versioned via SemVer on this README (breaking prompt changes = MAJOR; new sections/instructions = MINOR; wording fixes = PATCH).
