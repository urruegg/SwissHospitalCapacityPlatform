"""Static SIT<->PROD Bicep parameter parity harness.

Guards the #255 Definition-of-Done item *"SIT + PROD deployed identically"* as a
**machine-checked, fully offline** gate (no Azure calls). It complements the
live ``deployed-parity-check`` job in ``ci-infra-validate.yml`` (which is
``workflow_dispatch``-only and compares *deployed resource types*) by catching
the earlier class of drift: a module-selection difference between
``infra/environments/sit.bicepparam`` and ``infra/environments/prod-swn.bicepparam``
that still *compiles* (so ``az bicep build-params`` passes) but is semantically
wrong -- e.g. a new ``enable*Module`` flag flipped on in SIT but forgotten in
PROD (the failure mode #381 skirted and that #419's
``enableSkillsEventSimJobModule`` could reintroduce).

Design
------
* The *effective* selection of every ``enable*Module`` parameter is compared,
  where effective = the value declared in the ``.bicepparam`` file, or -- when a
  file does not declare it -- the ``param ... bool = <default>`` in
  ``infra/main.bicep``. This makes "declared in one file, defaulted in the
  other" a first-class, correctly-resolved comparison.
* Every legitimate difference lives in :data:`ALLOWED_ASYMMETRIES`, the single
  source of truth for *what is allowed to differ*, each row sourced to an ADR or
  the SIT<->PROD parity matrix. Any **new** divergence fails the test until it is
  either fixed or added here with a documented reason.
* :func:`test_allowlist_has_no_stale_entries` keeps the allow-list honest: an
  allow-list row that is no longer actually divergent fails, so the list cannot
  rot.

No third-party dependencies -- stdlib + pytest only.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# --- repo-relative paths (this file lives at infra/tests/) ---
_INFRA_DIR = Path(__file__).resolve().parents[1]
_MAIN_BICEP = _INFRA_DIR / "main.bicep"
_SIT_PARAM = _INFRA_DIR / "environments" / "sit.bicepparam"
_PROD_PARAM = _INFRA_DIR / "environments" / "prod-swn.bicepparam"

# Deliberate, documented SIT<->PROD module-selection asymmetries. This is the
# ONLY place a difference is permitted; each row cites its authority. Keys are
# the ``enable*Module`` parameter name; ``sit`` / ``prod`` are the expected
# effective booleans.
ALLOWED_ASYMMETRIES: dict[str, dict[str, object]] = {
    "enableExperienceHostingModule": {
        "sit": True,
        "prod": False,
        "reason": (
            "Lean PROD (ADR-0037): the legacy App Service / experience-hosting "
            "topology is deliberately excluded from the switzerlandnorth "
            "greenfield rebuild; the live experience lane is reconciled "
            "separately. Parity matrix Level 5."
        ),
    },
    "enableApiRuntimeModule": {
        "sit": True,
        "prod": False,
        "reason": (
            "Lean PROD (ADR-0037): the legacy App Service / API topology is "
            "already live and is excluded from this data/AI/integration "
            "parity slice. Parity matrix Level 5."
        ),
    },
    "enableSignalRunnerModule": {
        "sit": False,
        "prod": True,
        "reason": (
            "PROD-exceeds-SIT hardening (ADR-0039): PROD codifies the "
            "external-signals provider-runner on a stable UAMI so the EH Data "
            "Sender role survives CAE recreate; SIT still uses a "
            "SystemAssigned identity. Parity matrix Level 3 (deliberate "
            "asymmetry, not a gap)."
        ),
    },
    "enableDecisionApplyJobModule": {
        "sit": True,
        "prod": False,
        "reason": (
            "SIT-only (Sprint 26 WS-C, #335): the decision-tier live-apply "
            "Container Apps Job is enabled in SIT for the demo path; the PROD "
            "extension is tracked separately outside Sprint 23. Off-by-default "
            "in main.bicep, so PROD carries no footprint."
        ),
    },
}

# Non-``Module`` enable flags and region/topology params are intentionally out
# of scope for this harness: PROD-only hardening such as
# ``enableKeyVaultPrivateEndpoint`` (ADR-0039) and region params are documented
# in the SIT<->PROD parity matrix, not asserted here.

_FLAG_RE = re.compile(r"^\s*param\s+(enable\w*Module)\s*=\s*(true|false)\s*$")
_DEFAULT_RE = re.compile(r"param\s+(enable\w*Module)\s+bool\s*=\s*(true|false)")


def _parse_declared(path: Path) -> dict[str, bool]:
    """Return the ``enable*Module`` flags explicitly declared in a bicepparam."""
    out: dict[str, bool] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _FLAG_RE.match(line)
        if m:
            out[m.group(1)] = m.group(2) == "true"
    return out


def _parse_defaults(path: Path) -> dict[str, bool]:
    """Return the ``enable*Module`` param defaults from main.bicep."""
    txt = path.read_text(encoding="utf-8")
    return {m.group(1): m.group(2) == "true" for m in _DEFAULT_RE.finditer(txt)}


def _effective(declared: dict[str, bool], defaults: dict[str, bool]) -> dict[str, bool]:
    """Resolve effective selection: declared value else main.bicep default."""
    return {name: declared.get(name, default) for name, default in defaults.items()}


def _divergences() -> dict[str, tuple[bool, bool]]:
    """Map of ``enable*Module`` -> (sit_effective, prod_effective) where they differ."""
    defaults = _parse_defaults(_MAIN_BICEP)
    sit = _effective(_parse_declared(_SIT_PARAM), defaults)
    prod = _effective(_parse_declared(_PROD_PARAM), defaults)
    return {name: (sit[name], prod[name]) for name in defaults if sit[name] != prod[name]}


# Skills lane modules that Sprint 23 (#255) requires to be selected identically
# in SIT and PROD (the org/skills medallion landing surface, ADR-0039).
_SKILLS_LANE_MODULES = (
    "enableMasterdataLandingModule",
    "enableSkillsSimJobsModule",
    "enableSkillsEventstreamModule",
    "enableSkillsEventSimJobModule",
)


def test_bicepparam_files_exist() -> None:
    assert _MAIN_BICEP.is_file(), _MAIN_BICEP
    assert _SIT_PARAM.is_file(), _SIT_PARAM
    assert _PROD_PARAM.is_file(), _PROD_PARAM


def test_no_undocumented_module_divergence() -> None:
    """Every SIT<->PROD ``enable*Module`` difference must be allow-listed."""
    divergences = _divergences()
    undocumented = {
        name: pair for name, pair in divergences.items() if name not in ALLOWED_ASYMMETRIES
    }
    assert not undocumented, (
        "Undocumented SIT<->PROD module-selection drift (add to "
        "ALLOWED_ASYMMETRIES with an ADR/parity-matrix reason, or fix the "
        f"bicepparam): {undocumented} (sit, prod)"
    )


@pytest.mark.parametrize("flag", sorted(ALLOWED_ASYMMETRIES))
def test_allowlisted_asymmetry_matches_declared_values(flag: str) -> None:
    """Each allow-list row must state the *actual* current effective values."""
    divergences = _divergences()
    assert flag in divergences, (
        f"Allow-list entry {flag!r} is not actually divergent any more "
        "(stale row -- remove it from ALLOWED_ASYMMETRIES)."
    )
    sit_eff, prod_eff = divergences[flag]
    row = ALLOWED_ASYMMETRIES[flag]
    assert (row["sit"], row["prod"]) == (sit_eff, prod_eff), (
        f"Allow-list values for {flag!r} are stale: documented "
        f"(sit={row['sit']}, prod={row['prod']}) but actual "
        f"(sit={sit_eff}, prod={prod_eff}). Update ALLOWED_ASYMMETRIES."
    )
    assert isinstance(row.get("reason"), str) and row["reason"].strip(), (
        f"Allow-list entry {flag!r} must carry a non-empty reason."
    )


def test_allowlist_has_no_stale_entries() -> None:
    """Allow-list must not carry entries that are no longer divergent."""
    divergences = _divergences()
    stale = sorted(set(ALLOWED_ASYMMETRIES) - set(divergences))
    assert not stale, (
        f"Stale allow-list entries (no longer divergent, remove them): {stale}"
    )


def test_skills_lane_modules_are_parity() -> None:
    """The Sprint 23 org/skills medallion modules must match effectively."""
    divergent_skills = [m for m in _SKILLS_LANE_MODULES if m in _divergences()]
    assert not divergent_skills, (
        "Sprint 23 skills-lane modules must be selected identically in SIT and "
        f"PROD, but these diverge: {divergent_skills}. If a difference is "
        "intentional, add it to ALLOWED_ASYMMETRIES with a documented reason."
    )


def test_skills_eventstream_source_mode_is_deliberately_asymmetric() -> None:
    """SIT uses CustomEndpoint, PROD uses EventHub -- deliberate (ADR-0043)."""
    src_re = re.compile(
        r"^\s*param\s+skillsEventstreamSourceMode\s*=\s*'([^']+)'\s*$", re.MULTILINE
    )
    sit_m = src_re.search(_SIT_PARAM.read_text(encoding="utf-8"))
    prod_m = src_re.search(_PROD_PARAM.read_text(encoding="utf-8"))
    assert sit_m and prod_m, "skillsEventstreamSourceMode must be declared in both env files"
    assert sit_m.group(1) == "CustomEndpoint", (
        "SIT skills-events lane must stay on the live-deployable CustomEndpoint "
        f"source (demo scope, ADR-0013/ADR-0043); got {sit_m.group(1)!r}."
    )
    assert prod_m.group(1) == "EventHub", (
        "PROD skills-events lane targets the dedicated EventHub source "
        f"(ADR-0043; live bind GA-deferred); got {prod_m.group(1)!r}."
    )
