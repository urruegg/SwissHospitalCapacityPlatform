# Swiss Hospital Capacity Platform

| Field | Value |
| ----- | ----- |
| Version | 1.0.0 |
| Date | 2026-06-01 |
| Author | Urs Rueegg |
| Status | Draft |
| Previous Version | 0.1.0 (title-only placeholder) |

## Executive Summary

Swiss Hospital Capacity Platform is a governance-first blueprint for improving
patient flow and bed-capacity decisions across Swiss healthcare operations.

The solution combines:
1. Data interoperability and analytics for capacity visibility.
2. AI-assisted forecasting and discharge coordination.
3. GitHub-native, auditable delivery workflows for architecture, compliance,
	and implementation control.

The MVP is intentionally focused on a single-provider deployment with strict
Swiss in-country processing guardrails for PHI-sensitive workloads.

## Strategic Outcomes

1. Better occupancy and discharge planning through near-real-time capacity insight.
2. Faster, more consistent operational decisions supported by explainable AI outputs.
3. Stronger compliance posture through explicit traceability from requirements
	to architecture, security, and control evidence.

## Delivery Model (At a Glance)

1. Governance and requirements are documented first.
2. Agent-based workflows generate and review solution artefacts.
3. Security, compliance, and test evidence are built into the release path.

## Key Artefacts

| Artefact | Why it matters for stakeholders | Link |
| ----- | ----- | ----- |
| Product Requirements | Business scope, FR and NFR commitments, traceability baseline | [docs/PRD.md](docs/PRD.md) |
| Solution Architecture | MVP architecture decisions, service boundaries, and constraints | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| AI Design | AI scope, safety boundaries, residency constraints, and operations | [docs/AI.md](docs/AI.md) |
| Security Baseline | Zero Trust pattern and requirement-level validation | [docs/SECURITY.md](docs/SECURITY.md) |
| Compliance Baseline | Swiss control mappings, evidence model, and release checks | [docs/COMPLIANCE.md](docs/COMPLIANCE.md) |
| Data Design | Data domains, contracts, retention model, and requirement mapping | [docs/DATA.md](docs/DATA.md) |
| Solution Design Draft | MVP implementation view and phased delivery framing | [docs/SD.md](docs/SD.md) |
| Agent Registry | Operational view of agent responsibilities and side-effect controls | [AGENTS.md](AGENTS.md) |
| Sprint Trace | Detailed Sprint 02 refinement record and outcomes | [sprints/sprint-02-prd-refine-detailed-reviews.md](sprints/sprint-02-prd-refine-detailed-reviews.md) |
