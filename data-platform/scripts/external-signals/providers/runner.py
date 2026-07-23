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
