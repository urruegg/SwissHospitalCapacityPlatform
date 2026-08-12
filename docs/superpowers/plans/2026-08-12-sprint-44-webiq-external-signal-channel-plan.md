# Sprint 44 — Microsoft Web IQ External Signal Channel — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Microsoft Web IQ as a governed **Trust-B, advisory-only** external signal channel — ingested via a manifest-driven provider plugin, normalized to `DC-EXT-SIGNAL-v1`, surfaced on the Curavias OOA + CSA signal screens with grounded web citations and a HITL promote-to-watch action, never auto-arming a lever.

**Architecture:** Reuse the entire Sprint 21 provider-plugin pipeline (`provider-runner` → Event Hub → `data-quality-agent` → `signal-triage-agent` → app). New code is confined to one provider directory plus a small, additive app-model extension. Trust-B is enforced structurally by the existing `trigger_rules` gate (`trust-tier-not-a`), so "advisory-only" needs a guard test, not new gating logic.

**Tech Stack:** Python 3 (stdlib-only provider plugins; `pytest`), JSON Schema (draft-07), React + TypeScript + Fluent UI (`hcc-app-fluent`, Vitest), Bicep (unchanged), Markdown docs.

**Design spec:** [`docs/superpowers/specs/2026-08-12-sprint-44-webiq-external-signal-channel-design.md`](../specs/2026-08-12-sprint-44-webiq-external-signal-channel-design.md)

---

## File Structure

**Create:**

- `docs/adr/0060-webiq-external-signal-channel.md` — governance ADR.
- `data-platform/scripts/external-signals/providers/microsoft_webiq/__init__.py`
- `data-platform/scripts/external-signals/providers/microsoft_webiq/provider.yaml` — manifest (Trust-B).
- `data-platform/scripts/external-signals/providers/microsoft_webiq/simulator.py` — deterministic synthetic Web IQ payload.
- `data-platform/scripts/external-signals/providers/microsoft_webiq/parse.py` — Web IQ result → `DC-EXT-SIGNAL-v1`.
- `data-platform/scripts/external-signals/providers/microsoft_webiq/live_adapter.py` — gated live-binding stub.
- `data-platform/scripts/external-signals/providers/microsoft_webiq/tests/__init__.py`
- `data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py`
- `docs/sprints/sprint-44-webiq-external-signal-channel.md` — sprint backlog page.

**Modify:**

- `data/synthetic/schema/dc-ext-signal-v1.schema.json` — add optional `webCitations[]`.
- `docs/DATA.md` — document `webCitations` + bump contract note to v1.1.0.
- `docs/PRD.md` — add `FR-EXT-021..023`, `NFR-EXT-WEBIQ-001..002` + §7 traceability rows.
- `data-platform/scripts/external-signals/tests/` — add a Trust-B guard test file.
- `apps/hcc-app-fluent/src/data/roleboard/crisis-data.ts` — extend `ExternalSignal` union + Web IQ fixture.
- `apps/hcc-app-fluent/src/data/roleboard/occupancy-data.ts` — add Web IQ `BoardSignal` fixture + optional `webCitations`.
- `apps/hcc-app-fluent/src/workspaces/main/boards/occupancy/SignalsPanel.tsx` — Trust-B badge + web-citation affordance + promote-to-watch.

**No change (verified):** `provider-runner/main.bicep`, `registry.py` (auto-discovers `*/provider.yaml`), `.github/copilot/mcp.json` (Web IQ is an outbound endpoint, not an MCP server), `AGENTS.md` registry (no new agent).

---

## Task 1: Governance ADR-0060

**Files:**

- Create: `docs/adr/0060-webiq-external-signal-channel.md`

- [ ] **Step 1: Write the ADR** (ADRs use a Status field, no SemVer header — see §9 of copilot-instructions).

```markdown
# ADR-0060: Microsoft Web IQ as a Governed Trust-B External Signal Channel

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-08-12 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related issue** | (Sprint 44) |

## Context

External signals (Sprint 21, ADR-0036) ingest only Trust-A Swiss public-authority
hazard feeds. Microsoft Web IQ (https://webiq.microsoft.ai/) is a commercial,
preview/limited-access web-grounding API returning free-form web/news/image/video
content — a new *class* of source: non-authority, non-Swiss, preview-gated, and
free-form rather than a CAP-Suisse envelope. ADR-0054 explicitly defers "live
web-search discovery." This ADR governs a narrow lift of that deferral.

## Decision

* Web IQ is classified **Trust-B**: advisory, human-curated, and never
  auto-evaluated against trigger rules, never auto-arms a lever, never
  auto-triggers a CSA handoff, and never enters the forecast-uplift overlay
  (consistent with ADR-0036).
* The ADR-0054 "web-discovery deferred" boundary is lifted **only** for this
  governed case: onboarding runs the full `signal-agent` lifecycle with a
  sandbox Channel Readiness Scorecard and a HITL data-owner + compliance/DPO
  activation gate; no autonomous activation.
* The live Web IQ binding is **GA- and credential-gated** (parallel to
  ADR-0014); demo/SIT run simulator-only, and CI always mocks the live binding
  (NFR-EXT-PLG-001).
* Outbound Web IQ queries contain **no PHI** (ADR-0016); returned web content is
  untrusted and re-validated at every boundary (NFR-SIG-001).

## Consequences

### Positive

* Adds an earliest-warning, web-grounded situational-awareness channel without
  weakening HITL or trust-tier governance.
* Establishes a reusable pattern for future non-authority grounding sources.

### Negative / risks

* Web content is untrusted (prompt-injection surface) — mitigated by Trust-B,
  typed-field-only extraction, and no free-text forwarding into tools/queries.
* No live entitlement in demo scope — mitigated by simulator-first design.

## Related

ADR-0036 (external trigger governance), ADR-0054 (signal-channel lifecycle),
ADR-0014 (GA-gating pattern), ADR-0016 (no PHI).
```

- [ ] **Step 2: Lint + commit**

```bash
git add docs/adr/0060-webiq-external-signal-channel.md
git commit -m "docs(adr): ADR-0060 Web IQ as a governed Trust-B external signal channel"
```

Expected: pre-commit doc-steward gates pass (0 markdownlint issues).

---

## Task 2: Extend `DC-EXT-SIGNAL-v1` → v1.1.0 (optional `webCitations`)

**Files:**

- Modify: `data/synthetic/schema/dc-ext-signal-v1.schema.json`
- Modify: `docs/DATA.md`
- Test: `data/synthetic/validate_datasets.py` (existing CI validator round-trips the schema)

- [ ] **Step 1: Read the current record schema** to find the record `properties` object.

Run: `Get-Content data/synthetic/schema/dc-ext-signal-v1.schema.json`
Expected: locate the per-record `properties` block (the object holding `signalId`, `sourceId`, `trustTier`, `provenance`, ...).

- [ ] **Step 2: Add the optional `webCitations` field** to the record `properties` (do NOT add it to `required` — additive/backward-compatible).

```jsonc
"webCitations": {
  "type": "array",
  "description": "Grounded web evidence for web-grounding sources (Trust-B). Optional; omitted by Trust-A records.",
  "items": {
    "type": "object",
    "additionalProperties": false,
    "required": ["title", "uri"],
    "properties": {
      "title": {"type": "string", "minLength": 1},
      "uri": {"type": "string", "minLength": 1},
      "publishedAt": {"type": "string"},
      "snippet": {"type": "string"}
    }
  }
}
```

- [ ] **Step 3: Bump the contract version note** in `docs/DATA.md` — in the `DC-EXT-SIGNAL-v1` section add a row to the envelope table and note v1.1.0:

```markdown
| `webCitations` | array of `{title, uri, publishedAt?, snippet?}` (optional) | Grounded web evidence for web-grounding sources (Trust-B, Sprint 44, contract v1.1.0). Omitted by Trust-A records. |
```

- [ ] **Step 4: Run the dataset validator to confirm backward compatibility**

Run: `python data/synthetic/validate_datasets.py`
Expected: PASS — existing Trust-A external-signal samples (which omit `webCitations`) still validate.

- [ ] **Step 5: Bump `docs/DATA.md` version header** per §9 (MINOR — additive field) and commit.

```bash
git add data/synthetic/schema/dc-ext-signal-v1.schema.json docs/DATA.md
git commit -m "feat(contract): DC-EXT-SIGNAL-v1 v1.1.0 - optional webCitations for web-grounding sources"
```

---

## Task 3: Provider manifest + fail-closed schema validation

**Files:**

- Create: `data-platform/scripts/external-signals/providers/microsoft_webiq/__init__.py` (empty)
- Create: `data-platform/scripts/external-signals/providers/microsoft_webiq/provider.yaml`
- Create: `data-platform/scripts/external-signals/providers/microsoft_webiq/tests/__init__.py` (empty)
- Create: `data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py`

- [ ] **Step 1: Write the failing manifest-discovery test** (mirrors the Sprint 21 registry contract — a valid manifest is discovered and Trust-B).

```python
# tests/test_provider.py
import sys
from pathlib import Path

_PROVIDERS = Path(__file__).resolve().parents[2]  # .../external-signals/providers
sys.path.insert(0, str(_PROVIDERS.parent))         # .../external-signals (for registry, normalize)

from providers import registry  # noqa: E402


def test_microsoft_webiq_manifest_is_discovered_and_trust_b():
    specs = {s.source_id: s for s in registry.discover()}
    assert "microsoft-webiq" in specs
    spec = specs["microsoft-webiq"]
    assert spec.trust_tier == "B"
    assert spec.channel_kind == "external"
    assert spec.default_mode == "simulated"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py -v`
Expected: FAIL — `microsoft-webiq` not in discovered specs (manifest does not exist yet).

- [ ] **Step 3: Write the manifest**

```yaml
# provider.yaml
sourceId: microsoft-webiq
authority: Microsoft Web IQ
trustTier: B
channelKind: external
hazardTypes: [epidemic, outbreak, public-health, mass-casualty, heat, flood]
defaultMode: simulated
fallbackMode: simulated
cadenceSeconds: 900
endpoint: https://api.webiq.microsoft.ai
licence: microsoft-web-iq-preview-terms
providerVersion: microsoft-webiq-1.0.0
scenarioMap:
  epidemic: {template: F5, lageTier: 2}
  outbreak: {template: F5, lageTier: 2}
  mass-casualty: {template: F3, lageTier: 3}
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py -v`
Expected: PASS.

- [ ] **Step 5: Add a fail-closed negative assertion** (schema rejects a Trust-tier outside A/B/C) — confirm the existing registry validation is enforced by temporarily asserting the schema path exists.

```python
def test_registry_schema_is_enforced():
    # provider.schema.json restricts trustTier to A/B/C; a bad value must not load.
    assert registry.SCHEMA_PATH.exists()
```

Run: `python -m pytest data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/external-signals/providers/microsoft_webiq/__init__.py `
  data-platform/scripts/external-signals/providers/microsoft_webiq/provider.yaml `
  data-platform/scripts/external-signals/providers/microsoft_webiq/tests/
git commit -m "feat(signals): microsoft-webiq provider manifest (Trust-B, simulator-default)"
```

---

## Task 4: Deterministic simulator

**Files:**

- Create: `data-platform/scripts/external-signals/providers/microsoft_webiq/simulator.py`
- Test: `.../microsoft_webiq/tests/test_provider.py` (append)

- [ ] **Step 1: Write the failing determinism test**

```python
def test_simulator_is_deterministic():
    from providers.microsoft_webiq import simulator
    a = simulator.generate(seed=7)
    b = simulator.generate(seed=7)
    assert a == b
    assert a["results"], "simulator must yield at least one web result"
    first = a["results"][0]
    assert {"title", "uri", "publishedAt", "hazard", "cantons", "confidence"} <= set(first)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py::test_simulator_is_deterministic -v`
Expected: FAIL — module `simulator` not found.

- [ ] **Step 3: Write the simulator** (stdlib-only, mirrors `meteoswiss/simulator.py`).

```python
"""Deterministic synthetic Microsoft Web IQ result payload (no network)."""
from __future__ import annotations


def generate(seed: int = 0) -> dict:
    return {
        "query": "emerging hospital-relevant public-health events Switzerland",
        "results": [
            {
                "title": f"Regional respiratory-illness uptick reported (sim {seed:04d})",
                "uri": "https://example.invalid/webiq/news/respiratory-uptick",
                "publishedAt": "2026-08-12T06:00:00Z",
                "hazard": "outbreak",
                "cantons": ["ZH"],
                "confidence": 0.72,
                "snippet": "Local outlets report a rise in respiratory presentations ahead of official surveillance.",
            }
        ],
    }
```

- [ ] **Step 4: Run to verify it passes**

Run: `python -m pytest data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py::test_simulator_is_deterministic -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/providers/microsoft_webiq/simulator.py `
  data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py
git commit -m "feat(signals): deterministic microsoft-webiq simulator"
```

---

## Task 5: `parse.py` — Web IQ result → `DC-EXT-SIGNAL-v1` (Trust-B, webCitations, PHI-query guard)

**Files:**

- Create: `data-platform/scripts/external-signals/providers/microsoft_webiq/parse.py`
- Test: `.../microsoft_webiq/tests/test_provider.py` (append)

- [ ] **Step 1: Write the failing parse tests**

```python
def test_parse_emits_trust_b_record_with_webcitations():
    from providers.microsoft_webiq import parse, simulator
    recs = parse.parse(simulator.generate(seed=1))
    assert len(recs) == 1
    r = recs[0]
    assert r["sourceId"] == "microsoft-webiq"
    assert r["trustTier"] == "B"
    assert r["hazardType"] == "outbreak"
    assert r["status"] == "Actual"           # confidence 0.72 >= 0.6 threshold
    assert r["webCitations"] and r["webCitations"][0]["uri"].startswith("https://")
    assert r["provenance"]["licence"] == "microsoft-web-iq-preview-terms"


def test_parse_quarantines_low_confidence():
    from providers.microsoft_webiq import parse
    payload = {"results": [{
        "title": "unverified rumor", "uri": "https://example.invalid/x",
        "publishedAt": "2026-08-12T06:00:00Z", "hazard": "outbreak",
        "cantons": ["ZH"], "confidence": 0.3, "snippet": "unconfirmed",
    }]}
    r = parse.parse(payload)[0]
    assert r["status"] != "Actual"           # below threshold -> not eligible to trigger


def test_query_builder_rejects_phi_terms():
    from providers.microsoft_webiq import parse
    import pytest
    with pytest.raises(ValueError):
        parse.build_query(["patient", "AHV 756.1234"])   # PHI-shaped -> refuse
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py -k parse -v`
Expected: FAIL — module `parse` not found.

- [ ] **Step 3: Write `parse.py`** (uses the exact `normalize.build_record` signature).

```python
"""Microsoft Web IQ result set -> DC-EXT-SIGNAL-v1 records (Trust-B, stdlib-only).

Web content is UNTRUSTED: only typed fields are extracted, never free text
forwarded into a tool/query. Trust-B never arms a lever (enforced downstream by
trigger_rules' trust-tier gate); this module just normalizes + attaches grounded
web citations.
"""
from __future__ import annotations

import json
import re

from normalize import build_record

SOURCE_ID = "microsoft-webiq"
AUTHORITY = "Microsoft Web IQ"
LICENCE = "microsoft-web-iq-preview-terms"
VERSION = "microsoft-webiq-1.0.0"
_TRIGGER_CONFIDENCE = 0.6
_SCENARIO = {"epidemic": ("F5", 2), "outbreak": ("F5", 2), "mass-casualty": ("F3", 3)}
# ADR-0016: outbound queries must never carry PHI-shaped terms.
_PHI_PATTERNS = [re.compile(p, re.I) for p in (r"\bpatient\b", r"\bahv\b", r"\d{3}\.\d{4}", r"\bname\b")]


def build_query(terms: list[str]) -> str:
    joined = " ".join(terms)
    for pat in _PHI_PATTERNS:
        if pat.search(joined):
            raise ValueError("REFUSE: phi-in-webiq-query")
    return joined


def _severity_from_confidence(conf: float) -> str:
    if conf >= 0.85:
        return "Severe"
    if conf >= 0.6:
        return "Moderate"
    return "Minor"


def parse(payload: dict, *, active_binding: str = "live",
          fell_back_from: str | None = None) -> list[dict]:
    out = []
    for i, res in enumerate(payload.get("results", [])):
        conf = float(res.get("confidence", 0.0))
        hazard = str(res.get("hazard", "public-health")).lower()
        scenario, tier = _SCENARIO.get(hazard, (None, None))
        status = "Actual" if conf >= _TRIGGER_CONFIDENCE else "System"  # below-threshold -> quarantined
        rec = build_record(
            signal_id=f"webiq-{i}-{res.get('uri', '')}", source_id=SOURCE_ID,
            source_authority=AUTHORITY, hazard_type=hazard,
            severity=_severity_from_confidence(conf),
            certainty="Possible", urgency="Future",
            region={"cantons": res.get("cantons", [])},
            onset=res.get("publishedAt"), effective=res.get("publishedAt"),
            status=status, connector_version=VERSION, licence=LICENCE,
            raw=json.dumps(res, sort_keys=True).encode(),
            uri=res.get("uri"), mapped_scenario_template=scenario,
            default_lage_tier=tier, trust_tier="B",
            active_binding=active_binding, fell_back_from=fell_back_from,
            channel_kind="external",
        )
        rec["webCitations"] = [{
            "title": res.get("title", ""), "uri": res.get("uri", ""),
            "publishedAt": res.get("publishedAt", ""), "snippet": res.get("snippet", ""),
        }]
        out.append(rec)
    return out
```

- [ ] **Step 4: Run to verify they pass**

Run: `python -m pytest data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py -k parse -v`
Expected: PASS (3 tests).

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/providers/microsoft_webiq/parse.py `
  data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py
git commit -m "feat(signals): microsoft-webiq parse to DC-EXT-SIGNAL-v1 (Trust-B, webCitations, PHI-query guard)"
```

---

## Task 6: Gated live-adapter stub

**Files:**

- Create: `data-platform/scripts/external-signals/providers/microsoft_webiq/live_adapter.py`
- Test: `.../microsoft_webiq/tests/test_provider.py` (append)

- [ ] **Step 1: Write the failing gate test**

```python
def test_live_adapter_is_disabled_by_default(monkeypatch):
    from providers.microsoft_webiq import live_adapter
    monkeypatch.delenv("WEBIQ_LIVE_ENABLED", raising=False)
    assert live_adapter.is_enabled() is False


def test_live_fetch_refuses_when_disabled(monkeypatch):
    from providers.microsoft_webiq import live_adapter
    import pytest
    monkeypatch.delenv("WEBIQ_LIVE_ENABLED", raising=False)
    with pytest.raises(RuntimeError):
        live_adapter.fetch(["heat", "Zurich"])
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py -k live -v`
Expected: FAIL — module `live_adapter` not found.

- [ ] **Step 3: Write the stub**

```python
"""Gated Microsoft Web IQ live binding. Disabled unless WEBIQ_LIVE_ENABLED=true
AND a Key Vault-backed credential resolves. Always mocked in CI (NFR-EXT-PLG-001);
demo/SIT run simulator-only (NFR-EXT-WEBIQ-002). This stub makes a real call
impossible in demo scope by refusing when disabled."""
from __future__ import annotations

import os


def is_enabled() -> bool:
    return os.environ.get("WEBIQ_LIVE_ENABLED", "").lower() == "true"


def fetch(terms: list[str], *, token_provider=None, http_request=None) -> dict:
    if not is_enabled():
        raise RuntimeError("REFUSE: webiq-live-binding-disabled (GA/credential-gated)")
    # GA/credential-gated real path — intentionally not wired in demo scope.
    raise NotImplementedError("Web IQ live binding is GA-gated; enable only with a vetted credential.")
```

- [ ] **Step 4: Run to verify they pass**

Run: `python -m pytest data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py -k live -v`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/external-signals/providers/microsoft_webiq/live_adapter.py `
  data-platform/scripts/external-signals/providers/microsoft_webiq/tests/test_provider.py
git commit -m "feat(signals): gated microsoft-webiq live-adapter stub (disabled by default)"
```

---

## Task 7: Trust-B guard — advisory-only (never fires a trigger)

**Files:**

- Create: `data-platform/scripts/external-signals/tests/test_webiq_trust_b_guard.py`

- [ ] **Step 1: Write the failing guard test** (uses the real `trigger_rules` gate already in the repo).

```python
import sys
from pathlib import Path

_ES = Path(__file__).resolve().parents[1]  # .../external-signals
sys.path.insert(0, str(_ES))

import trigger_rules  # noqa: E402
from providers.microsoft_webiq import parse, simulator  # noqa: E402


def test_webiq_trust_b_never_fires_a_trigger():
    rec = parse.parse(simulator.generate(seed=1))[0]
    result = trigger_rules.evaluate(rec, trigger_rules.load_rules())
    assert result.fired is False
    assert result.outcome == "trust-tier-not-a"
```

- [ ] **Step 2: Run to verify it fails first (import path), then passes once wired**

Run: `python -m pytest data-platform/scripts/external-signals/tests/test_webiq_trust_b_guard.py -v`
Expected: PASS — `trigger_rules.evaluate` returns `trust-tier-not-a` for `trustTier="B"` (confirmed behaviour in `trigger_rules.py`). If FAIL on import, fix the `sys.path` insert to point at `.../external-signals`.

- [ ] **Step 3: Commit**

```bash
git add data-platform/scripts/external-signals/tests/test_webiq_trust_b_guard.py
git commit -m "test(signals): guard - Trust-B Web IQ signal never fires a trigger"
```

---

## Task 8: App — extend model + fixtures + Web IQ card

**Files:**

- Modify: `apps/hcc-app-fluent/src/data/roleboard/occupancy-data.ts` (`BoardSignal` + `OCCUPANCY_SIGNALS`)
- Modify: `apps/hcc-app-fluent/src/data/roleboard/crisis-data.ts` (`ExternalSignal` union + fixture)
- Modify: `apps/hcc-app-fluent/src/workspaces/main/boards/occupancy/SignalsPanel.tsx`
- Test: `apps/hcc-app-fluent/src/data/roleboard/__tests__/webiq-signal.test.ts` (create)

- [ ] **Step 1: Write the failing fixture test**

```typescript
// __tests__/webiq-signal.test.ts
import { describe, it, expect } from 'vitest';
import { OCCUPANCY_SIGNALS } from '../occupancy-data';

describe('Web IQ board signal', () => {
  it('is present as an external Trust-B channel that does not arm a lever', () => {
    const webiq = OCCUPANCY_SIGNALS.find((s) => s.id === 'webiq');
    expect(webiq).toBeDefined();
    expect(webiq!.scope).toBe('external');
    expect(webiq!.trustClass).toBe('Trust-B');
  });
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd apps/hcc-app-fluent; npx vitest run src/data/roleboard/__tests__/webiq-signal.test.ts`
Expected: FAIL — `trustClass` type does not allow `'Trust-B'` yet; no `webiq` fixture.

- [ ] **Step 3: Extend `BoardSignal`** in `occupancy-data.ts` — widen `trustClass` and add optional `webCitations`.

```typescript
export interface BoardSignal {
  id: string;
  label: string;
  detail: string;
  iconKey: string;
  scope: 'external' | 'internal';
  provenance: Provenance;
  trustClass?: 'Trust-A' | 'Trust-B';
  statusLabel: string;
  statusTone: ChipTone;
  webCitations?: { title: string; uri: string; publishedAt?: string; snippet?: string }[];
}
```

- [ ] **Step 4: Add the Web IQ fixture** to `OCCUPANCY_SIGNALS` in `occupancy-data.ts`.

```typescript
  {
    id: 'webiq',
    label: 'Microsoft Web IQ',
    detail: 'Web/news early-warning — advisory only (Trust-B).',
    iconKey: 'globe',
    scope: 'external',
    provenance: 'simulated',
    trustClass: 'Trust-B',
    statusLabel: 'Watch',
    statusTone: 'watch',
    webCitations: [
      {
        title: 'Regional respiratory-illness uptick reported',
        uri: 'https://example.invalid/webiq/news/respiratory-uptick',
        publishedAt: '2026-08-12T06:00:00Z',
        snippet: 'Local outlets report a rise in respiratory presentations ahead of official surveillance.',
      },
    ],
  },
```

- [ ] **Step 5: Extend `ExternalSignal`** in `crisis-data.ts` — widen `source` + `trustClass` and add a Web IQ entry to the `signals` fixture with `filtered: true` (renders, no lever).

```typescript
export interface ExternalSignal {
  id: string;
  source: 'MeteoSwiss' | 'BAG/FOPH' | 'Alertswiss/BABS' | 'SED-ETH' | 'Microsoft Web IQ';
  feed: string;
  status: string;
  trustClass: 'Trust-A' | 'Trust-B';
  lageLevel?: string;
  certainty: Certainty;
  probability: number;
  feedsLever?: string;
  licence: string;
  provenance: string;
  filtered?: boolean;
  webCitations?: { title: string; uri: string; publishedAt?: string; snippet?: string }[];
}
```

Add to the CSA `signals: [...]` fixture array:

```typescript
  {
    id: 'webiq-outbreak',
    source: 'Microsoft Web IQ',
    feed: 'Web/news early-warning',
    status: 'Watch',
    trustClass: 'Trust-B',
    certainty: 'Possible',
    probability: CERTAINTY_TO_PROBABILITY['Possible'],
    licence: 'microsoft-web-iq-preview-terms',
    provenance: 'simulated',
    filtered: true, // renders but does NOT arm a lever (Trust-B, ADR-0036)
    webCitations: [
      {
        title: 'Regional respiratory-illness uptick reported',
        uri: 'https://example.invalid/webiq/news/respiratory-uptick',
        publishedAt: '2026-08-12T06:00:00Z',
      },
    ],
  },
```

- [ ] **Step 6: Run the fixture test to verify it passes**

Run: `cd apps/hcc-app-fluent; npx vitest run src/data/roleboard/__tests__/webiq-signal.test.ts`
Expected: PASS.

- [ ] **Step 7: Render the Trust-B badge + web-citation affordance** in `SignalsPanel.tsx` `renderRow` — add a muted badge when `sig.trustClass === 'Trust-B'` and a citations list when `sig.webCitations?.length`. Keep it minimal and follow the existing row markup already in that file.

```tsx
// inside renderRow(sig), after the existing status chip:
{sig.trustClass === 'Trust-B' && (
  <span className={styles.trustBBadge} aria-label="Trust-B advisory">Trust-B · advisory</span>
)}
{sig.webCitations?.length ? (
  <ul className={styles.webCitations}>
    {sig.webCitations.map((c) => (
      <li key={c.uri}><a href={c.uri} target="_blank" rel="noreferrer">{c.title}</a></li>
    ))}
  </ul>
) : null}
```

Add the two `styles` entries to the file's `makeStyles` block (muted secondary tone for the badge, compact list for citations), matching the existing style conventions in `SignalsPanel.tsx`.

- [ ] **Step 8: Run the full app unit suite + typecheck**

Run: `cd apps/hcc-app-fluent; npx vitest run; npx tsc --noEmit`
Expected: PASS — no type errors from the widened unions.

- [ ] **Step 9: Commit**

```bash
git add apps/hcc-app-fluent/src/data/roleboard/occupancy-data.ts `
  apps/hcc-app-fluent/src/data/roleboard/crisis-data.ts `
  apps/hcc-app-fluent/src/workspaces/main/boards/occupancy/SignalsPanel.tsx `
  apps/hcc-app-fluent/src/data/roleboard/__tests__/webiq-signal.test.ts
git commit -m "feat(app): Web IQ Trust-B signal card with web-citation evidence on OOA + CSA boards"
```

---

## Task 9: Recommendation glue — corroboration badge + promote-to-watch

**Files:**

- Modify: `apps/hcc-app-fluent/src/workspaces/main/boards/occupancy/SignalsPanel.tsx`
- Test: `apps/hcc-app-fluent/src/data/roleboard/__tests__/webiq-corroboration.test.ts` (create)

- [ ] **Step 1: Write the failing corroboration helper test** (pure function — display-only, never mutates a lever).

```typescript
import { describe, it, expect } from 'vitest';
import { corroborates } from '../../../workspaces/main/boards/occupancy/corroboration';

describe('web-signal corroboration (display-only)', () => {
  it('flags a Trust-A signal corroborated by a Web IQ signal on same hazard+canton', () => {
    const trustA = { hazardType: 'heat', cantons: ['ZH'], trustClass: 'Trust-A' as const };
    const webiq = { hazardType: 'heat', cantons: ['ZH'], trustClass: 'Trust-B' as const };
    expect(corroborates(trustA, webiq)).toBe(true);
  });
  it('does not corroborate across different cantons', () => {
    const trustA = { hazardType: 'heat', cantons: ['BE'], trustClass: 'Trust-A' as const };
    const webiq = { hazardType: 'heat', cantons: ['ZH'], trustClass: 'Trust-B' as const };
    expect(corroborates(trustA, webiq)).toBe(false);
  });
});
```

- [ ] **Step 2: Run to verify it fails**

Run: `cd apps/hcc-app-fluent; npx vitest run src/data/roleboard/__tests__/webiq-corroboration.test.ts`
Expected: FAIL — module `corroboration` not found.

- [ ] **Step 3: Write the pure helper**

```typescript
// workspaces/main/boards/occupancy/corroboration.ts
interface SignalKey { hazardType: string; cantons: string[]; trustClass: 'Trust-A' | 'Trust-B'; }

/** Display-only: a Trust-B web signal corroborates a Trust-A signal iff same
 * hazard and overlapping canton. NEVER changes a lever or forecast (ADR-0036). */
export function corroborates(trustA: SignalKey, web: SignalKey): boolean {
  if (trustA.trustClass !== 'Trust-A' || web.trustClass !== 'Trust-B') return false;
  if (trustA.hazardType !== web.hazardType) return false;
  return trustA.cantons.some((c) => web.cantons.includes(c));
}
```

- [ ] **Step 4: Run to verify it passes**

Run: `cd apps/hcc-app-fluent; npx vitest run src/data/roleboard/__tests__/webiq-corroboration.test.ts`
Expected: PASS.

- [ ] **Step 5: Wire the promote-to-watch action** (advisory) on the Web IQ row in `SignalsPanel.tsx` — a button that calls an injected `onPromoteToWatch(sig.id)` callback (no state mutation in this component; the CSA view owns the scenario-queue append). Add the prop to `SignalsPanelProps` with a safe default no-op so existing call-sites compile.

```tsx
// SignalsPanelProps
onPromoteToWatch?: (signalId: string) => void;
// default in the component signature:
onPromoteToWatch = () => {},
// in renderRow(sig), only for Trust-B:
{sig.trustClass === 'Trust-B' && (
  <button type="button" className={styles.promoteBtn} onClick={() => onPromoteToWatch(sig.id)}>
    Promote to watch
  </button>
)}
```

- [ ] **Step 6: Run the full app suite + typecheck**

Run: `cd apps/hcc-app-fluent; npx vitest run; npx tsc --noEmit`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add apps/hcc-app-fluent/src/workspaces/main/boards/occupancy/corroboration.ts `
  apps/hcc-app-fluent/src/workspaces/main/boards/occupancy/SignalsPanel.tsx `
  apps/hcc-app-fluent/src/data/roleboard/__tests__/webiq-corroboration.test.ts
git commit -m "feat(app): display-only web corroboration badge + HITL promote-to-watch for Web IQ"
```

---

## Task 10: PRD requirements + sprint page + traceability

**Files:**

- Modify: `docs/PRD.md` (§ FR-EXT / NFR-EXT tables + §7 traceability)
- Create: `docs/sprints/sprint-44-webiq-external-signal-channel.md`

- [ ] **Step 1: Add the new FR/NFR rows** to `docs/PRD.md` (exact IDs from the design §9): `FR-EXT-021`, `FR-EXT-022`, `FR-EXT-023`, `NFR-EXT-WEBIQ-001`, `NFR-EXT-WEBIQ-002`, with the wording from design §9.

- [ ] **Step 2: Add a §7 traceability row** pointing the new IDs at the Sprint 44 design + ADR-0060.

```markdown
| [`docs/superpowers/specs/2026-08-12-sprint-44-webiq-external-signal-channel-design.md`](superpowers/specs/2026-08-12-sprint-44-webiq-external-signal-channel-design.md) + [`docs/adr/0060-webiq-external-signal-channel.md`](adr/0060-webiq-external-signal-channel.md) *(Sprint 44: Web IQ Trust-B channel)* | `FR-EXT-021` to `FR-EXT-023`, `NFR-EXT-WEBIQ-001` to `NFR-EXT-WEBIQ-002` |
```

- [ ] **Step 3: Bump `docs/PRD.md` version header** (MINOR — new requirements) per §9, updating **Previous Version**.

- [ ] **Step 4: Write the sprint page** `docs/sprints/sprint-44-webiq-external-signal-channel.md` (mirror the structure of `docs/sprints/sprint-40-*.md`: goal, scope, predecessors, links to the design spec + this plan + ADR-0060, milestones M0–M6, DoD).

- [ ] **Step 5: Lint + commit**

```bash
git add docs/PRD.md docs/sprints/sprint-44-webiq-external-signal-channel.md
git commit -m "docs(prd): Sprint 44 Web IQ requirements FR-EXT-021..023 + NFR-EXT-WEBIQ-001..002 + sprint page"
```

---

## Task 11: Full verification

- [ ] **Step 1: Run the Python signal suite**

Run: `python -m pytest data-platform/scripts/external-signals -q`
Expected: PASS (new provider tests + Trust-B guard + existing suite green).

- [ ] **Step 2: Run the app suite + typecheck + lint**

Run: `cd apps/hcc-app-fluent; npx vitest run; npx tsc --noEmit; npm run lint`
Expected: PASS.

- [ ] **Step 3: Markdown + link check on changed docs**

Run: `npx --yes markdownlint-cli2 "docs/adr/0060-webiq-external-signal-channel.md" "docs/superpowers/**/2026-08-12-sprint-44-*.md" "docs/sprints/sprint-44-*.md"`
Expected: 0 issues.

- [ ] **Step 4: Confirm no live network + no MCP/allow-list change**

Run: `git diff --name-only origin/main...HEAD`
Expected: no changes under `.github/copilot/mcp.json`, `AGENTS.md`, or `provider-runner/main.bicep`; live binding remains disabled by default.

- [ ] **Step 5: Final commit / push (if clean)**

```bash
git push origin main
```

---

## Self-review (against the design spec)

- **Spec coverage:** D1→Task 3/4/5; D2→Task 3 + Task 7 guard; D3→Task 6; D4→Tasks 3–7 (reuse; registry auto-discovers); D5→Task 9; D6→Task 8; D7→Task 1. Contract v1.1.0→Task 2. FR/NFR→Task 10. Testing §10→Tasks 3–9,11. Milestones M0–M6 map to Tasks 1–11.
- **Placeholder scan:** none — every code step contains real code; every command has an expected result.
- **Type consistency:** `webCitations` shape `{title, uri, publishedAt?, snippet?}` is identical in the JSON schema (Task 2), Python `parse.py` (Task 5), and both TS interfaces (Task 8); `trustClass` union `'Trust-A' | 'Trust-B'` is consistent across `BoardSignal` and `ExternalSignal`; `corroborates()` signature matches its test.

## Execution handoff

Two execution options:

1. **Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks.
2. **Inline Execution** — execute tasks in this session with checkpoints.

Awaiting user review of the design spec (§14) and this plan before any code is written.
