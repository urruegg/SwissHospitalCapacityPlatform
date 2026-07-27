# Signal Agent (SGA) Implementation Plan — Sprint 32

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stand up a new `signal-agent` that owns the channel-intake lifecycle and proves one certification-register → skills-baseline onboarding end-to-end (on a curated sample feed), demand-driven by the Sprint 31 `DC-DQ-GAP-v1` seam.

**Architecture:** A new agent pack (`agents/signal-agent/`) + one new staff-PII contract + three pure deterministic Python modules under `data-platform/signals/` (gap-register generator, credential→competency resolver + skills enrichment, channel-readiness scorecard) + ontology additions. Advisory + HITL + GA-only; staff-PII handled per nDSG (pseudonymised work-IDs).

**Tech Stack:** Python 3.11, pytest, JSON Schema (draft-07), the `dc-*-v1.schema.json` convention, the two-layer ontology + crosswalk CI (`NFR-ONT-001`).

**Prerequisite (hard):** Sprint 31 merged — the `DC-DQ-GAP-v1` seam (`data/synthetic/schema/dc-dq-gap-v1.schema.json`) exists on `main`. SGA's intake consumes a `newSourceNeeded: true` gap.

**Scope:** Sprint 32 SGA MVP slice (closes #454; tracker #452). Design: [`docs/superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md`](../specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md).

**Tests:** `python -m pytest data-platform/signals/tests -q`.

---

## File structure

| File | Responsibility |
|------|----------------|
| `data/synthetic/schema/dc-ref-certification-v1.schema.json` *(create)* | Credential↔competency contract (staff-PII, pseudonymised). |
| `data/synthetic/schema/certification-sample-feed.json` *(create)* | Curated, synthetic sample credential feed (no real staff-PII). |
| `data-platform/signals/__init__.py` *(create)* | Package marker. |
| `data-platform/signals/gap_register.py` *(create)* | Pure `build_gap_register()` (referenced-vs-wired scan → ranked register). |
| `data-platform/signals/credential_resolver.py` *(create)* | Pure `resolve_competencies()` + `enrich_skill_tags()` (pseudonymised work-ID). |
| `data-platform/signals/channel_scorecard.py` *(create)* | Pure `score_channel()` → Channel Readiness Scorecard. |
| `data-platform/signals/tests/*.py` *(create)* | Unit tests for the three modules. |
| `agents/signal-agent/AGENT.md` *(create)* | New agent pack — Identity, Scope, Tools, Refusal Rules, Output Contract, Confirmation Rules. |
| `agents/signal-agent/manifest.yaml` *(create)* | Runtime manifest. |
| `agents/signal-agent/golden-tasks.md` *(create)* | ≥1 happy-path + ≥1 failure-mode fixture. |
| `docs/ontology/*` *(modify)* | Credential/Competency/Qualification/IssuingAuthority + crosswalk. |
| `docs/adr/00NN-signal-channel-lifecycle.md` *(create)* | Signal-channel-lifecycle governance ADR. |
| `AGENTS.md`, `docs/PRD.md`, `docs/DATA.md` *(modify)* | Registry row; `FR-SIG-*`; contract registration. |

---

## Task 1: `DC-REF-CERTIFICATION-v1` contract + curated sample feed

**Files:**
- Create: `data/synthetic/schema/dc-ref-certification-v1.schema.json`
- Create: `data/synthetic/schema/certification-sample-feed.json`

- [ ] **Step 1: Write the schema** (staff-PII; pseudonymised work-ID; no direct identifiers)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://curavias/schema/dc-ref-certification-v1.schema.json",
  "title": "DC-REF-CERTIFICATION-v1",
  "type": "object",
  "required": ["contractId", "workId", "issuer", "credentialType", "competencyCodes", "verificationStatus", "_classification"],
  "additionalProperties": false,
  "properties": {
    "contractId": { "const": "DC-REF-CERTIFICATION-v1" },
    "workId": { "type": "string", "pattern": "^WID-[0-9a-f]{8,}$", "description": "pseudonymised staff work-ID; never a name/AHV" },
    "issuer": { "type": "string" },
    "credentialType": { "type": "string" },
    "competencyCodes": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
    "validFrom": { "type": "string", "format": "date" },
    "validUntil": { "type": ["string", "null"], "format": "date" },
    "verificationStatus": { "type": "string", "enum": ["verified", "self-attested", "expired", "revoked"] },
    "_classification": { "const": "staff-PII" },
    "_residency": { "type": "string" },
    "_provenance": { "type": "object" }
  }
}
```

- [ ] **Step 2: Write a small curated synthetic sample feed** — 3–4 records using `WID-*` pseudonymous ids only (no names, no AHV), e.g. an ICU nursing cert and an FMH anaesthesia title mapping to competency codes. This is the demo input; it contains **no** real staff-PII (ADR-0016).

- [ ] **Step 3: Commit**

```bash
git add data/synthetic/schema/dc-ref-certification-v1.schema.json data/synthetic/schema/certification-sample-feed.json
git commit -m "feat(sga): DC-REF-CERTIFICATION-v1 contract + curated synthetic sample feed"
```

---

## Task 2: Credential→competency resolver + skills enrichment

**Files:**
- Create: `data-platform/signals/__init__.py`, `data-platform/signals/credential_resolver.py`
- Test: `data-platform/signals/tests/test_credential_resolver.py`

- [ ] **Step 1: Write the failing test**

```python
"""Sprint 32 SGA — credential→competency resolver + skills enrichment."""
from __future__ import annotations

import pytest

from signals.credential_resolver import resolve_competencies, enrich_skill_tags

TAXONOMY = {
    "ICU-Nursing-Cert": ["comp.icu.core", "comp.ventilation"],
    "FMH-Anaesthesia": ["comp.anaesthesia", "comp.airway"],
}


def test_resolve_known_credential():
    assert resolve_competencies("ICU-Nursing-Cert", TAXONOMY) == ["comp.icu.core", "comp.ventilation"]


def test_resolve_unknown_credential_is_empty():
    assert resolve_competencies("Unknown-Cert", TAXONOMY) == []


def test_enrich_skill_tags_by_workid_is_pseudonymous_and_deduped():
    pool = {"WID-abcdef01": ["comp.icu.core"]}
    creds = [
        {"workId": "WID-abcdef01", "credentialType": "ICU-Nursing-Cert"},
        {"workId": "WID-99887766", "credentialType": "FMH-Anaesthesia"},
    ]
    out = enrich_skill_tags(pool, creds, TAXONOMY)
    assert set(out["WID-abcdef01"]) == {"comp.icu.core", "comp.ventilation"}   # merged, deduped
    assert set(out["WID-99887766"]) == {"comp.anaesthesia", "comp.airway"}
    # keys are pseudonymous work-IDs only
    assert all(k.startswith("WID-") for k in out)


def test_enrich_rejects_non_pseudonymous_key():
    with pytest.raises(ValueError):
        enrich_skill_tags({}, [{"workId": "Anna Meier", "credentialType": "ICU-Nursing-Cert"}], TAXONOMY)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/signals/tests/test_credential_resolver.py -q`
Expected: FAIL — module not found. *(Set the import path the same way the Sprint 31 `data-platform/quality` tests did — a `conftest.py` inserting the package parent, importing as `from signals.credential_resolver import ...`.)*

- [ ] **Step 3: Write the implementation**

```python
"""Sprint 32 SGA — deterministic credential→competency resolution + skills enrichment.

Staff-PII safe: operates only on pseudonymised work-IDs (WID-*), never names/AHV
(nDSG; ADR-0016). NO randomness.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

_WID = re.compile(r"^WID-[0-9a-f]{8,}$")


def resolve_competencies(credential_type: str, taxonomy: Dict[str, List[str]]) -> List[str]:
    """Map a credential type to its competency codes (empty if unknown)."""
    return list(taxonomy.get(credential_type, []))


def enrich_skill_tags(
    pool: Dict[str, List[str]],
    credentials: List[Dict[str, Any]],
    taxonomy: Dict[str, List[str]],
) -> Dict[str, List[str]]:
    """Merge resolved competencies into the skills baseline, keyed by pseudonymised work-ID."""
    out: Dict[str, List[str]] = {k: list(v) for k, v in pool.items()}
    for cred in credentials:
        wid = cred.get("workId", "")
        if not _WID.match(wid):
            raise ValueError(f"workId must be a pseudonymised WID-*, got {wid!r}")
        merged = set(out.get(wid, [])) | set(resolve_competencies(cred.get("credentialType", ""), taxonomy))
        out[wid] = sorted(merged)
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/signals/tests/test_credential_resolver.py -q`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add data-platform/signals/__init__.py data-platform/signals/credential_resolver.py data-platform/signals/tests/
git commit -m "feat(sga): credential->competency resolver + pseudonymous skills enrichment"
```

---

## Task 3: Signal Gap Register generator

**Files:**
- Create: `data-platform/signals/gap_register.py`
- Test: `data-platform/signals/tests/test_gap_register.py`

- [ ] **Step 1: Write the failing test**

```python
"""Sprint 32 SGA — Signal Gap Register tests."""
from __future__ import annotations

from signals.gap_register import build_gap_register


def test_ranks_referenced_but_unwired_and_dq_gaps_first():
    referenced = {"certification-register", "or-anaesthesia-status", "rostering-feed"}
    wired = {"rostering-feed"}
    dq_gaps = [{"domain": "staffing.skills", "recommendedSource": {"kind": "certification-register"}, "impactScore": 0.42, "newSourceNeeded": True}]
    reg = build_gap_register(referenced, wired, dq_gaps)
    kinds = [r["signal"] for r in reg]
    # DQ-demanded certification-register ranks first (has an impact score); unwired next
    assert kinds[0] == "certification-register"
    assert "or-anaesthesia-status" in kinds
    assert "rostering-feed" not in kinds  # already wired
    assert reg[0]["demandedByDq"] is True
    assert all(0.0 <= r["rank"] for r in reg)


def test_empty_when_all_wired_and_no_dq_gap():
    assert build_gap_register({"a"}, {"a"}, []) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/signals/tests/test_gap_register.py -q`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

```python
"""Sprint 32 SGA — deterministic Signal Gap Register (design §7, FR-SIG-001).

Referenced-but-unwired channels + DQ-demanded new sources, ranked. DQ-demanded
gaps rank first (they carry a measured impact score). NO randomness.
"""
from __future__ import annotations

from typing import Any, Dict, List, Set


def build_gap_register(
    referenced: Set[str],
    wired: Set[str],
    dq_gaps: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return a ranked list of signal gaps (highest rank first)."""
    dq_by_kind = {
        g["recommendedSource"]["kind"]: g
        for g in dq_gaps
        if g.get("newSourceNeeded") and g.get("recommendedSource", {}).get("kind")
    }
    rows: List[Dict[str, Any]] = []
    for signal in sorted((referenced - wired) | set(dq_by_kind)):
        g = dq_by_kind.get(signal)
        rows.append({
            "signal": signal,
            "demandedByDq": g is not None,
            # rank: DQ impact (0..1) + 0.5 base for referenced-but-unwired
            "rank": round((g["impactScore"] if g else 0.0) + (0.5 if signal in referenced else 0.0), 4),
        })
    return sorted(rows, key=lambda r: (-r["rank"], r["signal"]))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/signals/tests/test_gap_register.py -q`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add data-platform/signals/gap_register.py data-platform/signals/tests/test_gap_register.py
git commit -m "feat(sga): deterministic Signal Gap Register generator"
```

---

## Task 4: Channel Readiness Scorecard

**Files:**
- Create: `data-platform/signals/channel_scorecard.py`
- Test: `data-platform/signals/tests/test_channel_scorecard.py`

- [ ] **Step 1: Write the failing test**

```python
"""Sprint 32 SGA — Channel Readiness Scorecard tests."""
from __future__ import annotations

from signals.channel_scorecard import score_channel

REQUIRED = ["workId", "issuer", "credentialType", "competencyCodes"]


def test_ready_when_all_checks_pass():
    sample = [{"workId": "WID-abcdef01", "issuer": "NAREG", "credentialType": "ICU-Nursing-Cert",
               "competencyCodes": ["comp.icu.core"], "_provenance": {"sourceAuthority": "NAREG"}}]
    card = score_channel(sample, required_fields=REQUIRED)
    assert card["ready"] is True
    assert card["checks"]["schemaConformant"] is True
    assert card["checks"]["provenanceComplete"] is True
    assert card["checks"]["dedupOk"] is True


def test_not_ready_on_missing_field_or_provenance():
    sample = [{"workId": "WID-abcdef01", "issuer": "NAREG", "credentialType": "ICU"}]  # missing competencyCodes + provenance
    card = score_channel(sample, required_fields=REQUIRED)
    assert card["ready"] is False
    assert card["checks"]["schemaConformant"] is False
    assert card["checks"]["provenanceComplete"] is False


def test_dedup_detects_duplicate_workid_credential():
    row = {"workId": "WID-abcdef01", "issuer": "N", "credentialType": "ICU",
           "competencyCodes": ["c"], "_provenance": {"sourceAuthority": "N"}}
    card = score_channel([row, dict(row)], required_fields=REQUIRED)
    assert card["checks"]["dedupOk"] is False
    assert card["ready"] is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest data-platform/signals/tests/test_channel_scorecard.py -q`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the implementation**

```python
"""Sprint 32 SGA — deterministic Channel Readiness Scorecard (design §7, FR-SIG-007).

Sandbox gate before activation: schema conformance, provenance completeness,
dedup. NO network I/O in the scorer — operates on an already-fetched sample.
"""
from __future__ import annotations

from typing import Any, Dict, List


def score_channel(sample: List[Dict[str, Any]], required_fields: List[str]) -> Dict[str, Any]:
    """Return a Channel Readiness Scorecard for a fetched sample."""
    schema_ok = bool(sample) and all(all(f in row and row[f] not in (None, "", []) for f in required_fields) for row in sample)
    provenance_ok = bool(sample) and all(row.get("_provenance", {}).get("sourceAuthority") for row in sample)
    keys = [(row.get("workId"), row.get("credentialType")) for row in sample]
    dedup_ok = len(keys) == len(set(keys))
    ready = schema_ok and provenance_ok and dedup_ok
    return {
        "ready": ready,
        "checks": {"schemaConformant": schema_ok, "provenanceComplete": provenance_ok, "dedupOk": dedup_ok},
        "sampleSize": len(sample),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest data-platform/signals/tests -q`
Expected: PASS (all signals tests green).

- [ ] **Step 5: Commit**

```bash
git add data-platform/signals/channel_scorecard.py data-platform/signals/tests/test_channel_scorecard.py
git commit -m "feat(sga): deterministic Channel Readiness Scorecard"
```

---

## Task 5: New `signal-agent` pack

**Files:**
- Create: `agents/signal-agent/AGENT.md`, `agents/signal-agent/manifest.yaml`, `agents/signal-agent/golden-tasks.md`

- [ ] **Step 1: Author `AGENT.md`** — follow the fixed structure used by `agents/signal-triage-agent/AGENT.md`: **Identity** (channel-intake lifecycle meta-agent, sibling to signal-triage-agent), **Scope** (in: discover/classify/adapter/contract/ontology-bind/sandbox-test/HITL-activate/monitor; out: acting on signals, autonomous activation), **Tools** (`github-mcp` write; `fabric-mcp` read), **Refusal Rules** (inherit AGENTS.md §5; + no channel activation without data-owner+compliance approval; + staff-PII never as non-PHI; + web results untrusted), **Output Contract**, **Confirmation Rules** (`approved-to-apply` on activation). Version header per §9. Cite `DC-REF-CERTIFICATION-v1`, the three `data-platform/signals/` modules, and the `DC-DQ-GAP-v1` seam it consumes.

- [ ] **Step 2: Author `manifest.yaml`** — mirror `agents/signal-triage-agent/manifest.yaml` shape (agent, version, runtime, model_deployment_ref, system_prompt_ref, tools, hitl_gates, grounding). Ceiling `write`; `fabric-mcp` read-only.

- [ ] **Step 3: Author `golden-tasks.md`** — ≥1 happy path (consume a `DC-DQ-GAP-v1` `newSourceNeeded` gap → propose intake → onboard the curated certification feed → scorecard passes → HITL approve → skills baseline enriched by WID) and ≥2 failure-mode refusals (activate without approval; treat staff-PII as non-PHI). Front-matter `requirement:` keys reference the `FR-SIG-*` IDs.

- [ ] **Step 4: Commit**

```bash
git add agents/signal-agent/
git commit -m "feat(sga): new signal-agent pack (lifecycle, HITL, provenance, refusals)"
```

---

## Task 6: Ontology additions + crosswalk

**Files:**
- Modify: `docs/ontology/*` (the reference↔operational crosswalk source)

- [ ] **Step 1: Add the classes + relations** — `Certification`, `Qualification`, `Credential` (IAO information content entities), `Competency`/`SkillTag` (quality), `IssuingAuthority` (organisation with an authority role); relations *HealthWorker `holds` Credential; Credential `certifies` Competency; Competency `qualifies_for` CapacityUnit/Task*. Register the reference↔operational crosswalk entries so the CI conformance check (`NFR-ONT-001`) stays green.

- [ ] **Step 2: Run the ontology crosswalk CI check locally** (the command documented in `docs/ontology/` / `scripts/ontology/`). Expected: green.

- [ ] **Step 3: Commit**

```bash
git add docs/ontology/
git commit -m "feat(sga): ontology Credential/Competency/Qualification/IssuingAuthority + crosswalk"
```

---

## Task 7: ADR + PRD + DATA + AGENTS registry

**Files:**
- Create: `docs/adr/00NN-signal-channel-lifecycle.md`
- Modify: `docs/PRD.md`, `docs/DATA.md`, `AGENTS.md`

- [ ] **Step 1: Write the ADR** — signal-channel lifecycle governance (discover→…→retire; trust tiers; adapter catalogue; HITL approval RACI; staff-PII handling). Status `Proposed`; next free ADR number.

- [ ] **Step 2: `docs/PRD.md` §7** — add `FR-SIG-*` / `NFR-SIG-*` headline rows (design §13); bump PRD version.

- [ ] **Step 3: `docs/DATA.md`** — register `DC-REF-CERTIFICATION-v1` (staff-PII); bump version.

- [ ] **Step 4: `AGENTS.md`** — add a registry row for `signal-agent` (owner, trigger, MCP servers `github-mcp`+`fabric-mcp`, side-effect ceiling `write`, prompt + golden-tasks paths); bump AGENTS.md version. *(Governance file — requires the human-authored issue #454 + CODEOWNERS review per AGENTS.md §5; this task is that change.)*

- [ ] **Step 5: Doc gates** (repo root): `python scripts/lint/check_mojibake.py <edited docs>` + `npx --yes markdownlint-cli2 "<edited docs>"`. Expected: clean.

- [ ] **Step 6: Commit**

```bash
git add docs/adr/00NN-signal-channel-lifecycle.md docs/PRD.md docs/DATA.md AGENTS.md
git commit -m "docs(sga): signal-channel-lifecycle ADR + FR-SIG-* + contract + AGENTS registry row"
```

---

## Final verification

- [ ] `python -m pytest data-platform/signals/tests -q` — all green.
- [ ] End-to-end on the curated sample feed: gap register lists the certification-register (demanded by a `DC-DQ-GAP-v1`); scorecard passes; resolver enriches skills by `WID-*` only; ontology crosswalk CI green.
- [ ] No real staff-PII / PHI anywhere; every record `_classification: staff-PII`, pseudonymised.
- [ ] Doc gates green; `AGENTS.md` registry row + golden tasks present.

---

## Self-review checklist (run before opening the PR)

- Spec coverage: S0=T1, S3=T2, S2=T3, S5=T4, S1=T5, S4=T6, S6=T7 — all design §11 Sprint-32 milestones mapped.
- No placeholders except the flagged ADR-number + import-path + ontology-CI-command lookups (genuine environment lookups).
- Type consistency: `resolve_competencies` / `enrich_skill_tags` / `build_gap_register` / `score_channel` signatures match their tests; contract keys match the JSON Schema; `DC-DQ-GAP-v1` shape consumed matches the Sprint 31 frozen seam.
