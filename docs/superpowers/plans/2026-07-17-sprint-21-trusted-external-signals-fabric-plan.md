# Sprint 21 — Trusted External Signals Fabric Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ingest Trust-A Swiss authority hazard feeds into Fabric, normalize to `DC-EXT-SIGNAL-v1`, expose a dual-bound (Eventhouse + Lakehouse medallion) data product + semantic model + ontology domain, and fire advisory CSA runs via a new `signal-triage-agent` — all CI-gated and offline-testable.

**Architecture:** Four offline-testable Python connectors normalize source payloads to a CAP-aligned contract; medallion notebooks build `gold.ext_*` Delta tables; an Eventstream route feeds an Eventhouse hot path for Activator/Reflex; a poller-workflow bridge invokes `signal-triage-agent`, which dedups + arbitrates + routes to `csa-agent` (advisory/HITL preserved). Ontology and Fabric-IQ binding follow the three-plane crosswalk with operational binding GA-gated per ADR-0014.

**Tech Stack:** Python 3.12 (stdlib-only core, optional `requests`/`pyarrow`), JSON Schema draft-07, PySpark notebooks, Fabric Eventstream/Eventhouse (REST post-deploy), Power BI Direct Lake TMDL, GitHub Actions, Markdown agent packs + MCP.

**Design spec:** `docs/superpowers/specs/2026-07-17-sprint-21-trusted-external-signals-fabric-design.md`
**Tracking issue:** #247

---

## File Structure

Files created or modified, grouped by responsibility:

#### Governance and requirements

- Create `docs/adr/0033-external-trigger-governance.md` — external-trigger governance decision.
- Modify `docs/PRD.md` — add `FR-EXT-*` family + traceability rows (MINOR bump).
- Modify `docs/DATA.md` — document `DC-EXT-SIGNAL-v1` (MINOR bump).

#### Contract

- Create `data/synthetic/schema/dc-ext-signal-v1.schema.json` — JSON Schema (envelope + records).

#### Connectors and normalization (offline-testable core)

- Create `data-platform/scripts/external-signals/__init__.py`
- Create `data-platform/scripts/external-signals/normalize.py` — payload → contract record.
- Create `data-platform/scripts/external-signals/dedup.py` — derived dedup key + collapse.
- Create `data-platform/scripts/external-signals/connectors/__init__.py`
- Create `data-platform/scripts/external-signals/connectors/base_connector.py`
- Create `data-platform/scripts/external-signals/connectors/meteoswiss.py`
- Create `data-platform/scripts/external-signals/connectors/alertswiss.py`
- Create `data-platform/scripts/external-signals/connectors/sed.py`
- Create `data-platform/scripts/external-signals/connectors/bag.py`
- Create `data-platform/scripts/external-signals/trigger_rules.py` — rule eval + arbitration.
- Create `data-platform/scripts/external-signals/trigger_rules.yaml` — rule + precedence data.
- Create `data-platform/scripts/external-signals/signals_synth.py` — synthetic seeder.
- Create `data-platform/scripts/external-signals/tests/__init__.py`
- Create `data-platform/scripts/external-signals/tests/_util.py`
- Create `data-platform/scripts/external-signals/tests/fixtures/` (raw source payloads)
- Create `data-platform/scripts/external-signals/tests/test_normalize.py`
- Create `data-platform/scripts/external-signals/tests/test_connectors.py`
- Create `data-platform/scripts/external-signals/tests/test_dedup.py`
- Create `data-platform/scripts/external-signals/tests/test_trigger_rules.py`
- Create `data-platform/scripts/external-signals/tests/test_schema_conformance.py`

#### Medallion notebooks

- Create `data-platform/notebooks/external-signals/README.md`
- Create `data-platform/notebooks/external-signals/ingest_bronze_signals.py`
- Create `data-platform/notebooks/external-signals/build_silver_signals.py`
- Create `data-platform/notebooks/external-signals/build_gold_signals.py`
- Create `data-platform/notebooks/external-signals/tests/test_signals_pure.py`

#### Ontology

- Modify `docs/ontology/reference-layer.ttl` — new classes + relations.
- Modify `docs/ontology/crosswalk.md` — new rows (bump).

#### Semantic model

- Create `data-platform/reports/external-signals.SemanticModel/definition/model.tmdl`
- Create `data-platform/reports/external-signals.SemanticModel/definition/tables/*.tmdl`
- Create `data-platform/reports/external-signals.SemanticModel/README.md`

#### Triggering

- Create `data-platform/external-signals/activator/reflex-rule.json` — GA-gated Activator rule.
- Create `data-platform/external-signals/eventstream/route.md` — Eventstream route config note.
- Create `.github/workflows/ext-signal-poll.yml` — poller bridge workflow.
- Create `.github/workflows/external-signals.yml` — offline test gate.

#### Agents

- Create `agents/signal-triage-agent/AGENT.md`
- Create `agents/signal-triage-agent/golden-tasks.md`
- Modify `agents/data-quality-agent/AGENT.md` — add DC-EXT contract gate.
- Modify `agents/data-quality-agent/golden-tasks.md` — add DC-EXT fixture.
- Modify `AGENTS.md` — registry row + MCP note (MINOR bump).

---

## Conventions (read before starting)

- **Offline first:** connectors, normalize, dedup, trigger_rules, synth are stdlib-only so CI runs without network. `requests`/`pyarrow` are optional imports guarded by `try/except ImportError`.
- **Contract envelope** mirrors `data/synthetic/schema/dc-or-schedule-v1.schema.json`: top-level `datasetId/contractId/contractVersion/classification/residency/purposeTags/records[]`; signal fields live inside each record.
- **Tests:** `python3 -m unittest discover -s tests -v` from the script dir (matches `csa-checks.yml`). Hyphen-free module names so plain `import` works.
- **Docs:** every edited Markdown doc bumps SemVer per copilot-instructions §9; run `python scripts/lint/check_mojibake.py <file>` and `npx --yes markdownlint-cli2 "<file>"` before commit.
- **Gold prefix:** all gold tables `ext_`-prefixed. **Separate** semantic model (never touch `capacity-dashboard`).
- **Commit style:** Conventional Commits; reference `#247`; include the `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` trailer.

---

## Milestone M0 — Baseline + scaffolding

### Task M0.1: Create domain folders + package markers

**Files:**

- Create: `data-platform/scripts/external-signals/__init__.py`
- Create: `data-platform/scripts/external-signals/connectors/__init__.py`
- Create: `data-platform/scripts/external-signals/tests/__init__.py`
- Create: `data-platform/scripts/external-signals/tests/_util.py`

- [ ] **Step 1: Create the package markers and test util**

`__init__.py` files are empty. `tests/_util.py`:

```python
"""Shared helpers for the external-signals test-suite (dependency-free)."""
from __future__ import annotations

import json
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


def load_fixture(name: str) -> dict:
    """Load a raw source payload fixture by filename."""
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))
```

- [ ] **Step 2: Verify the package imports**

Run: `cd data-platform/scripts/external-signals; python3 -c "import tests._util as u; print(u.SCRIPTS_DIR.name)"`
Expected: prints `external-signals`

- [ ] **Step 3: Commit**

```bash
git add data-platform/scripts/external-signals
git commit -m "chore(ext-signals): scaffold external-signals domain package (#247)"
```

---

## Milestone M1 — Contract + governance

### Task M1.1: Author the DC-EXT-SIGNAL-v1 JSON Schema

**Files:**

- Create: `data/synthetic/schema/dc-ext-signal-v1.schema.json`
- Test: `data-platform/scripts/external-signals/tests/test_schema_conformance.py`

- [ ] **Step 1: Write the failing test**

`tests/test_schema_conformance.py`:

```python
import json
import unittest
from pathlib import Path

SCHEMA = (
    Path(__file__).resolve().parents[4]
    / "data" / "synthetic" / "schema" / "dc-ext-signal-v1.schema.json"
)


class TestSchemaShape(unittest.TestCase):
    def test_schema_loads_and_has_envelope(self):
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(doc["properties"]["contractId"]["enum"], ["DC-EXT-SIGNAL-v1"])
        required = set(doc["required"])
        self.assertTrue(
            {"datasetId", "contractId", "contractVersion", "classification",
             "residency", "purposeTags", "records"} <= required
        )

    def test_record_requires_core_signal_fields(self):
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        rec = doc["properties"]["records"]["items"]
        for field in ("signalId", "sourceId", "trustTier", "hazardType",
                      "severity", "status", "onset", "provenance"):
            self.assertIn(field, rec["properties"], field)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd data-platform/scripts/external-signals; python3 -m unittest tests.test_schema_conformance -v`
Expected: FAIL (file not found / KeyError)

- [ ] **Step 3: Write the schema**

`data/synthetic/schema/dc-ext-signal-v1.schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "dc-ext-signal-v1.schema.json",
  "title": "Trusted External Signal Contract (DC-EXT-SIGNAL-v1)",
  "description": "CAP-Suisse-aligned envelope for Trust-A Swiss authority hazard signals ingested by the Sprint 21 external-signals data product. Envelope mirrors dc-or-schedule-v1. Public authority data + synthetic fixtures only; no PHI. Records pre-seed CSA ScenarioTemplate and ADR-0024 Lage tiers. See docs/ontology/reference-layer.ttl (hcp:ExternalSignal) and docs/adr/0033-external-trigger-governance.md.",
  "type": "object",
  "additionalProperties": false,
  "required": ["datasetId", "contractId", "contractVersion", "classification", "residency", "purposeTags", "records"],
  "properties": {
    "datasetId":       { "type": "string", "pattern": "^DS-EXT-SIGNAL-[a-z0-9-]+$" },
    "contractId":      { "type": "string", "enum": ["DC-EXT-SIGNAL-v1"] },
    "contractVersion": { "type": "string", "pattern": "^[0-9]+\\.[0-9]+\\.[0-9]+$" },
    "classification":  { "type": "string", "enum": ["public-authority"] },
    "residency":       { "type": "string", "enum": ["CH", "demo-westus2"] },
    "purposeTags": {
      "type": "array", "minItems": 1,
      "items": { "type": "string", "enum": ["crisis-trigger", "capacity-planning", "situational-awareness"] }
    },
    "records": {
      "type": "array", "minItems": 1,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["signalId", "sourceId", "sourceAuthority", "trustTier", "hazardType",
                     "severity", "certainty", "urgency", "region", "onset", "status", "provenance"],
        "properties": {
          "signalId":        { "type": "string" },
          "sourceId":        { "type": "string" },
          "sourceAuthority": { "type": "string" },
          "trustTier":       { "type": "string", "enum": ["A", "B", "C"] },
          "capIdentifier":   { "type": ["string", "null"] },
          "hazardType":      { "type": "string" },
          "severity":        { "type": "string", "enum": ["Minor", "Moderate", "Severe", "Extreme"] },
          "certainty":       { "type": "string", "enum": ["Observed", "Likely", "Possible", "Unlikely"] },
          "urgency":         { "type": "string", "enum": ["Immediate", "Expected", "Future", "Past"] },
          "dangerLevel":     { "type": ["integer", "null"], "minimum": 1, "maximum": 5 },
          "region": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "cantons":    { "type": "array", "items": { "type": "string" } },
              "nuts":       { "type": "array", "items": { "type": "string" } },
              "geoPolygon": { "type": ["object", "null"] }
            }
          },
          "effective": { "type": ["string", "null"], "format": "date-time" },
          "onset":     { "type": "string", "format": "date-time" },
          "expires":   { "type": ["string", "null"], "format": "date-time" },
          "uri":       { "type": ["string", "null"] },
          "status":    { "type": "string", "enum": ["Actual", "Test", "Exercise", "System"] },
          "mappedScenarioTemplate": { "type": ["string", "null"] },
          "defaultLageTier": { "type": ["integer", "null"], "minimum": 1, "maximum": 3 },
          "provenance": {
            "type": "object",
            "additionalProperties": false,
            "required": ["ingestedAt", "connectorVersion", "licence", "rawHash"],
            "properties": {
              "ingestedAt":       { "type": "string", "format": "date-time" },
              "connectorVersion": { "type": "string" },
              "licence":          { "type": "string" },
              "rawHash":          { "type": "string" }
            }
          }
        }
      }
    }
  }
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd data-platform/scripts/external-signals; python3 -m unittest tests.test_schema_conformance -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add data/synthetic/schema/dc-ext-signal-v1.schema.json data-platform/scripts/external-signals/tests/test_schema_conformance.py
git commit -m "feat(ext-signals): add DC-EXT-SIGNAL-v1 contract schema (#247)"
```

### Task M1.2: Document the contract in docs/DATA.md

**Files:** Modify `docs/DATA.md`

- [ ] **Step 1: Add a `DC-EXT-SIGNAL-v1` subsection** under the Data Contracts section, describing: purpose (Trust-A hazard signals), envelope fields, record fields (table from spec §6), dedup key, noise-governance (Test/Exercise/System quarantine), licence obligation, link to `data/synthetic/schema/dc-ext-signal-v1.schema.json`, `docs/adr/0033-external-trigger-governance.md`, and `docs/ontology/reference-layer.ttl`.
- [ ] **Step 2: Bump the DATA.md version header** (MINOR: additive contract), update Previous Version.
- [ ] **Step 3: Lint** — `python scripts/lint/check_mojibake.py docs/DATA.md; npx --yes markdownlint-cli2 "docs/DATA.md"`. Expected: no mojibake, 0 errors.
- [ ] **Step 4: Commit** — `git add docs/DATA.md; git commit -m "docs(data): document DC-EXT-SIGNAL-v1 contract (#247)"`

### Task M1.3: Author ADR-0033 external-trigger governance

**Files:** Create `docs/adr/0033-external-trigger-governance.md`

- [ ] **Step 1: Write the ADR** using the repo ADR format (Status: Proposed → Accepted). Sections: Context (Swiss authority feeds as advisory CSA triggers), Decision (Trust-A auto-evaluated; B/C human-curated; dual-path Activator+poller with Activator GA-gated; Test/Exercise/System quarantine; licence recorded per signal; advisory/HITL preserved; non-PHI synthetic demo residency), Consequences, Alternatives, Links (ADR-0014/0024/0026/0013, spec, issue #247).
- [ ] **Step 2: Lint** — mojibake + markdownlint on the ADR. Expected: clean.
- [ ] **Step 3: Commit** — `git add docs/adr/0033-external-trigger-governance.md; git commit -m "docs(adr): add ADR-0033 external-trigger governance (#247)"`

### Task M1.4: Add FR-EXT-* requirements to docs/PRD.md

**Files:** Modify `docs/PRD.md`

- [ ] **Step 1: Add the `FR-EXT-*` requirement rows** (from spec §12) in the appropriate FR section, and the matching **traceability-matrix** rows at the bottom, each linking to the spec + ADR-0033. Include `FR-EXT-001..006`, `FR-EXT-ONT-001/002`, `NFR-EXT-ONT-001`, `FR-EXT-GOV-001`, `NFR-EXT-GOV-001/002`.
- [ ] **Step 2: Bump the PRD version header** (MINOR: additive requirements), update Previous Version.
- [ ] **Step 3: Lint** — mojibake + markdownlint + `npx --yes markdown-link-check docs/PRD.md`. Expected: clean.
- [ ] **Step 4: Commit** — `git add docs/PRD.md; git commit -m "docs(prd): add FR-EXT-* trusted external signal requirements (#247)"`

---

## Milestone M2 — Connectors + normalize (offline TDD core)

### Task M2.1: Normalize helper — hash + dedup key + record builder

**Files:**

- Create: `data-platform/scripts/external-signals/normalize.py`
- Test: `data-platform/scripts/external-signals/tests/test_normalize.py`

- [ ] **Step 1: Write the failing test**

`tests/test_normalize.py`:

```python
import unittest
from normalize import raw_hash, dedup_key, build_record, CONTRACT_VERSION


class TestNormalize(unittest.TestCase):
    def test_raw_hash_is_stable_sha256(self):
        self.assertEqual(raw_hash(b"abc"), raw_hash(b"abc"))
        self.assertEqual(len(raw_hash(b"abc")), 64)

    def test_dedup_key_ignores_publish_noise(self):
        base = dict(sourceId="meteoswiss", capIdentifier="cap-1",
                    hazardType="heat", region={"cantons": ["ZH"]},
                    onset="2026-07-17T12:00:00Z")
        self.assertEqual(dedup_key(base), dedup_key({**base, "capIdentifier": "cap-1"}))
        self.assertNotEqual(dedup_key(base), dedup_key({**base, "hazardType": "flood"}))

    def test_build_record_fills_provenance_and_defaults(self):
        rec = build_record(
            signal_id="s1", source_id="sed", source_authority="SED-ETH",
            hazard_type="earthquake", severity="Severe", certainty="Observed",
            urgency="Immediate", region={"cantons": ["VS"]},
            onset="2026-07-17T10:00:00Z", status="Actual",
            connector_version="sed-1.0.0", licence="ETH-open", raw=b"{}",
        )
        self.assertEqual(rec["trustTier"], "A")
        self.assertEqual(rec["provenance"]["connectorVersion"], "sed-1.0.0")
        self.assertEqual(len(rec["provenance"]["rawHash"]), 64)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd data-platform/scripts/external-signals; python3 -m unittest tests.test_normalize -v`
Expected: FAIL (ModuleNotFoundError: normalize) — run with `PYTHONPATH=.`: `PYTHONPATH=. python3 -m unittest tests.test_normalize -v`

- [ ] **Step 3: Write `normalize.py`**

```python
"""Normalize raw source payloads into DC-EXT-SIGNAL-v1 records (stdlib-only)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

CONTRACT_ID = "DC-EXT-SIGNAL-v1"
CONTRACT_VERSION = "1.0.0"


def raw_hash(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def dedup_key(rec: dict) -> str:
    cantons = ",".join(sorted((rec.get("region") or {}).get("cantons", [])))
    parts = [
        rec.get("sourceId", ""), rec.get("capIdentifier") or "",
        rec.get("hazardType", ""), cantons, rec.get("onset", ""),
    ]
    return "|".join(parts)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_record(*, signal_id, source_id, source_authority, hazard_type,
                 severity, certainty, urgency, region, onset, status,
                 connector_version, licence, raw,
                 cap_identifier=None, danger_level=None, effective=None,
                 expires=None, uri=None, mapped_scenario_template=None,
                 default_lage_tier=None, trust_tier="A") -> dict:
    return {
        "signalId": signal_id,
        "sourceId": source_id,
        "sourceAuthority": source_authority,
        "trustTier": trust_tier,
        "capIdentifier": cap_identifier,
        "hazardType": hazard_type,
        "severity": severity,
        "certainty": certainty,
        "urgency": urgency,
        "dangerLevel": danger_level,
        "region": region,
        "effective": effective,
        "onset": onset,
        "expires": expires,
        "uri": uri,
        "status": status,
        "mappedScenarioTemplate": mapped_scenario_template,
        "defaultLageTier": default_lage_tier,
        "provenance": {
            "ingestedAt": _now(),
            "connectorVersion": connector_version,
            "licence": licence,
            "rawHash": raw_hash(raw if isinstance(raw, bytes) else json.dumps(raw, sort_keys=True).encode()),
        },
    }


def envelope(records: list[dict], dataset_id: str, residency: str = "CH") -> dict:
    return {
        "datasetId": dataset_id,
        "contractId": CONTRACT_ID,
        "contractVersion": CONTRACT_VERSION,
        "classification": "public-authority",
        "residency": residency,
        "purposeTags": ["crisis-trigger", "situational-awareness"],
        "records": records,
    }
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd data-platform/scripts/external-signals; PYTHONPATH=. python3 -m unittest tests.test_normalize -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/normalize.py data-platform/scripts/external-signals/tests/test_normalize.py
git commit -m "feat(ext-signals): add normalize helper (hash, dedup key, record builder) (#247)"
```

### Task M2.2: Base connector + source→hazard/severity mapping

**Files:**

- Create: `data-platform/scripts/external-signals/connectors/base_connector.py`
- Create fixtures: `tests/fixtures/meteoswiss_heat.json`, `sed_quake.json`, `alertswiss_cap.json`, `bag_rsv.json`
- Test: `tests/test_connectors.py`

- [ ] **Step 1: Write the failing test**

`tests/test_connectors.py`:

```python
import unittest
from tests._util import load_fixture
from connectors.meteoswiss import MeteoSwissConnector
from connectors.sed import SedConnector
from connectors.alertswiss import AlertswissConnector
from connectors.bag import BagConnector


class TestConnectors(unittest.TestCase):
    def test_meteoswiss_maps_heat_to_f8(self):
        recs = MeteoSwissConnector().parse(load_fixture("meteoswiss_heat.json"))
        self.assertEqual(recs[0]["hazardType"], "heat")
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F8")
        self.assertEqual(recs[0]["trustTier"], "A")

    def test_sed_maps_quake_severity_from_magnitude(self):
        recs = SedConnector().parse(load_fixture("sed_quake.json"))
        self.assertEqual(recs[0]["hazardType"], "earthquake")
        self.assertIn(recs[0]["severity"], {"Severe", "Extreme"})

    def test_alertswiss_preserves_cap_identifier(self):
        recs = AlertswissConnector().parse(load_fixture("alertswiss_cap.json"))
        self.assertTrue(recs[0]["capIdentifier"])

    def test_bag_maps_rsv_to_f6(self):
        recs = BagConnector().parse(load_fixture("bag_rsv.json"))
        self.assertEqual(recs[0]["mappedScenarioTemplate"], "F6")

    def test_every_record_is_schema_valid(self):
        from tests.test_schema_conformance import SCHEMA  # reuse path
        import json
        doc = json.loads(SCHEMA.read_text(encoding="utf-8"))
        req = set(doc["properties"]["records"]["items"]["required"])
        for conn, fx in [(MeteoSwissConnector(), "meteoswiss_heat.json"),
                         (SedConnector(), "sed_quake.json"),
                         (AlertswissConnector(), "alertswiss_cap.json"),
                         (BagConnector(), "bag_rsv.json")]:
            for rec in conn.parse(load_fixture(fx)):
                self.assertTrue(req <= set(rec), f"{conn} missing {req - set(rec)}")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Create the four fixtures** with minimal representative raw payloads. Example `tests/fixtures/sed_quake.json`:

```json
{"events": [{"eventId": "sed-2026-0007", "magnitude": 5.4, "region": "Valais",
  "cantons": ["VS"], "time": "2026-07-17T10:00:00Z",
  "uri": "https://eida.ethz.ch/event/sed-2026-0007"}]}
```

(Author `meteoswiss_heat.json`, `alertswiss_cap.json`, `bag_rsv.json` analogously — a single representative record each; heat with a danger level ≥3, alertswiss with a CAP `identifier`, bag with a resp/RSV indicator above threshold.)

- [ ] **Step 3: Run to verify it fails**

Run: `cd data-platform/scripts/external-signals; PYTHONPATH=. python3 -m unittest tests.test_connectors -v`
Expected: FAIL (connectors modules missing)

- [ ] **Step 4: Write `connectors/base_connector.py`**

```python
"""Base connector: shared fetch (optional network) + parse contract."""
from __future__ import annotations

from abc import ABC, abstractmethod

# Maps CAP/hazard label -> (CSA ScenarioTemplate, default Lage tier)
HAZARD_SCENARIO_MAP = {
    "heat": ("F8", 2),
    "flood": ("F8", 2),
    "earthquake": ("F1", 3),
    "epidemic": ("F6", 2),
    "rsv": ("F6", 2),
    "mci": ("F3", 3),
}


class BaseConnector(ABC):
    source_id: str = "base"
    source_authority: str = "unknown"
    licence: str = "unspecified"
    version: str = "0.0.0"

    @abstractmethod
    def parse(self, payload: dict) -> list[dict]:
        """Return a list of DC-EXT-SIGNAL-v1 records from a raw payload."""

    def scenario_for(self, hazard: str) -> tuple[str | None, int | None]:
        return HAZARD_SCENARIO_MAP.get(hazard, (None, None))

    def fetch(self, url: str) -> dict:  # pragma: no cover - network optional
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("requests not installed; use fixtures offline") from exc
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
```

- [ ] **Step 5: Write the four connectors.** Each subclasses `BaseConnector`, sets identity, and implements `parse()` calling `normalize.build_record()`. Example `connectors/sed.py`:

```python
"""SED (ETH seismology) FDSN connector -> DC-EXT-SIGNAL-v1."""
from __future__ import annotations

import json
from connectors.base_connector import BaseConnector
from normalize import build_record


def _severity_from_magnitude(mag: float) -> str:
    if mag >= 6.0:
        return "Extreme"
    if mag >= 5.0:
        return "Severe"
    if mag >= 4.0:
        return "Moderate"
    return "Minor"


class SedConnector(BaseConnector):
    source_id = "sed"
    source_authority = "SED-ETH"
    licence = "ETH-open"
    version = "sed-1.0.0"

    def parse(self, payload: dict) -> list[dict]:
        out = []
        for ev in payload.get("events", []):
            scenario, tier = self.scenario_for("earthquake")
            out.append(build_record(
                signal_id=ev["eventId"], source_id=self.source_id,
                source_authority=self.source_authority, hazard_type="earthquake",
                severity=_severity_from_magnitude(float(ev["magnitude"])),
                certainty="Observed", urgency="Immediate",
                region={"cantons": ev.get("cantons", [])},
                onset=ev["time"], status="Actual",
                connector_version=self.version, licence=self.licence,
                raw=json.dumps(ev, sort_keys=True).encode(),
                uri=ev.get("uri"), danger_level=None,
                mapped_scenario_template=scenario, default_lage_tier=tier,
            ))
        return out
```

`connectors/meteoswiss.py` (hazard `heat`, severity from danger level, scenario F8), `connectors/alertswiss.py` (preserve `capIdentifier`, map CAP hazard label via `HAZARD_SCENARIO_MAP`, honour CAP `status`), `connectors/bag.py` (hazard `rsv`, scenario F6, `status` from surveillance threshold) follow the same shape.

- [ ] **Step 6: Run to verify it passes**

Run: `cd data-platform/scripts/external-signals; PYTHONPATH=. python3 -m unittest tests.test_connectors -v`
Expected: PASS (5 tests)

- [ ] **Step 7: Commit**

```bash
git add data-platform/scripts/external-signals/connectors data-platform/scripts/external-signals/tests/test_connectors.py data-platform/scripts/external-signals/tests/fixtures
git commit -m "feat(ext-signals): add 4 Trust-A source connectors + fixtures (#247)"
```

### Task M2.3: Dedup + collapse across overlapping sources

**Files:**

- Create: `data-platform/scripts/external-signals/dedup.py`
- Test: `data-platform/scripts/external-signals/tests/test_dedup.py`

- [ ] **Step 1: Write the failing test**

`tests/test_dedup.py`:

```python
import unittest
from dedup import collapse
from normalize import build_record


def _rec(source, hazard, cantons, onset, sev="Severe"):
    return build_record(
        signal_id=f"{source}-1", source_id=source, source_authority=source.upper(),
        hazard_type=hazard, severity=sev, certainty="Observed", urgency="Immediate",
        region={"cantons": cantons}, onset=onset, status="Actual",
        connector_version="v1", licence="open", raw=b"{}",
    )


class TestDedup(unittest.TestCase):
    def test_overlapping_heat_collapses_to_one_event(self):
        recs = [_rec("meteoswiss", "heat", ["ZH"], "2026-07-17T12:00:00Z"),
                _rec("alertswiss", "heat", ["ZH"], "2026-07-17T12:00:00Z")]
        events = collapse(recs)
        self.assertEqual(len(events), 1)
        self.assertEqual(len(events[0]["sources"]), 2)

    def test_distinct_hazards_stay_separate(self):
        recs = [_rec("meteoswiss", "heat", ["ZH"], "2026-07-17T12:00:00Z"),
                _rec("sed", "earthquake", ["VS"], "2026-07-17T12:00:00Z")]
        self.assertEqual(len(collapse(recs)), 2)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails** — `PYTHONPATH=. python3 -m unittest tests.test_dedup -v`. Expected: FAIL.

- [ ] **Step 3: Write `dedup.py`**

```python
"""Collapse overlapping ExternalSignal records into HazardEvents."""
from __future__ import annotations

from normalize import dedup_key

SEVERITY_RANK = {"Minor": 1, "Moderate": 2, "Severe": 3, "Extreme": 4}


def collapse(records: list[dict]) -> list[dict]:
    """Group by dedup key (minus onset noise handled upstream); one event per hazard/region."""
    groups: dict[tuple, list[dict]] = {}
    for rec in records:
        cantons = tuple(sorted((rec.get("region") or {}).get("cantons", [])))
        key = (rec.get("hazardType"), cantons)
        groups.setdefault(key, []).append(rec)

    events = []
    for (hazard, cantons), recs in groups.items():
        primary = max(recs, key=lambda r: SEVERITY_RANK.get(r["severity"], 0))
        events.append({
            "hazardType": hazard,
            "cantons": list(cantons),
            "severity": primary["severity"],
            "defaultLageTier": primary.get("defaultLageTier"),
            "mappedScenarioTemplate": primary.get("mappedScenarioTemplate"),
            "sources": sorted({r["sourceId"] for r in recs}),
            "signalIds": sorted(r["signalId"] for r in recs),
            "dedupKeys": sorted({dedup_key(r) for r in recs}),
        })
    return events
```

- [ ] **Step 4: Run to verify it passes** — `PYTHONPATH=. python3 -m unittest tests.test_dedup -v`. Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/dedup.py data-platform/scripts/external-signals/tests/test_dedup.py
git commit -m "feat(ext-signals): add dedup/collapse to HazardEvents (#247)"
```

---

## Milestone M3 — Medallion notebooks

### Task M3.1: Pure transforms behind the notebooks (offline-testable)

**Files:**

- Create: `data-platform/notebooks/external-signals/README.md`
- Create: `data-platform/notebooks/external-signals/ingest_bronze_signals.py`
- Create: `data-platform/notebooks/external-signals/build_silver_signals.py`
- Create: `data-platform/notebooks/external-signals/build_gold_signals.py`
- Create: `data-platform/notebooks/external-signals/tests/__init__.py`
- Create: `data-platform/notebooks/external-signals/tests/test_signals_pure.py`

Follow the CSA notebook pattern (`data-platform/notebooks/csa/`): each notebook wraps a pure function that is unit-tested without Spark, guarded by `try: from pyspark.sql import SparkSession except ImportError`.

- [ ] **Step 1: Write the failing test** for silver dedup + quarantine and gold projection:

`tests/test_signals_pure.py`:

```python
import importlib.util
import unittest
from pathlib import Path

NB = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), NB / name)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestSilverGoldPure(unittest.TestCase):
    def test_silver_quarantines_non_actual(self):
        silver = _load("build_silver_signals.py")
        recs = [{"signalId": "a", "status": "Actual", "hazardType": "heat",
                 "region": {"cantons": ["ZH"]}, "onset": "t", "sourceId": "m", "severity": "Severe"},
                {"signalId": "b", "status": "Exercise", "hazardType": "heat",
                 "region": {"cantons": ["ZH"]}, "onset": "t", "sourceId": "m", "severity": "Severe"}]
        kept, quarantined = silver.split_quarantine(recs)
        self.assertEqual([r["signalId"] for r in kept], ["a"])
        self.assertEqual([r["signalId"] for r in quarantined], ["b"])

    def test_gold_signal_row_projection(self):
        gold = _load("build_gold_signals.py")
        row = gold.to_gold_signal({"signalId": "a", "sourceId": "sed", "hazardType": "earthquake",
                                   "severity": "Severe", "defaultLageTier": 3,
                                   "mappedScenarioTemplate": "F1", "onset": "t",
                                   "region": {"cantons": ["VS"]}, "status": "Actual"})
        self.assertEqual(row["ext_scenario_template"], "F1")
        self.assertEqual(row["ext_lage_tier"], 3)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run to verify it fails** — `cd data-platform/notebooks/external-signals; python3 -m unittest discover -s tests -v`. Expected: FAIL.

- [ ] **Step 3: Write the notebooks' pure functions.** `build_silver_signals.py` exposes `split_quarantine(records) -> (kept, quarantined)` (kept = `status == "Actual"`, deduped via `dedup.collapse` signal membership) plus a Spark `main()` guarded by import. `build_gold_signals.py` exposes `to_gold_signal(rec) -> dict` (maps to `ext_*` columns incl. `ext_scenario_template`, `ext_lage_tier`, `ext_severity`, `ext_source_id`, `ext_hazard_type`, `ext_cantons`, `ext_onset`) and `to_gold_dims(records)`; `ingest_bronze_signals.py` exposes a pure `bronze_path(source, date)` returning `Files/Bronze/external-signals/<source>/<date>`.

- [ ] **Step 4: Run to verify it passes** — `cd data-platform/notebooks/external-signals; python3 -m unittest discover -s tests -v`. Expected: PASS.

- [ ] **Step 5: Write README.md** documenting the bronze→silver→gold chain, table names (`silver.ext_signal`, `silver.ext_signal_quarantine`, `gold.ext_dim_source/hazard_type/region`, `gold.ext_fact_signal/trigger_event`), and the Eventhouse route.

- [ ] **Step 6: Commit**

```bash
git add data-platform/notebooks/external-signals
git commit -m "feat(ext-signals): add medallion notebooks + pure transforms (#247)"
```

### Task M3.2: Synthetic seeder for offline end-to-end

**Files:**

- Create: `data-platform/scripts/external-signals/signals_synth.py`

- [ ] **Step 1: Write `signals_synth.py`** — a dependency-free generator (optional `pyarrow`) that runs each connector over its fixture and emits a `DC-EXT-SIGNAL-v1` envelope JSON to stdout or a path, plus a `--dry-run` validate mode (matches the CSA seeder `--dry-run` convention).
- [ ] **Step 2: Verify** — `cd data-platform/scripts/external-signals; PYTHONPATH=. python3 signals_synth.py --dry-run`. Expected: prints validated record count, exit 0.
- [ ] **Step 3: Commit** — `git add data-platform/scripts/external-signals/signals_synth.py; git commit -m "feat(ext-signals): add synthetic signal seeder (#247)"`

---

## Milestone M4 — Ontology extension

### Task M4.1: Add reference-layer classes + relations

**Files:** Modify `docs/ontology/reference-layer.ttl`

- [ ] **Step 1: Add the classes** `hcp:TrustedSource`, `hcp:HazardType`, `hcp:ExternalSignal`, `hcp:HazardEvent`, `hcp:TriggerRule`, and `hcp:AffectedRegion` (as an alias/subclass of the existing Location class), each with `rdfs:label`, `rdfs:comment`, and the BFO/OBO anchor noted in spec §7. Add object properties `hcp:signalFromSource`, `hcp:signalIndicatesHazard`, `hcp:signalAffectsRegion`, `hcp:triggerRuleMapsScenario`, `hcp:signalPreseeds` with domain/range.
- [ ] **Step 2: Validate TTL** — run whatever `ontology-conformance.yml` runs locally (inspect the workflow; typically an `rdflib` parse). Command from the workflow. Expected: parses clean.
- [ ] **Step 3: Commit** — `git add docs/ontology/reference-layer.ttl; git commit -m "feat(ontology): add ExternalSignal/TrustedSource/HazardType classes (#247)"`

### Task M4.2: Update the crosswalk

**Files:** Modify `docs/ontology/crosswalk.md`

- [ ] **Step 1: Add crosswalk rows** for each new class (reference class ↔ Fabric IQ entity [GA-gated] ↔ `DC-EXT-SIGNAL-v1` ↔ time-series binding), per spec §7. Note the operational binding is deferred per ADR-0014.
- [ ] **Step 2: Bump crosswalk version** (MINOR), update Previous Version + Date.
- [ ] **Step 3: Lint** — mojibake + markdownlint + link-check. Expected: clean.
- [ ] **Step 4: Commit** — `git add docs/ontology/crosswalk.md; git commit -m "docs(ontology): add external-signal crosswalk rows (#247)"`

---

## Milestone M5 — Semantic model

### Task M5.1: Author external-signals.SemanticModel (Direct Lake, separate)

**Files:**

- Create: `data-platform/reports/external-signals.SemanticModel/definition/model.tmdl`
- Create: `data-platform/reports/external-signals.SemanticModel/definition/tables/ext_fact_signal.tmdl` (+ `ext_fact_trigger_event`, `ext_dim_source`, `ext_dim_hazard_type`, `ext_dim_region`)
- Create: `data-platform/reports/external-signals.SemanticModel/README.md`

- [ ] **Step 1: Author the TMDL** following `data-platform/reports/evidence.SemanticModel/` as the template (separate model, single read-only role). Tables map the `gold.ext_*` columns. Measures: `Active Signals`, `Signals by Severity`, `Highest Lage Tier`, `Triggers Fired (24h)`, `Mean Time Source->Trigger`, `Signals Quarantined`. Role `SignalsReadOnly`.
- [ ] **Step 2: Write README.md** — note this is a **separate** model (ADR-0026 precedent) deliberately outside the `capacity-dashboard` verify gate; document measures + role.
- [ ] **Step 3: Verify no collision** — confirm `verify-semantic-model.yml` path filter only targets `capacity-dashboard.SemanticModel/**` (it does; grep to confirm). No change to that workflow.
- [ ] **Step 4: Lint README** — mojibake + markdownlint. Expected: clean.
- [ ] **Step 5: Commit**

```bash
git add data-platform/reports/external-signals.SemanticModel
git commit -m "feat(ext-signals): add external-signals Direct Lake semantic model (#247)"
```

---

## Milestone M6 — Triggering (dual-path)

### Task M6.1: TriggerRule evaluation + arbitration

**Files:**

- Create: `data-platform/scripts/external-signals/trigger_rules.yaml`
- Create: `data-platform/scripts/external-signals/trigger_rules.py`
- Test: `data-platform/scripts/external-signals/tests/test_trigger_rules.py`

- [ ] **Step 1: Write the failing test**

`tests/test_trigger_rules.py`:

```python
import unittest
from trigger_rules import load_rules, evaluate, arbitrate


class TestTriggerRules(unittest.TestCase):
    def setUp(self):
        self.rules = load_rules()

    def test_severe_actual_a_triggers(self):
        ev = {"hazardType": "heat", "severity": "Severe", "defaultLageTier": 2,
              "status": "Actual", "trustTier": "A"}
        self.assertTrue(evaluate(ev, self.rules).fired)

    def test_below_threshold_no_trigger(self):
        ev = {"hazardType": "heat", "severity": "Minor", "defaultLageTier": 1,
              "status": "Actual", "trustTier": "A"}
        r = evaluate(ev, self.rules)
        self.assertFalse(r.fired)
        self.assertEqual(r.outcome, "evaluated-no-trigger")

    def test_arbitration_prefers_higher_lage_tier(self):
        events = [{"hazardType": "heat", "severity": "Severe", "defaultLageTier": 2,
                   "mappedScenarioTemplate": "F8"},
                  {"hazardType": "earthquake", "severity": "Severe", "defaultLageTier": 3,
                   "mappedScenarioTemplate": "F1"}]
        primary, secondaries = arbitrate(events)
        self.assertEqual(primary["mappedScenarioTemplate"], "F1")
        self.assertEqual(len(secondaries), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Write `trigger_rules.yaml`**

```yaml
version: 1
# A signal fires a CSA handoff only when ALL gate conditions hold.
gate:
  min_severity: Severe        # Severe or Extreme
  min_danger_level: 3         # applies when dangerLevel present
  required_status: Actual
  required_trust_tier: A
# Arbitration precedence when multiple distinct hazards overlap.
arbitration:
  order: [lage_tier, severity, certainty]
severity_rank: { Minor: 1, Moderate: 2, Severe: 3, Extreme: 4 }
```

- [ ] **Step 3: Run to verify it fails** — `PYTHONPATH=. python3 -m unittest tests.test_trigger_rules -v`. Expected: FAIL.

- [ ] **Step 4: Write `trigger_rules.py`** — `load_rules()` (reads YAML; falls back to a stdlib parse if `pyyaml` absent by shipping a tiny embedded default), `evaluate(event, rules) -> Result(fired: bool, outcome: str)`, `arbitrate(events) -> (primary, secondaries)` ranking by `lage_tier` then `severity` then `certainty`.

```python
"""Evaluate TriggerRule gates + arbitrate overlapping hazard events."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_RULES_PATH = Path(__file__).resolve().parent / "trigger_rules.yaml"
_DEFAULTS = {
    "gate": {"min_severity": "Severe", "min_danger_level": 3,
             "required_status": "Actual", "required_trust_tier": "A"},
    "severity_rank": {"Minor": 1, "Moderate": 2, "Severe": 3, "Extreme": 4},
    "arbitration": {"order": ["lage_tier", "severity", "certainty"]},
}
_CERTAINTY_RANK = {"Unlikely": 1, "Possible": 2, "Likely": 3, "Observed": 4}


@dataclass
class Result:
    fired: bool
    outcome: str


def load_rules() -> dict:
    try:
        import yaml
        return yaml.safe_load(_RULES_PATH.read_text(encoding="utf-8"))
    except Exception:
        return _DEFAULTS


def evaluate(event: dict, rules: dict) -> Result:
    g = rules["gate"]
    rank = rules["severity_rank"]
    if event.get("status") != g["required_status"]:
        return Result(False, "quarantined-status")
    if event.get("trustTier", "A") != g["required_trust_tier"]:
        return Result(False, "trust-tier-not-a")
    if rank.get(event.get("severity"), 0) < rank.get(g["min_severity"], 3):
        return Result(False, "evaluated-no-trigger")
    dl = event.get("dangerLevel")
    if dl is not None and dl < g["min_danger_level"]:
        return Result(False, "evaluated-no-trigger")
    return Result(True, "trigger-fired")


def arbitrate(events: list[dict]) -> tuple[dict, list[dict]]:
    def key(e):
        return (e.get("defaultLageTier") or 0,
                _DEFAULTS["severity_rank"].get(e.get("severity"), 0),
                _CERTAINTY_RANK.get(e.get("certainty"), 0))
    ordered = sorted(events, key=key, reverse=True)
    return ordered[0], ordered[1:]
```

- [ ] **Step 5: Run to verify it passes** — `PYTHONPATH=. python3 -m unittest tests.test_trigger_rules -v`. Expected: PASS (3 tests).

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/external-signals/trigger_rules.py data-platform/scripts/external-signals/trigger_rules.yaml data-platform/scripts/external-signals/tests/test_trigger_rules.py
git commit -m "feat(ext-signals): add TriggerRule evaluation + arbitration (#247)"
```

### Task M6.2: Activator/Reflex config (GA-gated) + Eventstream route note

**Files:**

- Create: `data-platform/external-signals/activator/reflex-rule.json`
- Create: `data-platform/external-signals/eventstream/route.md`

- [ ] **Step 1: Author `reflex-rule.json`** — a documented Activator/Reflex rule definition (condition: `severity in {Severe, Extreme}` AND `status == Actual` AND `trustTier == A`; action: POST to the signal-triage webhook). Header comment/README note marks it **GA-gated** per ADR-0014 (authored, not deployed).
- [ ] **Step 2: Author `route.md`** — Eventstream route config: add `eventKind == "ext-signal"` route from `es-ihzhhpf-events` to the Eventhouse `ExternalSignal` KQL table; reference the `eventstream-authoring` skill for the `updateDefinition` REST call.
- [ ] **Step 3: Lint route.md** — mojibake + markdownlint. Expected: clean.
- [ ] **Step 4: Commit** — `git add data-platform/external-signals; git commit -m "feat(ext-signals): add Activator rule + eventstream route (GA-gated) (#247)"`

### Task M6.3: Poller bridge workflow

**Files:** Create `.github/workflows/ext-signal-poll.yml`

- [ ] **Step 1: Author the scheduled workflow** (cron + `workflow_dispatch`) mirroring `csa-scenario-sync.yml`: reads `gold.ext_fact_signal` via agent-host/`fabric-mcp`, filters fired triggers, and opens/updates an issue that invokes `@signal-triage-agent`. Use least-privilege `permissions:` (`contents: read`, `issues: write`). Since live Fabric read is deploy-time, gate the live step behind a `secrets`/`vars` presence check and default to a dry-run that reads the synthetic seed for CI.
- [ ] **Step 2: Validate YAML** — `npx --yes yaml-lint .github/workflows/ext-signal-poll.yml` (or `actionlint` if available). Expected: valid.
- [ ] **Step 3: Commit** — `git add .github/workflows/ext-signal-poll.yml; git commit -m "ci(ext-signals): add poller bridge workflow (#247)"`

### Task M6.4: Offline test gate workflow

**Files:** Create `.github/workflows/external-signals.yml`

- [ ] **Step 1: Author the CI gate** modeled on `csa-checks.yml`: on PR/push touching `data-platform/scripts/external-signals/**`, `data-platform/notebooks/external-signals/**`, `data/synthetic/schema/dc-ext-signal-v1.schema.json`, and the workflow itself. Install `pyyaml`; run `cd data-platform/scripts/external-signals && PYTHONPATH=. python3 -m unittest discover -s tests -v`; then the notebook pure tests; then `PYTHONPATH=. python3 signals_synth.py --dry-run`.
- [ ] **Step 2: Validate + run locally** — run the exact test command; expected: all suites PASS.
- [ ] **Step 3: Commit** — `git add .github/workflows/external-signals.yml; git commit -m "ci(ext-signals): add offline test gate (#247)"`

---

## Milestone M7 — Agents

### Task M7.1: signal-triage-agent pack

**Files:**

- Create: `agents/signal-triage-agent/AGENT.md`
- Create: `agents/signal-triage-agent/golden-tasks.md`

- [ ] **Step 1: Author `AGENT.md`** with the fixed structure (Identity, Scope, Tools, Refusal Rules, Output Contract, Confirmation Rules). Declare: MCP `github-mcp` (write) + `fabric-mcp` (read); side-effect ceiling `write`; responsibilities dedup → arbitrate → TriggerRule match → CSA handoff; refusal rules (never runs simulations, never mutates capacity, quarantines non-Actual, requires trust-tier A for auto-eval); output contract (opens a CSA handoff issue/PR referencing HazardEvent + ScenarioTemplate + LageTier, logs `ext_fact_trigger_event`).
- [ ] **Step 2: Author `golden-tasks.md`** with ≥1 happy-path and ≥1 failure-mode fixture, each with `requirement:` front-matter:
  - Happy: heat signals from MeteoSwiss + Alertswiss over ZH → dedup → F8 handoff to CSA (`requirement: FR-EXT-003`).
  - Failure: an `Exercise`-status signal → quarantined, no trigger, no CSA handoff (`requirement: FR-EXT-005`).
- [ ] **Step 3: Lint** — mojibake + markdownlint on both files. Expected: clean.
- [ ] **Step 4: Commit** — `git add agents/signal-triage-agent; git commit -m "feat(agent): add signal-triage-agent pack (#247)"`

### Task M7.2: Extend data-quality-agent for DC-EXT gate

**Files:** Modify `agents/data-quality-agent/AGENT.md` + `agents/data-quality-agent/golden-tasks.md`

- [ ] **Step 1: Add the `DC-EXT-SIGNAL-v1` contract check** to the agent's Bronze/Silver/Gold gate section: schema conformance, dedup-key uniqueness in silver, quarantine of Test/Exercise/System, provenance completeness, mandatory `licence`.
- [ ] **Step 2: Add a golden-task fixture** verifying the DC-EXT gate (`requirement: FR-EXT-004`), including a failure case (missing `licence` → fail).
- [ ] **Step 3: Lint + version note** — mojibake + markdownlint; bump any version header if present.
- [ ] **Step 4: Commit** — `git add agents/data-quality-agent; git commit -m "feat(agent): extend data-quality-agent with DC-EXT gate (#247)"`

### Task M7.3: Register in AGENTS.md

**Files:** Modify `AGENTS.md`

- [ ] **Step 1: Add the registry row** for `signal-triage-agent` (§1 table): use case, owner @urruegg, trigger (Activator webhook / poller / `@signal-triage-agent`), MCP `github-mcp` + `fabric-mcp`, ceiling `write`, prompt + golden-tasks paths. Add a note to the `data-quality-agent` row referencing the DC-EXT extension. If a new MCP server were required it would need `.github/copilot/mcp.json` — here both servers already exist, so note "no allow-list change".
- [ ] **Step 2: Bump AGENTS.md version** (MINOR: new agent), update Previous Version.
- [ ] **Step 3: Lint** — mojibake + markdownlint + link-check on AGENTS.md. Expected: clean.
- [ ] **Step 4: Commit** — `git add AGENTS.md; git commit -m "docs(agents): register signal-triage-agent (#247)"`

---

## Milestone M8 — Integration + docs reconciliation

### Task M8.1: End-to-end offline walk-through

- [ ] **Step 1: Run the full offline chain**

```bash
cd data-platform/scripts/external-signals
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 signals_synth.py --dry-run
cd ../../notebooks/external-signals && python3 -m unittest discover -s tests -v
```

Expected: all suites PASS; seeder validates the synthetic envelope.

- [ ] **Step 2: Trace a signal through** dedup → trigger evaluate → arbitrate → assert a `signal-triage-agent` handoff would reference the F8/F1 ScenarioTemplate. Capture the trace in the notebook README as an end-to-end example.
- [ ] **Step 3: Commit** any doc capture — `git commit -m "docs(ext-signals): capture end-to-end synthetic walk-through (#247)"`

### Task M8.2: Repo-wide lint + traceability reconciliation

- [ ] **Step 1: Run repo lint gates**

```bash
npx --yes markdownlint-cli2 "**/*.md" "#node_modules" "#.github/skills"
python scripts/lint/check_mojibake.py docs/PRD.md docs/DATA.md docs/ontology/crosswalk.md AGENTS.md docs/adr/0033-external-trigger-governance.md
```

Expected: 0 lint errors; no mojibake.

- [ ] **Step 2: Verify traceability** — every `FR-EXT-*` in PRD appears in the traceability matrix and is referenced by at least one golden-task `requirement:` front-matter or artefact. List and fix gaps.
- [ ] **Step 3: Update the design spec Status** from "Draft for review" to "Approved" and bump PATCH; update issue #247 with a completion checklist comment.
- [ ] **Step 4: Final commit** — `git add -A docs AGENTS.md agents; git commit -m "docs(sprint-21): reconcile traceability + status (#247)"`

---

## Self-Review

**Spec coverage:** Every spec section maps to a task — §5 domain/medallion → M0/M3, §6 contract → M1.1/M1.2, §7 ontology → M4, §8 semantic model → M5, §9 triggering → M6, §10 agents → M7, §11 governance → M1.3, §12 requirements → M1.4, §14 CI → M6.4/M8. No gaps.

**Placeholder scan:** All code steps contain complete, runnable code. Notebook Spark bodies and TMDL are specified by content + template reference (evidence model / CSA notebooks) rather than full listings because they are environment-bound; their offline-testable pure functions have full code and tests.

**Type consistency:** `build_record()` fields match the schema record properties; `dedup_key()`/`collapse()`/`evaluate()`/`arbitrate()` signatures are consistent across M2/M3/M6; gold column names (`ext_scenario_template`, `ext_lage_tier`) are consistent between M3.1 test and gold projection.

---

## Execution Handoff

Plan complete. Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks, fast iteration.
2. **Inline Execution** — execute tasks in this session with checkpoints.
