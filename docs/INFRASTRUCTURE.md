# Infrastructure Baseline

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-04 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | n/a |

## Purpose

Define the infrastructure baseline for Sprint 3 SIT and PROD provisioning and promotion workflows.

## Current Scope

- Root deployment entrypoint: infra/main.bicep
- Foundation module: infra/modules/platform-foundation/main.bicep
- Environment parameters:
  - infra/environments/sit.bicepparam
  - infra/environments/prod.bicepparam
- CI validation workflow: .github/workflows/ci-infra-validate.yml
- SIT deployment workflow: .github/workflows/cd-infra-deploy-sit.yml
- PROD deployment workflow: .github/workflows/cd-infra-deploy-prod.yml

## Next Expansion

Planned module domains:

- identity
- network
- observability
- data-platform
- ai-platform
- integration
