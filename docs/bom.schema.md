# BOM Schema — Showcase Evidence Bill of Materials

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-09 |
| **Author** | Urs Rüegg |
| **Status** | Draft for review |
| **Previous Version** | — (initial) |

Human-readable contract for [`docs/bom.yaml`](bom.yaml), the seed Bill-of-Materials
catalog of the Sprint 14 Showcase Evidence data product. The machine contract is
[`data/evidence/schema/bom.schema.json`](../data/evidence/schema/bom.schema.json)
(items) + [`dependencies.schema.json`](../data/evidence/schema/dependencies.schema.json)
(edges). Region-availability facts are kept separately in
[`docs/region-availability.yaml`](region-availability.yaml).

## File shape

```yaml
version: 1.0.0
items:
  - id: bom-<slug>
    name: <display name>
    type: <resource type>
    category: <category>
    sku: <sku>                       # optional
    realisesRequirements: [FR-…, NFR-…]   # optional
    governedByAdrs: [ADR-####]            # optional
    dependsOn:                            # optional
      - to: bom-<other>
        type: <edge type>
```

## Item fields

| Field | Required | Rule |
| --- | --- | --- |
| `id` | yes | kebab-case, matches `^bom-[a-z0-9-]+$`, unique |
| `name` | yes | human display name |
| `type` | yes | resource type (e.g. `Microsoft.Fabric/lakehouse`) |
| `category` | yes | one of `data`, `ai`, `app`, `integration`, `security`, `platform`, `governance` |
| `sku` | no | SKU string where meaningful |
| `realisesRequirements` | no | list of `FR-*` / `NFR-*` IDs from [`docs/PRD.md`](PRD.md) |
| `governedByAdrs` | no | list of `ADR-####` IDs from [`docs/adr/`](adr/) |
| `dependsOn` | no | list of dependency edges (see below) |

## Dependency edge fields

| Field | Required | Rule |
| --- | --- | --- |
| `to` | yes | target `bom-*` id (must exist in the same file) |
| `type` | yes | one of `requires`, `hosts`, `grounds`, `binds`, `governs` |

Edges are emitted to `data/evidence/dependencies.json` as directed
`{fromId, toId, type}` rows and become the dependency-edge cards on the
presenter whiteboard (design spec §5).

## Provenance

The parser attaches `sourcePath` (`docs/bom.yaml`) and `sourceCommit` to every
emitted item and edge. Every BOM item should have at least one matching
region-availability fact in `docs/region-availability.yaml`; the readiness
scoring rules (see `docs/adr/0021-readiness-scoring-rules.md`) depend on it.

## Validate locally

```bash
python -m scripts.evidence.publish --repo-root . --out data/evidence
```
