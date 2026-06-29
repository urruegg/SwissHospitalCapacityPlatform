# Sprint 08 Brainstorming - sql-kis-ingestion

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-29 |
| **Author** | GitHub Copilot |
| **Status** | Reviewed |
| **Previous Version** | 0.0.0 (new brainstorming artifact) |

## Stage

Superpowers Stage 1 `brainstorming` output for the Sprint 08 source SQL and
thin ingest slice (W1.1).

## Traceability

| Field | Value |
| ----- | ----- |
| Slice | `sql-kis-ingestion` |
| Parent sprint issue | #66 |
| Planned PR | `s08-source-sql` |
| Parent sprint document | [sprint-08-data-platform-resources-and-ingestion-pipeline.md](../sprint-08-data-platform-resources-and-ingestion-pipeline.md) |

## Problem

Sprint 08 needs a synthetic SQL source that represents the KIS entry point,
with one deterministic episode row for end-to-end walking-skeleton validation.

## Recommendation

Provision Azure SQL with private endpoint and seed using a deterministic script;
use metadata-only pseudonymized records and reject any PHI-bearing data.

## Acceptance Criteria

1. Azure SQL server and `kis` database deploy in `switzerlandnorth`.
2. Seed script inserts one deterministic `kis.Episode` row idempotently.
3. Dry-run mode returns expected seed payload for automated tests.
4. DNS dependency is explicit when private DNS zone ID is not provided.
