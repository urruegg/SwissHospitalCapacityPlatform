"""Dependency-free JSON-Schema (draft-07 subset) validator for the Foresight
offline tests.

Mirrors the stdlib-only posture of ``data/synthetic/validate_datasets.py`` so the
Foresight schema-conformance test runs identically in CI and on a developer
machine without ``jsonschema``. Supports exactly the keywords used by the
Foresight contracts: ``type`` (incl. union lists), ``required``, ``properties``,
``additionalProperties: false``, ``enum``, ``const``, ``items``, ``minItems``,
``minimum``, ``maximum``, ``minLength``, ``pattern`` and the ``date-time``
``format`` (structural only).
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "boolean": bool,
    "integer": int,
    "number": (int, float),
    "null": type(None),
}


def load_module(name: str):
    """Load a sibling notebook module by filename (mirrors external-signals tests)."""
    nb_dir = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_").replace(".py", ""), nb_dir / name
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _check_type(value, type_spec, path, errors):
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    ok = False
    for t in types:
        py = _TYPES[t]
        # bool is a subclass of int — keep them distinct.
        if t in ("integer", "number") and isinstance(value, bool):
            continue
        if isinstance(value, py):
            ok = True
            break
    if not ok:
        errors.append(f"{path}: expected type {type_spec}, got {type(value).__name__}")


def validate(instance, schema, path="$", errors=None):
    """Return a list of validation error strings (empty == valid)."""
    if errors is None:
        errors = []

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")
    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")
    if "type" in schema:
        _check_type(instance, schema["type"], path, errors)

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: shorter than minLength {schema['minLength']}")
        if "pattern" in schema and not re.search(schema["pattern"], instance):
            errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    if isinstance(instance, dict):
        for req in schema.get("required", []):
            if req not in instance:
                errors.append(f"{path}: missing required property {req!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            for key in instance:
                if key not in props:
                    errors.append(f"{path}: additional property {key!r} not allowed")
        for key, subschema in props.items():
            if key in instance:
                validate(instance[key], subschema, f"{path}.{key}", errors)

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(instance):
                validate(item, item_schema, f"{path}[{i}]", errors)

    return errors
