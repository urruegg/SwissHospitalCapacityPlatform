"""Unit tests for the Sprint 11 manifest loader (T5)."""

from __future__ import annotations

from pathlib import Path

import pytest

from manifests.loader import (
    ManifestError,
    load_agent_host_manifests,
    parse_manifest,
)


def _base_manifest() -> dict:
    return {
        "agent": "demo-agent",
        "version": "1.0.0",
        "runtime": "agent-host",
        "modelDeploymentRef": "sprint11-chat",
        "systemPromptRef": "./AGENT.md",
        "mcpTools": [
            {"server": "fabric-mcp", "tools": ["query"], "ceiling": "read"},
            {"server": "github-mcp", "tools": ["add-issue-comment"], "ceiling": "write"},
        ],
        "hitl": {"gates": ["HITL-02"]},
        "grounding": [{"table": "gold.bed_assignment", "scope": "hospital"}],
    }


def test_parse_manifest_projects_fields():
    manifest = parse_manifest(_base_manifest(), Path("demo/manifest.yaml"))
    assert manifest.agent == "demo-agent"
    assert manifest.runtime == "agent-host"
    assert manifest.hitl_gates == ("HITL-02",)
    assert manifest.grounding_tables == ("gold.bed_assignment",)
    assert manifest.max_ceiling == "write"


def test_missing_required_field_raises():
    data = _base_manifest()
    del data["modelDeploymentRef"]
    with pytest.raises(ManifestError):
        parse_manifest(data, Path("demo/manifest.yaml"))


def test_invalid_ceiling_raises():
    data = _base_manifest()
    data["mcpTools"][0]["ceiling"] = "superuser"
    with pytest.raises(ManifestError):
        parse_manifest(data, Path("demo/manifest.yaml"))


def test_unknown_hitl_gate_raises():
    data = _base_manifest()
    data["hitl"]["gates"] = ["HITL-99"]
    with pytest.raises(ManifestError):
        parse_manifest(data, Path("demo/manifest.yaml"))


def test_loads_real_bmca_manifest_from_repo():
    repo_root = Path(__file__).resolve().parents[4]
    manifests = load_agent_host_manifests(repo_root / "agents")
    assert "bmca-agent" in manifests
    bmca = manifests["bmca-agent"]
    assert bmca.runtime == "agent-host"
    assert "gold.bed_assignment" in bmca.grounding_tables
    assert bmca.hitl_gates == ("HITL-02",)
    # The Fabric IQ-hosted fabric-data-agent must never be loaded by this host.
    assert "fabric-data-agent" not in manifests
