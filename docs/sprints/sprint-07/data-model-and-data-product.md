# Sprint 07 Data Model and Data Product Scope

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-12 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 0.0.0 (new scope artifact) |

## Purpose

Define Sprint 07 scope for the episode-based data model and first data product,
aligned to AMA review recommendations.

## Model Principles

1. Control unit is Hospitalisation Episode (not patient).
2. Matching model compares:
   - Demand (episode metadata)
   - Supply (bed or station metadata)
3. Planning platform is metadata-only and excludes direct PII.

## Data Product Minimum Scope

1. Contract-first schema for episode demand metadata.
2. Contract-first schema for bed or station supply metadata.
3. Contract-first schema for match recommendation output with explainability fields.
4. Data quality checks:
   - Required field validation
   - Completeness thresholds
   - Schema conformance checks

## Governance and Compliance Expectations

1. No PII attributes in planning product schema.
2. Pseudonymised identifier strategy documented.
3. Traceability from requirement to schema contract to validation evidence.
4. Alignment with review findings in:
   - [docs/reviews/2026-06-10-ama-sd-review.md](../../reviews/2026-06-10-ama-sd-review.md)
   - [docs/reviews/2026-06-09-ama-sd-review.md](../../reviews/2026-06-09-ama-sd-review.md)
