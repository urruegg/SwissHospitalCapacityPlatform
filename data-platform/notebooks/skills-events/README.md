# Skills-events near-real-time lane (Sprint 23 WS-A4, #255)

Fabric Spark transforms for the **narrow near-real-time skills-events lane** the
WS-A4 Eventstream module (design D4) feeds. This lane is deliberately separate from
the batch org/skills master-data medallion (`skills-evidence/`): batch evidence is
periodic HRIS/LMS master data, whereas these three events must move faster than the
next batch load.

## The three event kinds (design D4)

The Eventstream routes by the `eventKind` message property and admits **only** these
three kinds (enforced by
`infra/modules/integration-orchestration/skills-eventstream/main.bicep`):

| `eventKind` | Meaning | Silver/Gold effect |
| --- | --- | --- |
| `credential-expiry` | A certification/credential lapsed | `credentialValid = false` so the associated assertion stops counting |
| `consent-grant-or-revoke` | A Work-ID consent decision | `grant` sets `workerGln` + `consentScope`; `revoke` **clears both** (GLN promotion removed) |
| `newly-confirmed-assertion` | An employer confirmed a self-declared skill | `confirmed = true` (the L0 → L1 transition) |

## Data contract — `DC-SKILL-EVENT-v1`

New, **additive** contract (`data/synthetic/schema/dc-skill-event-v1.schema.json`)
that complements — and does **not** modify — the batch `DC-SKILL-EVIDENCE-v1`
contract. The `sourceMode` (live | simulated) + `trustTier` badge travels in the
contract, is preserved through Bronze/Silver, and surfaces on the gold fact — never
invented downstream. Synthetic / no-PHI only (ADR-0013 / ADR-0016).

## Files

| File | Layer | Purpose |
| --- | --- | --- |
| `../../scripts/skills-events/normalize.py` | — | `build_event` factory (badge + provenance) + `envelope` wrapper; `EVENT_KINDS`, `dedup_key`. |
| `../../scripts/skills-events/skill_events_synth.py` | — | Dependency-free seeder: parses the three event fixtures into a `DC-SKILL-EVENT-v1` envelope; `--dry-run` schema-validates. The payload a Container Apps service publishes to the Eventstream (never a GitHub workflow). |
| `ingest_bronze_skill_events.py` | Bronze | `bronze_path(event_kind, date)` convention + `ingest_bronze_skill_events(spark, records)` → `bronze.skill_events_raw` at `Files/bronze/skills-events/`. |
| `build_silver_skill_events.py` | Silver | PHI/consent gate: `validate_event` + `consent_shape_error` (deny-by-default), `enforce_consent_gate` (revoke clears GLN promotion), `split_quarantine` → `silver.skill_events` + `silver.skill_events_quarantine`. |
| `build_gold_skill_events.py` | Gold | Separate `skillevt_*` star spine: `skillevt_fact_event` + `skillevt_dim_source` + `skillevt_dim_kind`, carrying the `skillevt_data_mode` badge. |
| `tests/test_skill_events_pure.py` | — | Spark-free unit tests: bronze path, silver gate (quarantine + consent revoke + credential validity), gold badge propagation. |

## Why a separate `skillevt_*` gold spine

Like the `external-signals` `ext_*` spine, the skills-events gold tables are **not**
Direct-Lake tables in the capacity-dashboard semantic model, so they are **not** part
of the derived gold contract (`verify_gold_schema.contract_tables`) and do not affect
that parity gate. Semantic-model surfacing (a live-vs-simulated event measure) is a
documented follow-up.

## Conventions

* Pure functions are unit-tested without Spark (external-signals / CSA pattern);
  `run()` executes only inside the Fabric Spark runtime.
* The consent-revocation invariant is enforced **defensively** at the silver gate:
  even if an upstream payload still carried a GLN on a `revoke`, silver nulls it, so a
  revoked worker can never be promoted (COMPLIANCE.md §Sprint 23; FR-SKILL-003).
* Synthetic / no-PHI only (ADR-0013 / ADR-0016).

## Run locally

```bash
python -m pytest data-platform/notebooks/skills-events/tests -v
python -m pytest data-platform/scripts/skills-events/tests -v
# seeder dry-run (schema-validates the three event kinds)
cd data-platform/scripts/skills-events && PYTHONPATH=. python skill_events_synth.py --dry-run
```

## Run in Fabric (end-to-end, `approved-to-apply` gated)

The lane runs as `ingest_bronze_skill_events` → `build_silver_skill_events` →
`build_gold_skill_events`. In production the Bronze layer is fed live by the WS-A4
Eventstream (Event Hub → Eventstream → `Files/bronze/skills-events/`); the committed
seeder reproduces the same envelopes for offline/demo replay. The end-to-end Fabric
run needs the WS-A landing zone + Eventstream wiring + `approved-to-apply`.
