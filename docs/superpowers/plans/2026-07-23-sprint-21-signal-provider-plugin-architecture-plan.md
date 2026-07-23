# Signal-Provider Plugin Architecture & Trust Badges Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor the Sprint 21 external-signals lane into a manifest-driven `SignalProvider` plugin architecture with swappable Live/Simulated/Internal bindings, a data-driven live-vs-simulated trust badge, and Azure Container Apps-hosted ingestion (not GitHub Actions).

**Architecture:** Each channel is a provider = a schema-validated `provider.yaml` manifest + a small code surface (`parse.py` plus one or more of `live.py` / `simulator.py` / `internal.py`). A `registry` auto-discovers and validates manifests; a `provider_runner` selects the active binding (with live→simulated fallback), stamps provenance, and emits `DC-EXT-SIGNAL-v1` records. The active binding flows `provenance.activeBinding → gold.ext_dim_source.dataMode → semantic-model measures → board badge`. Ingestion/simulation run as an Azure Container Apps provider-runner publishing to Event Hub/Eventstream; GitHub Actions is CI-only.

**Tech Stack:** Python 3.12 (stdlib-only; PyYAML for manifests), `unittest`, JSON Schema (manual dependency-free checks), Bicep (UC-output infra), Fabric medallion notebooks + Direct Lake semantic model (TMDL), GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-07-23-sprint-21-signal-provider-plugin-architecture-design.md`

---

## Local environment note (this machine)

- Run Python with `python` locally (Windows). CI uses `python3`.
- The `.githooks/pre-commit` hook calls `python3`, which on this box resolves to a broken Windows Store alias. A working shim was created this session at `$env:TEMP\py3shim\python3.exe` with `PYTHONHOME=C:\Python314`; prepend that dir to `PATH` before `git commit` so the hook runs. Both gates can also be run manually:
  - Mojibake: `python scripts/lint/check_mojibake.py --staged`
  - Markdownlint: `npx --yes markdownlint-cli2 "<file.md>"`
- Test suite (from repo root):

  ```bash
  cd data-platform/scripts/external-signals
  PYTHONPATH=. python -m unittest discover -s tests -v
  ```

---

## File Structure

Plugin **code** lives under the existing Python root `data-platform/scripts/external-signals/` (so `PYTHONPATH=.` imports keep working). Non-Python service **config** (Bicep, activator, eventstream) lives under `data-platform/external-signals/`. Manifests are co-located with provider code so the registry auto-discovers them.

```text
data-platform/scripts/external-signals/
  providers/
    _schema/provider.schema.json         # NEW - manifest JSON Schema
    registry.py                          # NEW - discovery + validation + catalog rows
    runner.py                            # NEW - binding selection, fallback, provenance stamping
    __init__.py                          # NEW
    <sourceId>/
      provider.yaml                      # NEW - manifest
      parse.py                           # NEW - raw -> DC-EXT-SIGNAL-v1 (moved from connectors/)
      live.py                            # NEW - external+live channels only
      simulator.py                       # NEW - every external channel
      internal.py                        # NEW - internal channels only
      __init__.py                        # NEW
  normalize.py                           # MODIFY - add provenance fields (activeBinding/fellBackFrom/channelKind)
  connectors/                            # DELETE after parse bodies move to providers/<id>/parse.py
  signals_synth.py                       # MODIFY - build from registry providers, not hard-coded connector list
  tests/
    _util.py                             # MODIFY - add load_provider_fixture helper
    test_registry.py                     # NEW
    test_providers.py                    # NEW (replaces test_connectors.py)
    test_simulators.py                   # NEW
    test_internal.py                     # NEW
    test_runner_fallback.py              # NEW
    test_badge_propagation.py            # NEW
    fixtures/                            # existing raw fixtures reused/extended

data-platform/notebooks/external-signals/
  build_silver_signals.py                # MODIFY - carry provenance.activeBinding
  build_gold_signals.py                  # MODIFY - ext_dim_source.dataMode/trustTier/lastLiveAt/fellBackFrom

data-platform/external-signals/
  provider-runner/                       # NEW - Container App Bicep + config
    main.bicep
    README.md

data-platform/fabric/semantic-models/external-signals/   # MODIFY - badge measures (path confirmed in Task 12)

.github/workflows/
  external-signals.yml                   # MODIFY - new test files + manifest validation
  ext-signal-poll.yml                    # DELETE - ingestion/simulation move to Azure provider-runner

docs/
  PRD.md                                 # MODIFY - FR-EXT-015..020 + NFR-EXT-PLG-001/002 + matrix
  DATA.md                                # MODIFY - provenance.activeBinding fields + ext_dim_source.dataMode
  adr/0036-external-trigger-governance.md# MODIFY - plugin architecture + badge + Azure-hosted ingestion
AGENTS.md                                # MODIFY - reconcile ingestion-hosting note
agents/data-quality-agent/AGENT.md       # MODIFY - manifest/activeBinding/dataMode/licence gate
agents/data-quality-agent/golden-tasks.md# MODIFY - fixture for new gate
```

---

## Task 1: Manifest JSON Schema

**Files:**
- Create: `data-platform/scripts/external-signals/providers/_schema/provider.schema.json`
- Create: `data-platform/scripts/external-signals/providers/__init__.py` (empty)
- Test: `data-platform/scripts/external-signals/tests/test_registry.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_registry.py`:

```python
import json
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
SCHEMA = SCRIPTS_DIR / "providers" / "_schema" / "provider.schema.json"


class TestManifestSchema(unittest.TestCase):
    def test_schema_exists_and_declares_required_keys(self):
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        required = set(doc["required"])
        self.assertTrue(
            {"sourceId", "authority", "trustTier", "channelKind",
             "hazardTypes", "defaultMode", "licence", "providerVersion"} <= required
        )

    def test_mode_and_kind_enums(self):
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(
            set(doc["properties"]["channelKind"]["enum"]), {"external", "internal"}
        )
        self.assertEqual(
            set(doc["properties"]["defaultMode"]["enum"]),
            {"live", "simulated", "internal"},
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest tests.test_registry -v`
Expected: FAIL (schema file does not exist → `FileNotFoundError`).

- [ ] **Step 3: Write the schema**

Create `providers/_schema/provider.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SignalProvider manifest",
  "type": "object",
  "additionalProperties": false,
  "required": ["sourceId", "authority", "trustTier", "channelKind",
               "hazardTypes", "defaultMode", "licence", "providerVersion"],
  "properties": {
    "sourceId": {"type": "string", "pattern": "^[a-z0-9-]+$"},
    "authority": {"type": "string"},
    "trustTier": {"type": "string", "enum": ["A", "B", "C"]},
    "channelKind": {"type": "string", "enum": ["external", "internal"]},
    "hazardTypes": {"type": "array", "items": {"type": "string"}, "minItems": 1},
    "defaultMode": {"type": "string", "enum": ["live", "simulated", "internal"]},
    "fallbackMode": {"type": "string", "enum": ["simulated"]},
    "cadenceSeconds": {"type": "integer", "minimum": 1},
    "endpoint": {"type": "string"},
    "licence": {"type": "string", "minLength": 1},
    "providerVersion": {"type": "string"},
    "scenarioMap": {"type": "object"}
  }
}
```

Create empty `providers/__init__.py`.

- [ ] **Step 4: Run test to verify it passes**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest tests.test_registry -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/providers/_schema/provider.schema.json \
        data-platform/scripts/external-signals/providers/__init__.py \
        data-platform/scripts/external-signals/tests/test_registry.py
git commit -m "feat(external-signals): add SignalProvider manifest schema"
```

---

## Task 2: Registry (discover + validate + catalog rows)

**Files:**
- Create: `data-platform/scripts/external-signals/providers/registry.py`
- Create: `data-platform/scripts/external-signals/providers/sed/provider.yaml` (first real manifest, used as a discovery fixture)
- Create: `data-platform/scripts/external-signals/providers/sed/__init__.py` (empty)
- Test: `data-platform/scripts/external-signals/tests/test_registry.py` (extend)

- [ ] **Step 1: Write the failing test (append to `tests/test_registry.py`)**

```python
from providers.registry import (
    load_manifest, validate_manifest, discover, catalog_rows, ProviderSpec,
)


class TestRegistry(unittest.TestCase):
    def test_discover_finds_sed_and_validates(self):
        specs = discover()
        by_id = {s.source_id: s for s in specs}
        self.assertIn("sed", by_id)
        self.assertIsInstance(by_id["sed"], ProviderSpec)
        self.assertEqual(by_id["sed"].channel_kind, "external")
        self.assertEqual(by_id["sed"].default_mode, "live")

    def test_invalid_manifest_reports_errors(self):
        errors = validate_manifest({"sourceId": "x"})  # missing required keys
        self.assertTrue(errors)

    def test_catalog_rows_shape(self):
        rows = catalog_rows(discover())
        sed = next(r for r in rows if r["sourceId"] == "sed")
        self.assertEqual(
            set(sed) >= {"sourceId", "authority", "trustTier", "defaultMode", "channelKind"},
            True,
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest tests.test_registry -v`
Expected: FAIL (`ModuleNotFoundError: providers.registry`).

- [ ] **Step 3: Write the sed manifest**

Create `providers/sed/provider.yaml`:

```yaml
sourceId: sed
authority: SED-ETH
trustTier: A
channelKind: external
hazardTypes: [earthquake]
defaultMode: live
fallbackMode: simulated
cadenceSeconds: 300
endpoint: https://eida.ethz.ch/fdsnws/event/1/query
licence: SED-ETH-open-data
providerVersion: sed-2.0.0
scenarioMap:
  earthquake: {template: F1, lageTier: 3}
```

Create empty `providers/sed/__init__.py`.

- [ ] **Step 4: Write the registry**

Create `providers/registry.py`:

```python
"""Discover, validate, and catalog SignalProvider manifests (stdlib + PyYAML)."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import yaml

PROVIDERS_DIR = Path(__file__).resolve().parent
SCHEMA_PATH = PROVIDERS_DIR / "_schema" / "provider.schema.json"


@dataclass(frozen=True)
class ProviderSpec:
    source_id: str
    authority: str
    trust_tier: str
    channel_kind: str
    hazard_types: list[str]
    default_mode: str
    licence: str
    provider_version: str
    fallback_mode: str | None = None
    cadence_seconds: int | None = None
    endpoint: str | None = None
    scenario_map: dict = field(default_factory=dict)
    directory: Path | None = None


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def validate_manifest(doc: dict, schema: dict | None = None) -> list[str]:
    schema = schema or _schema()
    errors: list[str] = []
    for key in schema.get("required", []):
        if key not in doc:
            errors.append(f"missing required key: {key}")
    for key, spec in schema.get("properties", {}).items():
        if key in doc and "enum" in spec and doc[key] not in spec["enum"]:
            errors.append(f"{key}={doc[key]!r} not in {spec['enum']}")
    extra = set(doc) - set(schema.get("properties", {}))
    if schema.get("additionalProperties") is False and extra:
        errors.append(f"unexpected keys: {sorted(extra)}")
    # channel/mode coherence
    if doc.get("channelKind") == "internal" and doc.get("endpoint"):
        errors.append("internal channel must not declare endpoint")
    return errors


def load_manifest(path: Path, schema: dict | None = None) -> ProviderSpec:
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    errors = validate_manifest(doc, schema)
    if errors:
        raise ValueError(f"invalid manifest {path}: {errors}")
    return ProviderSpec(
        source_id=doc["sourceId"], authority=doc["authority"],
        trust_tier=doc["trustTier"], channel_kind=doc["channelKind"],
        hazard_types=list(doc["hazardTypes"]), default_mode=doc["defaultMode"],
        licence=doc["licence"], provider_version=doc["providerVersion"],
        fallback_mode=doc.get("fallbackMode"),
        cadence_seconds=doc.get("cadenceSeconds"),
        endpoint=doc.get("endpoint"), scenario_map=doc.get("scenarioMap", {}),
        directory=path.parent,
    )


def discover(providers_dir: Path = PROVIDERS_DIR) -> list[ProviderSpec]:
    schema = _schema()
    specs: list[ProviderSpec] = []
    for manifest in sorted(providers_dir.glob("*/provider.yaml")):
        specs.append(load_manifest(manifest, schema))
    return specs


def catalog_rows(specs: list[ProviderSpec]) -> list[dict]:
    return [
        {
            "sourceId": s.source_id, "authority": s.authority,
            "trustTier": s.trust_tier, "channelKind": s.channel_kind,
            "defaultMode": s.default_mode, "hazardTypes": s.hazard_types,
            "providerVersion": s.provider_version, "licence": s.licence,
        }
        for s in specs
    ]
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest tests.test_registry -v`
Expected: PASS (all registry tests). Requires PyYAML: `python -m pip install pyyaml` if missing.

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/external-signals/providers/registry.py \
        data-platform/scripts/external-signals/providers/sed/ \
        data-platform/scripts/external-signals/tests/test_registry.py
git commit -m "feat(external-signals): add provider registry with discovery and validation"
```

---

## Task 3: Add provenance fields to `normalize.build_record`

**Files:**
- Modify: `data-platform/scripts/external-signals/normalize.py`
- Test: `data-platform/scripts/external-signals/tests/test_normalize.py` (extend)

- [ ] **Step 1: Write the failing test (append to `tests/test_normalize.py`)**

```python
class TestProvenanceFields(unittest.TestCase):
    def test_active_binding_defaults_and_override(self):
        from normalize import build_record
        rec = build_record(
            signal_id="s1", source_id="sed", source_authority="SED-ETH",
            hazard_type="earthquake", severity="Severe", certainty="Observed",
            urgency="Immediate", region={"cantons": ["ZH"]}, onset="2026-07-23T00:00:00Z",
            status="Actual", connector_version="sed-2.0.0", licence="SED-ETH-open-data",
            raw=b"{}", active_binding="simulated", fell_back_from="live",
            channel_kind="external",
        )
        self.assertEqual(rec["provenance"]["activeBinding"], "simulated")
        self.assertEqual(rec["provenance"]["fellBackFrom"], "live")
        self.assertEqual(rec["provenance"]["channelKind"], "external")

    def test_active_binding_default_is_live(self):
        from normalize import build_record
        rec = build_record(
            signal_id="s2", source_id="sed", source_authority="SED-ETH",
            hazard_type="earthquake", severity="Severe", certainty="Observed",
            urgency="Immediate", region={"cantons": ["ZH"]}, onset="2026-07-23T00:00:00Z",
            status="Actual", connector_version="sed-2.0.0", licence="SED-ETH-open-data",
            raw=b"{}",
        )
        self.assertEqual(rec["provenance"]["activeBinding"], "live")
        self.assertIsNone(rec["provenance"]["fellBackFrom"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest tests.test_normalize -v`
Expected: FAIL (`TypeError: unexpected keyword argument 'active_binding'`).

- [ ] **Step 3: Modify `build_record`**

In `normalize.py`, change the `build_record` signature to add three keyword args and extend the `provenance` block:

```python
def build_record(*, signal_id, source_id, source_authority, hazard_type,
                 severity, certainty, urgency, region, onset, status,
                 connector_version, licence, raw,
                 cap_identifier=None, danger_level=None, effective=None,
                 expires=None, uri=None, mapped_scenario_template=None,
                 default_lage_tier=None, trust_tier="A",
                 active_binding="live", fell_back_from=None,
                 channel_kind="external") -> dict:
```

And in the returned dict, replace the `provenance` block with:

```python
        "provenance": {
            "ingestedAt": _now(),
            "connectorVersion": connector_version,
            "licence": licence,
            "rawHash": raw_hash(raw if isinstance(raw, bytes) else json.dumps(raw, sort_keys=True).encode()),
            "activeBinding": active_binding,
            "fellBackFrom": fell_back_from,
            "channelKind": channel_kind,
        },
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest tests.test_normalize -v`
Expected: PASS (existing + 2 new tests).

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/normalize.py \
        data-platform/scripts/external-signals/tests/test_normalize.py
git commit -m "feat(external-signals): add binding provenance fields to build_record"
```

---

## Task 4: Migrate `sed` parse from connectors to provider (parse.py)

**Files:**
- Create: `data-platform/scripts/external-signals/providers/sed/parse.py`
- Modify: `data-platform/scripts/external-signals/tests/_util.py`
- Test: `data-platform/scripts/external-signals/tests/test_providers.py`

- [ ] **Step 1: Add fixture helper (modify `tests/_util.py`, append)**

```python
def load_provider_fixture(source_id: str, name: str) -> dict:
    """Load a raw fixture for a specific provider from tests/fixtures."""
    return load_fixture(name)  # fixtures remain flat in tests/fixtures/
```

- [ ] **Step 2: Write the failing test — create `tests/test_providers.py`**

```python
import unittest
from tests._util import load_fixture
from providers.sed.parse import parse as sed_parse


class TestSedProvider(unittest.TestCase):
    def test_sed_maps_quake_and_stamps_channel_kind(self):
        recs = sed_parse(load_fixture("sed_quake.json"))
        self.assertEqual(recs[0]["hazardType"], "earthquake")
        self.assertIn(recs[0]["severity"], {"Severe", "Extreme"})
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F1")
        self.assertEqual(recs[0]["provenance"]["channelKind"], "external")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest tests.test_providers -v`
Expected: FAIL (`ModuleNotFoundError: providers.sed.parse`).

- [ ] **Step 4: Write `providers/sed/parse.py`**

Open the existing `connectors/sed.py` to copy its exact mapping logic, then write `providers/sed/parse.py` as a function that reuses `normalize.build_record` with `channel_kind="external"`. Example structure (fill severity/field mapping from `connectors/sed.py`):

```python
"""SED FDSN earthquake connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from normalize import build_record

SOURCE_ID = "sed"
AUTHORITY = "SED-ETH"
LICENCE = "SED-ETH-open-data"
VERSION = "sed-2.0.0"


def _severity_from_magnitude(mag: float) -> str:
    if mag >= 6.0:
        return "Extreme"
    if mag >= 5.0:
        return "Severe"
    if mag >= 4.0:
        return "Moderate"
    return "Minor"


def parse(payload: dict, *, active_binding: str = "live",
          fell_back_from: str | None = None) -> list[dict]:
    out = []
    for ev in payload.get("events", []):
        mag = float(ev.get("magnitude", 0.0))
        out.append(build_record(
            signal_id=ev["eventId"], source_id=SOURCE_ID,
            source_authority=AUTHORITY, hazard_type="earthquake",
            severity=_severity_from_magnitude(mag), certainty="Observed",
            urgency="Immediate", region={"cantons": ev.get("cantons", [])},
            effective=ev.get("time"), onset=ev.get("time"),
            expires=ev.get("expires"), status="Actual",
            connector_version=VERSION, licence=LICENCE,
            raw=json.dumps(ev, sort_keys=True).encode(), uri=ev.get("uri"),
            danger_level=None, mapped_scenario_template="F1", default_lage_tier=3,
            active_binding=active_binding, fell_back_from=fell_back_from,
            channel_kind="external",
        ))
    return out
```

> IMPORTANT: reconcile field names (`events`, `eventId`, `magnitude`, `time`, `cantons`) against the existing `tests/fixtures/sed_quake.json` and `connectors/sed.py`. Adjust key names so the test passes with the committed fixture.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest tests.test_providers -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/external-signals/providers/sed/parse.py \
        data-platform/scripts/external-signals/tests/_util.py \
        data-platform/scripts/external-signals/tests/test_providers.py
git commit -m "refactor(external-signals): migrate sed parse into provider plugin"
```

---

## Task 5: Migrate remaining external parsers (meteoswiss, alertswiss, bag)

For each of the three providers below, repeat the Task 4 pattern exactly: create `provider.yaml`, `parse.py` (moving the mapping from the matching `connectors/<id>.py`), `__init__.py`, and a test in `tests/test_providers.py`. Use these manifest values (all `channelKind: external`, `trustTier: A`):

| sourceId | authority | hazardTypes | defaultMode | endpoint | licence | providerVersion | scenarioMap |
|----------|-----------|-------------|-------------|----------|---------|-----------------|-------------|
| meteoswiss | MeteoSwiss | [heat, flood] | simulated | https://data.geo.admin.ch/api/stac/v1 | MeteoSwiss-open-government-data | meteoswiss-2.0.0 | heat: {template: F8, lageTier: 2}, flood: {template: F8, lageTier: 2} |
| alertswiss | BABS/FOCP | [govt-alert] | live | https://www.alert.swiss/api/v1/cap | Alertswiss-CAP-open | alertswiss-2.0.0 | govt-alert: {template: F7, lageTier: 3} |
| bag | FOPH/BAG | [epidemic] | simulated | https://idd.bag.admin.ch/api | BAG-open-data | bag-2.0.0 | epidemic: {template: F6, lageTier: 2} |

Note `meteoswiss.defaultMode` and `bag.defaultMode` are `simulated` (live adapter authored but dormant — Open-Meteo licence + BAG dataset-ID caveats per the AMA). `alertswiss.defaultMode` is `live`. Each `parse.py` sets `channel_kind="external"` and accepts `active_binding` / `fell_back_from` kwargs (as in Task 4). Reconcile field names against each existing `connectors/<id>.py` + fixture.

- [ ] **Step 1: Write failing tests (append to `tests/test_providers.py`)**

```python
from providers.meteoswiss.parse import parse as meteo_parse
from providers.alertswiss.parse import parse as alert_parse
from providers.bag.parse import parse as bag_parse


class TestExternalProviders(unittest.TestCase):
    def test_meteoswiss_heat_f8(self):
        recs = meteo_parse(load_fixture("meteoswiss_heat.json"))
        self.assertEqual(recs[0]["hazardType"], "heat")
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F8")

    def test_alertswiss_preserves_cap_identifier(self):
        recs = alert_parse(load_fixture("alertswiss_cap.json"))
        self.assertTrue(recs[0]["capIdentifier"])

    def test_bag_rsv_f6(self):
        recs = bag_parse(load_fixture("bag_rsv.json"))
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F6")
```

- [ ] **Step 2: Run to verify fail** — Run the providers test module; expect `ModuleNotFoundError` for the three new modules.

- [ ] **Step 3: Create the three manifests + `parse.py` + `__init__.py`** using the table values and the Task 4 `parse.py` template (copy mapping from each `connectors/<id>.py`).

- [ ] **Step 4: Run to verify pass** — `PYTHONPATH=. python -m unittest tests.test_providers -v` → PASS.

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/providers/meteoswiss/ \
        data-platform/scripts/external-signals/providers/alertswiss/ \
        data-platform/scripts/external-signals/providers/bag/ \
        data-platform/scripts/external-signals/tests/test_providers.py
git commit -m "refactor(external-signals): migrate meteoswiss/alertswiss/bag into provider plugins"
```

---

## Task 6: Delete `connectors/` and update `signals_synth.py` + `test_connectors.py`

**Files:**
- Delete: `data-platform/scripts/external-signals/connectors/` (whole directory)
- Delete: `data-platform/scripts/external-signals/tests/test_connectors.py`
- Modify: `data-platform/scripts/external-signals/signals_synth.py`

- [ ] **Step 1: Rewrite `signals_synth.build_records` to use provider parse modules**

Replace the connector imports and `_CONNECTORS` list in `signals_synth.py` with a provider-driven build. Change the import block and `build_records`:

```python
import importlib
from providers.registry import discover

# fixture filename per provider (raw payloads live in tests/fixtures)
_PROVIDER_FIXTURES = {
    "meteoswiss": "meteoswiss_heat.json",
    "sed": "sed_quake.json",
    "alertswiss": "alertswiss_cap.json",
    "bag": "bag_rsv.json",
}


def build_records() -> list[dict]:
    records: list[dict] = []
    for spec in discover():
        fixture = _PROVIDER_FIXTURES.get(spec.source_id)
        if not fixture:
            continue  # simulator/internal-only providers seeded elsewhere (Tasks 7-8)
        parse = importlib.import_module(f"providers.{spec.source_id}.parse").parse
        records.extend(parse(_load_fixture(fixture)))
    return records
```

Remove the old `from connectors.* import *` lines and the `_CONNECTORS` list.

- [ ] **Step 2: Delete the old connector code and test**

```bash
git rm -r data-platform/scripts/external-signals/connectors
git rm data-platform/scripts/external-signals/tests/test_connectors.py
```

- [ ] **Step 3: Run the full suite to verify green**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest discover -s tests -v`
Expected: PASS (no import errors; `signals_synth --dry-run` still works).

- [ ] **Step 4: Verify the seeder**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python signals_synth.py --dry-run`
Expected: `OK: N DC-EXT-SIGNAL-v1 records validated against schema.`

- [ ] **Step 5: Commit**

```bash
git add -A data-platform/scripts/external-signals
git commit -m "refactor(external-signals): remove connectors in favour of provider plugins"
```

---

## Task 7: Simulator bindings for every external provider

Each external provider gets a deterministic `simulator.py` producing the SAME raw shape its `parse.py` consumes, so `parse(simulator.generate())` yields valid records. Add simulators for the 4 migrated providers **and** create simulator-only providers (no live/parse-from-API needed beyond the shared parse) for `bafu, astra, slf, nabel, swissgrid, ncsc` using the manifest table below (all `channelKind: external`, `trustTier: A`, `defaultMode: simulated`, no live adapter this sprint):

| sourceId | authority | hazardTypes | licence | providerVersion | scenarioMap |
|----------|-----------|-------------|---------|-----------------|-------------|
| bafu | BAFU | [flood] | BAFU-open-data | bafu-1.0.0 | flood: {template: F8, lageTier: 2} |
| astra | ASTRA | [traffic] | ASTRA-DATEX-II | astra-1.0.0 | traffic: {template: F3, lageTier: 1} |
| slf | SLF | [avalanche] | SLF-open-data | slf-1.0.0 | avalanche: {template: F8, lageTier: 2} |
| nabel | BAFU-NABEL | [air-quality] | NABEL-open-data | nabel-1.0.0 | air-quality: {template: F8, lageTier: 1} |
| swissgrid | Swissgrid | [power] | Swissgrid-terms | swissgrid-1.0.0 | power: {template: F1, lageTier: 2} |
| ncsc | NCSC | [cyber] | NCSC-open-data | ncsc-1.0.0 | cyber: {template: F4, lageTier: 2} |

For the 6 simulator-only providers, `parse.py` follows the Task 4 template mapping the single hazard in the table (severity from a `severity` key in the simulated raw). Each `simulator.py`:

```python
"""Deterministic synthetic raw payload for the <sourceId> channel."""
from __future__ import annotations


def generate(seed: int = 0) -> dict:
    # Deterministic: same seed -> same payload. Shape matches parse.py input.
    return {
        "events": [
            {
                "eventId": f"<sourceId>-sim-{seed:04d}",
                "severity": "Severe",
                "cantons": ["ZH"],
                "time": "2026-07-23T00:00:00Z",
                "expires": "2026-07-24T00:00:00Z",
                "uri": "https://example.invalid/<sourceId>/sim",
            }
        ]
    }
```

- [ ] **Step 1: Write failing test — create `tests/test_simulators.py`**

```python
import importlib
import unittest
from providers.registry import discover


class TestSimulators(unittest.TestCase):
    def test_every_external_provider_has_deterministic_simulator(self):
        for spec in discover():
            if spec.channel_kind != "external":
                continue
            sim = importlib.import_module(f"providers.{spec.source_id}.simulator")
            a = sim.generate(seed=1)
            b = sim.generate(seed=1)
            self.assertEqual(a, b, f"{spec.source_id} simulator not deterministic")

    def test_simulated_payload_parses_to_valid_records(self):
        import json
        from pathlib import Path
        scripts = Path(__file__).resolve().parents[1]
        schema = json.loads(
            (scripts / "providers" / "_schema" / "provider.schema.json").read_text()
        )  # sanity: schema loads
        self.assertTrue(schema)
        for spec in discover():
            if spec.channel_kind != "external":
                continue
            sim = importlib.import_module(f"providers.{spec.source_id}.simulator")
            parse = importlib.import_module(f"providers.{spec.source_id}.parse").parse
            recs = parse(sim.generate(seed=2), active_binding="simulated")
            self.assertTrue(recs)
            self.assertEqual(recs[0]["provenance"]["activeBinding"], "simulated")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify fail** — expect `ModuleNotFoundError` for the first missing `simulator`.

- [ ] **Step 3: Create all simulators + the 6 new simulator-only providers** (manifests + `parse.py` + `simulator.py` + `__init__.py`). For the 4 migrated providers, add a `simulator.py` whose `generate()` returns the same shape as their existing fixture.

- [ ] **Step 4: Run to verify pass** — `PYTHONPATH=. python -m unittest tests.test_simulators -v` → PASS.

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/providers \
        data-platform/scripts/external-signals/tests/test_simulators.py
git commit -m "feat(external-signals): add deterministic simulator bindings for all external channels"
```

---

## Task 8: Internal providers (occupancy-breach, roster-shortfall, supply-stock)

Internal providers read our own gold tables (passed in as a dict of rows for offline testing) and emit `DC-EXT-SIGNAL-v1` with `channel_kind="internal"`, `active_binding="internal"`. Manifests (all `channelKind: internal`, `trustTier: A`, `defaultMode: internal`, **no** endpoint):

| sourceId | authority | hazardTypes | licence | providerVersion | scenarioMap |
|----------|-----------|-------------|---------|-----------------|-------------|
| occupancy-breach | Curavias-internal | [capacity-breach] | internal | occupancy-breach-1.0.0 | capacity-breach: {template: F5, lageTier: 1} |
| roster-shortfall | Curavias-internal | [staffing-shortfall] | internal | roster-shortfall-1.0.0 | staffing-shortfall: {template: F5, lageTier: 1} |
| supply-stock | Curavias-internal | [supply-shortage] | internal | supply-stock-1.0.0 | supply-shortage: {template: F5, lageTier: 2} |

Each provider dir gets `provider.yaml`, `internal.py`, `parse.py`, `__init__.py`.

- [ ] **Step 1: Write failing test — create `tests/test_internal.py`**

```python
import unittest
from providers.occupancy_breach.internal import read as occ_read
from providers.occupancy_breach.parse import parse as occ_parse


GOLD = {
    "fact_bed_state": [
        {"hospital": "USZ", "ward_id": "GER-1", "occupied": 34, "capacity": 30,
         "date": "2026-07-23"},
        {"hospital": "USZ", "ward_id": "CAR-1", "occupied": 10, "capacity": 30,
         "date": "2026-07-23"},
    ]
}


class TestInternalOccupancy(unittest.TestCase):
    def test_breach_emits_internal_signal(self):
        raw = occ_read(GOLD)          # only the breached ward
        recs = occ_parse(raw)
        self.assertEqual(len(recs), 1)
        self.assertEqual(recs[0]["provenance"]["channelKind"], "internal")
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "internal")
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F5")


if __name__ == "__main__":
    unittest.main()
```

> Note: the provider package dir is `occupancy-breach` on disk, but Python import uses `occupancy_breach`. Create the dir as `occupancy_breach/` (underscore) and set `sourceId: occupancy-breach` in the manifest, so both the registry `sourceId` (hyphen) and Python import (underscore) are satisfied. Registry `discover()` reads `sourceId` from YAML, not the dir name, so this is safe. Apply the same convention to `roster_shortfall` and `supply_stock`.

- [ ] **Step 2: Run to verify fail** — expect `ModuleNotFoundError: providers.occupancy_breach`.

- [ ] **Step 3: Write `providers/occupancy_breach/internal.py`**

```python
"""Derive occupancy-breach raw events from gold bed-state rows."""
from __future__ import annotations


def read(gold: dict) -> dict:
    events = []
    for row in gold.get("fact_bed_state", []):
        if row["occupied"] > row["capacity"]:
            events.append({
                "eventId": f"occ-{row['hospital']}-{row['ward_id']}-{row['date']}",
                "severity": "Moderate",
                "cantons": ["ZH"],
                "ward": row["ward_id"],
                "time": f"{row['date']}T00:00:00Z",
                "expires": None,
                "uri": None,
            })
    return {"events": events}
```

And `providers/occupancy_breach/parse.py` following the Task 4 template with `channel_kind="internal"`, `active_binding="internal"` defaults, `mapped_scenario_template="F5"`, `hazard_type="capacity-breach"`, `licence="internal"`, `connector_version="occupancy-breach-1.0.0"`. Create the manifest + `__init__.py`.

- [ ] **Step 4: Repeat for `roster_shortfall` and `supply_stock`** (their `internal.read` derives events from `fact_roster` shortfall rows and `fact_supply` low-stock rows respectively; write one focused test each in `tests/test_internal.py`).

- [ ] **Step 5: Run to verify pass** — `PYTHONPATH=. python -m unittest tests.test_internal -v` → PASS.

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/external-signals/providers \
        data-platform/scripts/external-signals/tests/test_internal.py
git commit -m "feat(external-signals): add internal signal providers from gold tables"
```

---

## Task 9: Live adapters (sed, alertswiss) with injectable transport

**Files:**
- Create: `providers/sed/live.py`, `providers/alertswiss/live.py`
- Test: `tests/test_providers.py` (extend)

Live bindings fetch raw via an injectable `transport(url) -> dict` so CI mocks it (no network).

- [ ] **Step 1: Write failing test (append to `tests/test_providers.py`)**

```python
class TestLiveBindings(unittest.TestCase):
    def test_sed_live_uses_injected_transport(self):
        from providers.sed.live import LiveBinding
        sample = load_fixture("sed_quake.json")
        binding = LiveBinding(endpoint="https://example.invalid")
        raw = binding.poll(transport=lambda url: sample)
        self.assertEqual(raw, sample)
```

- [ ] **Step 2: Run to verify fail** — expect `ModuleNotFoundError: providers.sed.live`.

- [ ] **Step 3: Write `providers/sed/live.py`**

```python
"""SED FDSN live adapter (network optional; transport is injectable)."""
from __future__ import annotations

from typing import Callable


class LiveBinding:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def _default_transport(self, url: str) -> dict:  # pragma: no cover - network
        import requests
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def poll(self, transport: Callable[[str], dict] | None = None) -> dict:
        fetch = transport or self._default_transport
        return fetch(self.endpoint)
```

Write `providers/alertswiss/live.py` identically (same class; different default parsing is handled by `parse.py`, not here).

- [ ] **Step 4: Run to verify pass** — PASS.

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/providers/sed/live.py \
        data-platform/scripts/external-signals/providers/alertswiss/live.py \
        data-platform/scripts/external-signals/tests/test_providers.py
git commit -m "feat(external-signals): add live adapters for sed and alertswiss"
```

---

## Task 10: Provider runner with binding selection + live→simulated fallback

**Files:**
- Create: `data-platform/scripts/external-signals/providers/runner.py`
- Test: `data-platform/scripts/external-signals/tests/test_runner_fallback.py`

- [ ] **Step 1: Write failing test — create `tests/test_runner_fallback.py`**

```python
import unittest
from providers.registry import load_manifest
from providers.runner import run_provider
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]


def _spec(source_id):
    return load_manifest(SCRIPTS / "providers" / source_id / "provider.yaml")


class TestRunnerFallback(unittest.TestCase):
    def test_live_success_marks_live(self):
        spec = _spec("sed")
        from tests._util import load_fixture
        recs = run_provider(spec, transport=lambda url: load_fixture("sed_quake.json"))
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "live")
        self.assertIsNone(recs[0]["provenance"]["fellBackFrom"])

    def test_live_failure_falls_back_to_simulated(self):
        spec = _spec("sed")
        def boom(url):
            raise TimeoutError("endpoint down")
        recs = run_provider(spec, transport=boom)
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "simulated")
        self.assertEqual(recs[0]["provenance"]["fellBackFrom"], "live")

    def test_simulated_default_marks_simulated(self):
        spec = _spec("bafu")
        recs = run_provider(spec)
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "simulated")

    def test_internal_default_marks_internal(self):
        spec = _spec("occupancy-breach")
        gold = {"fact_bed_state": [
            {"hospital": "USZ", "ward_id": "GER-1", "occupied": 34,
             "capacity": 30, "date": "2026-07-23"}]}
        recs = run_provider(spec, gold=gold)
        self.assertEqual(recs[0]["provenance"]["activeBinding"], "internal")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify fail** — expect `ModuleNotFoundError: providers.runner`.

- [ ] **Step 3: Write `providers/runner.py`**

```python
"""Select a provider binding, apply live->simulated fallback, emit records."""
from __future__ import annotations

import importlib
from typing import Callable

from providers.registry import ProviderSpec


def _mod(source_id: str, name: str):
    py_id = source_id.replace("-", "_")
    return importlib.import_module(f"providers.{py_id}.{name}")


def run_provider(spec: ProviderSpec, *,
                 transport: Callable[[str], dict] | None = None,
                 gold: dict | None = None,
                 seed: int = 0) -> list[dict]:
    parse = _mod(spec.source_id, "parse").parse

    if spec.default_mode == "internal":
        raw = _mod(spec.source_id, "internal").read(gold or {})
        return parse(raw, active_binding="internal", fell_back_from=None)

    if spec.default_mode == "live":
        try:
            binding = _mod(spec.source_id, "live").LiveBinding(endpoint=spec.endpoint)
            raw = binding.poll(transport=transport)
            return parse(raw, active_binding="live", fell_back_from=None)
        except Exception:  # noqa: BLE001 - any live failure triggers fallback
            raw = _mod(spec.source_id, "simulator").generate(seed=seed)
            return parse(raw, active_binding="simulated", fell_back_from="live")

    # default_mode == "simulated"
    raw = _mod(spec.source_id, "simulator").generate(seed=seed)
    return parse(raw, active_binding="simulated", fell_back_from=None)
```

> The internal `parse.py` created in Task 8 must accept `active_binding`/`fell_back_from` kwargs (default `internal`/`None`). Ensure all `parse.py` signatures accept these two kwargs.

- [ ] **Step 4: Run to verify pass** — `PYTHONPATH=. python -m unittest tests.test_runner_fallback -v` → PASS.

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/providers/runner.py \
        data-platform/scripts/external-signals/tests/test_runner_fallback.py
git commit -m "feat(external-signals): add provider runner with live-to-simulated fallback"
```

---

## Task 11: Badge propagation — silver/gold `dataMode` + test

**Files:**
- Modify: `data-platform/notebooks/external-signals/build_silver_signals.py`
- Modify: `data-platform/notebooks/external-signals/build_gold_signals.py`
- Test: `data-platform/scripts/external-signals/tests/test_badge_propagation.py`

- [ ] **Step 1: Inspect the notebooks**

Open both notebook files and locate the pure helper functions that build silver rows and the `ext_dim_source` gold dim. They are written as importable pure functions for offline testing (per the existing repo pattern). Identify the function that projects a record to a silver row and the one that builds the source dim.

- [ ] **Step 2: Write failing test — create `tests/test_badge_propagation.py`**

Reference the notebook pure functions (adjust import to match what you found in Step 1 — the notebooks live under `data-platform/notebooks/external-signals/` and expose helpers importable with `PYTHONPATH=.` from that dir). Example asserting the mapping `activeBinding → dataMode`:

```python
import unittest


class TestBadgePropagation(unittest.TestCase):
    def test_active_binding_maps_to_data_mode(self):
        from build_gold_signals import data_mode_for  # add this helper in Step 3
        self.assertEqual(data_mode_for("live"), "Live")
        self.assertEqual(data_mode_for("simulated"), "Simulated")
        self.assertEqual(data_mode_for("internal"), "Internal")

    def test_source_dim_row_carries_data_mode(self):
        from build_gold_signals import ext_dim_source_row  # add in Step 3
        rec = {"sourceId": "sed", "sourceAuthority": "SED-ETH", "trustTier": "A",
               "provenance": {"activeBinding": "simulated", "fellBackFrom": "live",
                              "ingestedAt": "2026-07-23T00:00:00Z"}}
        row = ext_dim_source_row(rec)
        self.assertEqual(row["dataMode"], "Simulated")
        self.assertEqual(row["fellBackFrom"], "live")
        self.assertEqual(row["trustTier"], "A")
```

> This test imports from `build_gold_signals`, so run it from the notebooks dir:
> `cd data-platform/notebooks/external-signals && PYTHONPATH=.:../../scripts/external-signals python -m unittest <path-to-test>`. To keep the suite unified, place a thin copy of the test under `data-platform/notebooks/external-signals/tests/` (the CI workflow already discovers notebook tests there). Move the test there if the scripts-dir import path is awkward.

- [ ] **Step 3: Add the pure helpers to `build_gold_signals.py`**

```python
_DATA_MODE = {"live": "Live", "simulated": "Simulated", "internal": "Internal"}


def data_mode_for(active_binding: str) -> str:
    return _DATA_MODE[active_binding]


def ext_dim_source_row(rec: dict) -> dict:
    prov = rec.get("provenance", {})
    return {
        "sourceId": rec["sourceId"],
        "authority": rec.get("sourceAuthority"),
        "trustTier": rec.get("trustTier"),
        "dataMode": data_mode_for(prov.get("activeBinding", "live")),
        "fellBackFrom": prov.get("fellBackFrom"),
        "lastLiveAt": prov.get("ingestedAt") if prov.get("activeBinding") == "live" else None,
    }
```

Wire `ext_dim_source_row` into the existing `ext_dim_source` build in the notebook (dedup by `sourceId`, keeping the latest `ingestedAt`). In `build_silver_signals.py`, ensure the silver projection carries `provenance.activeBinding` through to the silver row.

- [ ] **Step 4: Run to verify pass** — run the notebook-tests discovery per the note; PASS.

- [ ] **Step 5: Commit**

```bash
git add data-platform/notebooks/external-signals/ \
        data-platform/scripts/external-signals/tests/test_badge_propagation.py
git commit -m "feat(external-signals): propagate active binding to ext_dim_source.dataMode"
```

---

## Task 12: Semantic-model badge measures

**Files:**
- Modify: the `external-signals` semantic model TMDL (confirm exact path first)

- [ ] **Step 1: Locate the semantic model**

Find the `external-signals.SemanticModel` TMDL directory:
`find data-platform -iname '*.tmdl' -path '*external*'` (or search `git ls-files | grep -i external | grep -i tmdl`). Confirm the model and the `ext_dim_source` / `ext_fact_signal` table definitions.

- [ ] **Step 2: Add measures**

Add these measures (DAX) to the model's measures table, mirroring the existing measure authoring style in the located TMDL:

```dax
Channels Live = CALCULATE(DISTINCTCOUNT(ext_dim_source[sourceId]), ext_dim_source[dataMode] = "Live")
Channels Simulated = CALCULATE(DISTINCTCOUNT(ext_dim_source[sourceId]), ext_dim_source[dataMode] = "Simulated")
Channels Internal = CALCULATE(DISTINCTCOUNT(ext_dim_source[sourceId]), ext_dim_source[dataMode] = "Internal")
Last Live Signal = MAX(ext_dim_source[lastLiveAt])
```

Add a `Channel Data Mode = SELECTEDVALUE(ext_dim_source[dataMode], "Simulated")` measure for card binding.

- [ ] **Step 3: Validate (no CI collision)**

Confirm `verify-semantic-model.yml` targets only the `capacity-dashboard` model (per ADR-0026) and does NOT include `external-signals` — so this change stays outside the exact-count gate. If a separate validation exists for this model, run it.

- [ ] **Step 4: Commit**

```bash
git add <external-signals-tmdl-path>
git commit -m "feat(external-signals): add live/simulated/internal channel badge measures"
```

---

## Task 13: Provider-runner Container App (Bicep scaffold, deploy-gated)

**Files:**
- Create: `data-platform/external-signals/provider-runner/main.bicep`
- Create: `data-platform/external-signals/provider-runner/README.md`

- [ ] **Step 1: Author the Bicep module**

Create `main.bicep` provisioning a Container App that runs the provider-runner and publishes to the existing Event Hub. Parameterise (no hard-coded names); reuse existing Event Hub/Eventstream by name parameter. Tag `env`, `owner`, `costCenter`, `workload`. Minimal shape:

```bicep
@description('Environment suffix, e.g. sit or prod')
param envSuffix string
@description('Existing Container Apps managed environment resource id')
param managedEnvironmentId string
@description('Existing Event Hub namespace name (evh-ihzhhpf...)')
param eventHubNamespace string
@description('Event Hub name for external signals')
param eventHubName string
param location string = resourceGroup().location

var appName = 'ca-signal-runner-ihzhhpf-${envSuffix}'

resource runner 'Microsoft.App/containerApps@2024-03-01' = {
  name: appName
  location: location
  tags: {
    env: envSuffix
    owner: 'urruegg'
    costCenter: 'curavias-platform'
    workload: 'external-signals'
  }
  properties: {
    managedEnvironmentId: managedEnvironmentId
    configuration: {
      activeRevisionsMode: 'Single'
    }
    template: {
      containers: [
        {
          name: 'provider-runner'
          image: 'mcr.microsoft.com/azure-cli:latest' // replaced by built image at deploy
          env: [
            { name: 'EVENT_HUB_NAMESPACE', value: eventHubNamespace }
            { name: 'EVENT_HUB_NAME', value: eventHubName }
          ]
        }
      ]
      scale: { minReplicas: 0, maxReplicas: 1 }
    }
  }
  identity: { type: 'SystemAssigned' }
}

output providerRunnerName string = runner.name
```

- [ ] **Step 2: Validate the Bicep**

Run: `az bicep build --file data-platform/external-signals/provider-runner/main.bicep`
Expected: builds with no errors (warnings about placeholder image are acceptable). If `az` is unavailable locally, note that CI runs the Bicep build; ensure syntax is valid.

- [ ] **Step 3: Write the README**

Create `README.md` documenting: purpose (host adapters+simulators+internal providers, publish DC-EXT-SIGNAL-v1 to Event Hub), that deploy is gated by `approved-to-apply`, and that CI never runs ingestion. State that live bindings (SED, Alertswiss) require the build-time endpoint/licence verification list before promotion.

- [ ] **Step 4: Commit**

```bash
git add data-platform/external-signals/provider-runner/
git commit -m "feat(external-signals): add provider-runner Container App bicep (deploy-gated)"
```

---

## Task 14: Retire the poller workflow; update `external-signals.yml`

**Files:**
- Delete: `.github/workflows/ext-signal-poll.yml`
- Modify: `.github/workflows/external-signals.yml`

- [ ] **Step 1: Delete the poller**

```bash
git rm .github/workflows/ext-signal-poll.yml
```

- [ ] **Step 2: Add manifest-validation + full test coverage to `external-signals.yml`**

In the `Run external-signal script tests` step, the existing `python3 -m unittest discover -s tests -v` already picks up the new test modules. Add a manifest-validation step before it:

```yaml
      - name: Validate provider manifests
        shell: bash
        run: |
          set -euo pipefail
          cd data-platform/scripts/external-signals
          PYTHONPATH=. python3 -c "from providers.registry import discover, catalog_rows; rows = catalog_rows(discover()); print(f'validated {len(rows)} provider manifests'); assert rows"
```

Confirm PyYAML is installed (the workflow already runs `pip install pyyaml`).

- [ ] **Step 3: Verify offline suite mirrors CI locally**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest discover -s tests -v`
Expected: PASS (registry, providers, simulators, internal, runner-fallback, normalize, dedup, trigger_rules, schema_conformance, forecast_uplift).

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/external-signals.yml
git rm .github/workflows/ext-signal-poll.yml
git commit -m "ci(external-signals): retire poller workflow; validate provider manifests"
```

---

## Task 15: Governance — ADR-0036, PRD FR-EXT-015+, DATA.md

**Files:**
- Modify: `docs/adr/0036-external-trigger-governance.md`
- Modify: `docs/PRD.md`
- Modify: `docs/DATA.md`

- [ ] **Step 1: Extend ADR-0036**

Read `docs/adr/0036-external-trigger-governance.md`. Append a decision section recording: (a) manifest-driven provider-plugin architecture with swappable Live/Simulated/Internal bindings + live→simulated fallback; (b) 3-state trust-badge data contract (`provenance.activeBinding → ext_dim_source.dataMode → measures → board`); (c) ingestion+simulation hosted on Azure Container Apps (provider-runner), **not** GitHub Actions (Actions is CI-only); (d) internal signal channels as first-class providers. Keep `Status` accurate and cross-link the new design spec.

- [ ] **Step 2: Add requirements to PRD §K**

In `docs/PRD.md` §K table, append rows (IDs verified free against v1.9.0):

```markdown
| `FR-EXT-015` | Onboard new signal sources as manifest-driven provider plugins emitting `DC-EXT-SIGNAL-v1`. |
| `FR-EXT-016` | Provide real API adapters (LiveBinding) for confirmed-ready channels (SED, Alertswiss). |
| `FR-EXT-017` | Provide simulator plugins (SimulatorBinding) for channels without a confirmed API. |
| `FR-EXT-018` | Support internal signal channels (InternalBinding) derived from platform gold tables. |
| `FR-EXT-019` | Surface a data-driven live/simulated/internal trust badge per channel on the CSA/OCA boards. |
| `FR-EXT-020` | Host ingestion + simulation as Azure Container Apps services publishing to Event Hub/Eventstream (not GitHub Actions). |
| `NFR-EXT-PLG-001` | Live bindings are always mocked in CI; no external network calls in Actions. |
| `NFR-EXT-PLG-002` | A schema-invalid manifest fails CI and is excluded from the runtime catalogue (fail-closed). |
```

Add matching rows to the PRD traceability matrix (§7 or the matrix section — locate it and mirror the existing row format). Bump the PRD `Version` MINOR (1.9.0 → 1.10.0), update `Previous Version`, update `Date` to 2026-07-23.

- [ ] **Step 3: Update DATA.md**

In the `DC-EXT-*` contract family section of `docs/DATA.md`, document the new provenance fields (`activeBinding`, `fellBackFrom`, `channelKind`) and the `ext_dim_source` badge columns (`dataMode`, `trustTier`, `lastLiveAt`, `fellBackFrom`). Bump `Version` per §9.

- [ ] **Step 4: Run doc gates**

```bash
python scripts/lint/check_mojibake.py docs/PRD.md docs/DATA.md docs/adr/0036-external-trigger-governance.md
npx --yes markdownlint-cli2 docs/PRD.md docs/DATA.md docs/adr/0036-external-trigger-governance.md
```

Expected: no mojibake; 0 markdownlint errors.

- [ ] **Step 5: Commit**

```bash
git add docs/adr/0036-external-trigger-governance.md docs/PRD.md docs/DATA.md
git commit -m "docs(external-signals): add plugin-architecture requirements, ADR update, DATA fields"
```

---

## Task 16: data-quality-agent gate + AGENTS.md reconciliation

**Files:**
- Modify: `agents/data-quality-agent/AGENT.md`
- Modify: `agents/data-quality-agent/golden-tasks.md`
- Modify: `AGENTS.md`

- [ ] **Step 1: Extend the data-quality-agent gate**

In `agents/data-quality-agent/AGENT.md`, extend the `DC-EXT-SIGNAL-v1` gate to also check: every provider manifest is schema-valid; every record carries `provenance.activeBinding`; `ext_dim_source.dataMode` is populated for every provider; `licence` present per provider. Keep the existing gate text intact; add the new checks.

- [ ] **Step 2: Add a golden-task fixture**

In `agents/data-quality-agent/golden-tasks.md`, add one fixture: input = a batch containing a live-fallback record (`activeBinding=simulated, fellBackFrom=live`) and an internal record; expected = gate PASS with `dataMode` correctly derived; forbidden = passing a record missing `activeBinding` or a manifest missing `licence`. Add a `requirement:` front-matter referencing `FR-EXT-019`/`NFR-EXT-PLG-002`.

- [ ] **Step 3: Reconcile AGENTS.md**

In `AGENTS.md`, update the `data-quality-agent` registry row description to mention the manifest/badge gate, and add a short note (in the Fabric/MCP or runtime section) that external-signal ingestion + simulation are Azure Container Apps services (provider-runner), not GitHub workflows. Bump the AGENTS.md `Version` MINOR and update `Previous Version` + `Date`.

- [ ] **Step 4: Run doc gates**

```bash
python scripts/lint/check_mojibake.py AGENTS.md agents/data-quality-agent/AGENT.md agents/data-quality-agent/golden-tasks.md
npx --yes markdownlint-cli2 AGENTS.md agents/data-quality-agent/AGENT.md agents/data-quality-agent/golden-tasks.md
```

Expected: clean.

- [ ] **Step 5: Replay the eval golden (if runnable)**

If `eval-goldens.yml` has a local replay path, run the `data-quality-agent` fixture. Otherwise note CI enforces it.

- [ ] **Step 6: Commit**

```bash
git add AGENTS.md agents/data-quality-agent/
git commit -m "docs(agents): extend data-quality gate for provider manifests and badge"
```

---

## Task 17: End-to-end synthetic walk-through + spec status bump

**Files:**
- Modify: `docs/superpowers/specs/2026-07-23-sprint-21-signal-provider-plugin-architecture-design.md`
- (Optional) Create: a short evidence note under `docs/sprints/`

- [ ] **Step 1: Run the full offline suite**

Run: `cd data-platform/scripts/external-signals && PYTHONPATH=. python -m unittest discover -s tests -v`
Expected: PASS (all modules). Then `PYTHONPATH=. python signals_synth.py --dry-run` → OK.

- [ ] **Step 2: Prove the runner over a mixed batch**

Run a one-off (from `data-platform/scripts/external-signals`):

```bash
PYTHONPATH=. python -c "from providers.registry import discover; from providers.runner import run_provider; \
recs=[]; \
[recs.extend(run_provider(s, gold={'fact_bed_state':[{'hospital':'USZ','ward_id':'GER-1','occupied':34,'capacity':30,'date':'2026-07-23'}]})) for s in discover()]; \
modes={r['provenance']['activeBinding'] for r in recs}; \
print('records',len(recs),'modes',sorted(modes)); \
assert {'simulated','internal'} <= modes"
```

Expected: prints record count and `modes ['internal', 'live', 'simulated']` (live present if SED live path is exercised with a transport; simulated+internal guaranteed). Adjust to inject a transport for the two live providers to observe `live`.

- [ ] **Step 3: Update the design spec status**

Set the spec `Status` to `Implemented` (or `Approved — implemented`), bump `Version` PATCH (1.0.0 → 1.0.1), update `Previous Version` + `Date`. Run mojibake + markdownlint on the spec.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/specs/2026-07-23-sprint-21-signal-provider-plugin-architecture-design.md
git commit -m "docs(sprint-21): mark plugin-architecture spec implemented"
```

- [ ] **Step 5: Push and open the PR (do NOT self-merge)**

```bash
git push -u origin sprint-21/refactor-signals
gh pr create --fill --base main --head sprint-21/refactor-signals \
  --title "feat(sprint-21): signal-provider plugin architecture and trust badges"
```

PR description must follow the PR Output Contract: What changed / Why (issue #247) / Requirements implemented (FR-EXT-015..020, NFR-EXT-PLG-001/002) / Test evidence (suite output) / Agent+eval impact / Infra impact (provider-runner Bicep, deploy-gated) / Security impact (Container App system-assigned identity; no secrets) / Lane impact (Data + Platform-control + Experience) / Compliance impact (public non-PHI; licence per provider). Leave the PR as a draft/ready-for-review; **do not merge**.

---

## Self-Review

**Spec coverage** (spec section → task):
- §5 plugin contract → Tasks 1–4, 9, 10
- §6 manifest + binding + fallback + registry → Tasks 1, 2, 7, 8, 10
- §6.3 provenance fields → Task 3
- §7 trust-badge propagation → Tasks 11, 12
- §8 provider inventory (SED/Alertswiss live; 6 simulated; MeteoSwiss/BAG dormant-live; 3 internal) → Tasks 4, 5, 7, 8, 9
- §9 refactor delta (connectors→providers; retire poller; provider-runner infra; DQ gate) → Tasks 6, 13, 14, 16
- §10 ADR-0036 + FR-EXT-015+ → Task 15
- §12 CI gates (manifest validation, fallback test, badge-propagation test, no live in CI) → Tasks 10, 11, 14
- §13 milestones M0–M7 → Tasks 1–17
- §15 DoD (all gates green; badges from data; docs bumped; PR not merged) → Tasks 14, 17
- §16 B/C stubs → out of scope (referenced only)

**Placeholder scan:** No "TBD/TODO". The two spots that say "reconcile field names against the existing fixture/connector" are explicit reconciliation instructions with the exact files named, not placeholders — the engineer copies concrete mapping from a named source file.

**Type consistency:** `ProviderSpec` fields, `run_provider(spec, *, transport, gold, seed)`, `parse(raw, *, active_binding, fell_back_from)`, `LiveBinding(endpoint).poll(transport)`, `simulator.generate(seed)`, `internal.read(gold)`, `data_mode_for()`, `ext_dim_source_row()`, `catalog_rows()`, `discover()` — names are consistent across Tasks 2, 3, 4, 7, 8, 9, 10, 11. Python package dirs use underscores (`occupancy_breach`) while manifest `sourceId` uses hyphens (`occupancy-breach`); `runner._mod` bridges via `.replace("-", "_")` (Task 10), consistent with Task 8's note.

---

## Execution Handoff

Plan complete. Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task with two-stage review between tasks.
2. **Inline Execution** — execute tasks in this session with checkpoints.
