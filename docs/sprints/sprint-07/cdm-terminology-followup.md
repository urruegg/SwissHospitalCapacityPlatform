# Sprint 07 follow-up — CDM terminology alignment (Episode → Encounter)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-12 |
| **Author** | Urs Rüegg (with GitHub Copilot) |
| **Status** | Open (separate PR required) |
| **Previous Version** | — |

## Background

The Sprint 07 patient capacity data product spec ([docs/superpowers/specs/2026-06-12-patient-capacity-data-product-design.md](../../superpowers/specs/2026-06-12-patient-capacity-data-product-design.md), decision D-07) adopts Microsoft Healthcare CDM / HL7 FHIR R4 terminology. In FHIR, `EpisodeOfCare` denotes a **multi-Encounter care relationship** (e.g. a chronic-disease management programme), which is **not** what Sprint 06 documents meant when they said "episode".

Sprint 06 documents used "episode" to refer to a single hospitalisation, which is `Encounter` (`class=IMP`) in FHIR.

## Scope of the follow-up

A separate PR must:

1. Rename loose uses of "episode" to "encounter" (or "hospitalisation encounter") in:
   - `docs/PRD.md`
   - `docs/ARCHITECTURE.md`
   - `docs/SD.md`
   - `docs/DATA.md` (any pre-Sprint-07 prose still using "episode")
   - `docs/reviews/*-ama-sd-review.md` (only if pulled into a follow-up review)
2. Preserve `FR-*` / `NFR-*` IDs (no renames — that would force MAJOR doc bumps per `.github/copilot-instructions.md` §9).
3. Add a one-line glossary entry in `docs/DATA.md` clarifying `EpisodeOfCare` vs `Encounter`.

## Out of scope for this follow-up

- Renaming requirement IDs.
- Touching the Sprint 06 contracts `DC-ONB-PATIENT-v1` and `DC-ONB-CAPACITY-v1`.
- Reverting any decision recorded in `docs/adr/`.

## Acceptance criteria

- All Sprint-06-and-earlier prose uses "encounter" (or "hospitalisation encounter") where it refers to a single hospitalisation.
- Markdownlint and link checks pass.
- PR description references this follow-up note.
