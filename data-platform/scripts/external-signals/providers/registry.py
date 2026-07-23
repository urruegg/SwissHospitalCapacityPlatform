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
