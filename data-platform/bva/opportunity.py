"""Dependency-free helpers for BVA Opportunity v1 records."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCHEMA_PATH = REPO_ROOT / "data" / "synthetic" / "schema" / "bva-opportunity-v1.schema.json"
DEFAULT_DATASET_PATH = REPO_ROOT / "data" / "synthetic" / "bva" / "bva-opportunities.json"

_JSON_TYPES = {
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
    "array": list,
    "object": dict,
    "null": type(None),
}


def load_schema(path: str | Path | None = None) -> dict[str, Any]:
    """Load the frozen Opportunity v1 JSON schema."""
    schema_path = Path(path) if path is not None else DEFAULT_SCHEMA_PATH
    return json.loads(schema_path.read_text(encoding="utf-8"))


def load_dataset(path: str | Path | None = None) -> list[dict[str, Any]]:
    """Load the shared synthetic Opportunity dataset."""
    dataset_path = Path(path) if path is not None else DEFAULT_DATASET_PATH
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("opportunities"), list):
        return payload["opportunities"]
    raise ValueError(f"{dataset_path}: expected a list or object with opportunities list")


def slugify(name: str) -> str:
    """Return a deterministic lowercase ASCII slug for a hospital name."""
    ascii_name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_name.lower()).strip("-")
    return re.sub(r"-{2,}", "-", slug)


def make_opportunity_id(hospitalName: str) -> str:
    """Build the deterministic Opportunity id for the first ask from a hospital."""
    return f"opp-{slugify(hospitalName)}-0001"


def validate_opportunity(doc: dict[str, Any]) -> list[str]:
    """Validate an Opportunity document and return errors; empty means valid."""
    schema = load_schema()
    try:
        import jsonschema  # type: ignore[import-not-found]
    except ImportError:
        return _validate_fallback(doc, schema)

    validator = jsonschema.Draft7Validator(schema)
    errors: list[str] = []
    for error in sorted(validator.iter_errors(doc), key=lambda item: list(item.path)):
        path = "$" + "".join(f".{part}" if isinstance(part, str) else f"[{part}]" for part in error.path)
        errors.append(f"{path}: {error.message} ({error.validator})")
    return errors


def _type_ok(value: Any, expected: Any) -> bool:
    types = expected if isinstance(expected, list) else [expected]
    for schema_type in types:
        py_type = _JSON_TYPES.get(schema_type)
        if py_type is None:
            continue
        if schema_type in ("integer", "number") and isinstance(value, bool):
            continue
        if isinstance(value, py_type):
            return True
    return False


def _validate_fallback(instance: Any, schema: dict[str, Any], path: str = "$") -> list[str]:
    errors: list[str] = []

    if "type" in schema and not _type_ok(instance, schema["type"]):
        errors.append(f"{path}: expected type {schema['type']}, got {type(instance).__name__}")
        return errors

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")

    if isinstance(instance, str) and "minLength" in schema and len(instance) < schema["minLength"]:
        errors.append(f"{path}: string shorter than minLength {schema['minLength']}")

    if isinstance(instance, list):
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for index, item in enumerate(instance):
                errors.extend(_validate_fallback(item, item_schema, f"{path}[{index}]"))

    if isinstance(instance, dict):
        for required in schema.get("required", []):
            if required not in instance:
                errors.append(f"{path}: missing required property '{required}'")
        properties = schema.get("properties", {})
        for key, value in instance.items():
            if key in properties:
                errors.extend(_validate_fallback(value, properties[key], f"{path}.{key}"))
            elif schema.get("additionalProperties") is False:
                errors.append(f"{path}: additional property '{key}' not allowed")

    return errors


__all__ = [
    "load_dataset",
    "load_schema",
    "make_opportunity_id",
    "slugify",
    "validate_opportunity",
]
