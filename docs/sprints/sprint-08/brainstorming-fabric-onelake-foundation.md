# Sprint 08 Brainstorming - fabric-onelake-foundation

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-29 |
| **Author** | GitHub Copilot |
| **Status** | Reviewed |
| **Previous Version** | 0.0.0 (new brainstorming artifact) |

## Stage

Superpowers Stage 1 `brainstorming` output for the Sprint 08 Fabric and OneLake
foundation slice (W1.2).

## Traceability

| Field | Value |
| ----- | ----- |
| Slice | `fabric-onelake-foundation` |
| Parent sprint issue | #66 |
| Planned PR | `s08-fabric-foundation` |
| Parent sprint document | [sprint-08-data-platform-resources-and-ingestion-pipeline.md](../sprint-08-data-platform-resources-and-ingestion-pipeline.md) |

## Problem

Sprint 08 requires a minimal Fabric foundation in SIT that can receive mirrored
SQL KIS data and provide bronze, silver, and gold lakehouse schemas with Swiss
residency constraints.

## Recommendation

Use Bicep for Fabric capacity provisioning plus a post-deploy script for
workspace/lakehouse/mirror item creation, with strict SIT-only scope and no
PROD rollout in this slice.

## Acceptance Criteria

1. Fabric capacity resource deploys in `switzerlandnorth`.
2. Workspace and lakehouse are created with deterministic naming.
3. Mirror setup flow is documented and test-covered for payload generation.
4. No deploy/delete bypasses `approved-to-apply`.
