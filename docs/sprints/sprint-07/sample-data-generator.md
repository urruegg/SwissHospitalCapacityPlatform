# Sprint 07 Sample Data Generator Scope

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-12 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | 0.0.0 (new scope artifact) |

## Purpose

Define Sprint 07 scope for a sample data generator that supports development,
validation, and review of the metadata-only planning model.

## Generator Requirements

1. Produce synthetic episode demand records with pseudonymised identifiers.
2. Produce synthetic bed or station supply records with metadata attributes.
3. Produce optional recommendation test fixtures for match validation.
4. Exclude direct PII from generated planning datasets.

## Quality and Validation

1. Deterministic generation mode for reproducible tests.
2. Schema conformance checks against Sprint 07 data contracts.
3. Completeness threshold checks for mandatory metadata fields.
4. Dataset summary output (row counts, null checks, field coverage).

## Compliance and Boundary Conditions

1. Keep separation clear:
   - KIS identity layer (outside generated planning dataset)
   - Planning metadata layer (inside generated dataset)
2. Use pseudonymised identifiers only.
3. Provide evidence links in Sprint checkpoints and PR validation sections.

## Output Artifacts

1. Synthetic demand dataset sample.
2. Synthetic supply dataset sample.
3. Generation configuration and seed notes.
4. Validation result summary.
