"""Sprint 13 T5 — Sprint 11 agent manifest loader.

Reads every ``agents/<name>/manifest.yaml`` at startup and validates it against a
minimal schema so the agent-host knows which agents it can dispatch, which MCP
tools each may call, and which HITL gates govern their side effects.

The manifests are the runtime contract (AGENTS.md §1). Only ``runtime:
agent-host`` manifests are loaded by this host; ``fabric-data-agent`` (Fabric
IQ-hosted) and control-plane packs without a manifest are skipped.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

# The side-effect ceilings recognised by the host, ordered least → most powerful.
CEILINGS = ("read", "write", "deploy", "delete")

# The mandatory HITL gates per ADR-0007 §3.
VALID_HITL_GATES = {"HITL-01", "HITL-02", "HITL-03", "HITL-04", "HITL-05"}


class ManifestError(ValueError):
    """Raised when a manifest is missing required fields or is malformed."""


@dataclass(frozen=True)
class ToolBinding:
    server: str
    tools: tuple[str, ...]
    ceiling: str


@dataclass(frozen=True)
class GroundingAgentBinding:
    server: str
    endpoint_env: str
    workspace_env: str
    precedence: str = "primary"


@dataclass(frozen=True)
class AgentManifest:
    agent: str
    version: str
    runtime: str
    model_deployment_ref: str
    system_prompt_ref: str
    tools: tuple[ToolBinding, ...] = ()
    hitl_gates: tuple[str, ...] = ()
    grounding_tables: tuple[str, ...] = field(default=())
    grounding_agent: "GroundingAgentBinding | None" = None

    @property
    def max_ceiling(self) -> str:
        """The highest ceiling any bound tool may reach."""
        if not self.tools:
            return "read"
        return max((t.ceiling for t in self.tools), key=CEILINGS.index)


def _require(data: dict[str, Any], key: str, source: Path) -> Any:
    if key not in data or data[key] in (None, ""):
        raise ManifestError(f"{source}: missing required field '{key}'")
    return data[key]


def parse_manifest(data: dict[str, Any], source: Path) -> AgentManifest:
    """Validate a parsed manifest mapping and build an :class:`AgentManifest`."""
    agent = _require(data, "agent", source)
    runtime = _require(data, "runtime", source)

    tools: list[ToolBinding] = []
    for raw in data.get("mcpTools", []) or []:
        ceiling = raw.get("ceiling", "read")
        if ceiling not in CEILINGS:
            raise ManifestError(
                f"{source}: tool ceiling '{ceiling}' is not one of {CEILINGS}"
            )
        tools.append(
            ToolBinding(
                server=_require(raw, "server", source),
                tools=tuple(raw.get("tools", []) or []),
                ceiling=ceiling,
            )
        )

    gates = tuple(((data.get("hitl") or {}).get("gates", []) or []))
    for gate in gates:
        if gate not in VALID_HITL_GATES:
            raise ManifestError(f"{source}: unknown HITL gate '{gate}'")

    grounding = tuple(
        row["table"]
        for row in (data.get("grounding") or [])
        if isinstance(row, dict) and row.get("table")
    )

    grounding_agent = None
    raw_ga = data.get("groundingAgent")
    if raw_ga:
        precedence = raw_ga.get("precedence", "primary")
        if precedence not in ("primary", "secondary"):
            raise ManifestError(
                f"{source}: groundingAgent precedence '{precedence}' must be 'primary' or 'secondary'"
            )
        grounding_agent = GroundingAgentBinding(
            server=_require(raw_ga, "server", source),
            endpoint_env=_require(raw_ga, "endpointEnv", source),
            workspace_env=_require(raw_ga, "workspaceEnv", source),
            precedence=precedence,
        )

    return AgentManifest(
        agent=agent,
        version=str(_require(data, "version", source)),
        runtime=runtime,
        model_deployment_ref=_require(data, "modelDeploymentRef", source),
        system_prompt_ref=_require(data, "systemPromptRef", source),
        tools=tuple(tools),
        hitl_gates=gates,
        grounding_tables=grounding,
        grounding_agent=grounding_agent,
    )


def load_manifest_file(path: Path) -> AgentManifest:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ManifestError(f"{path}: manifest is not a mapping")
    return parse_manifest(data, path)


def load_agent_host_manifests(agents_root: Path) -> dict[str, AgentManifest]:
    """Load all ``runtime: agent-host`` manifests under ``agents_root``.

    Manifests with a different runtime (e.g. Fabric IQ) are skipped so the host
    only exposes the agents it can actually dispatch.
    """
    manifests: dict[str, AgentManifest] = {}
    for manifest_path in sorted(agents_root.glob("*/manifest.yaml")):
        manifest = load_manifest_file(manifest_path)
        if manifest.runtime != "agent-host":
            continue
        manifests[manifest.agent] = manifest
    return manifests
