"""Skills-evidence plugin package (Sprint 23 WS-B).

Mirrors data-platform/scripts/external-signals: per-source connectors normalize
external skills evidence into the DC-SKILL-EVIDENCE-v1 contract. All sources are
simulated now; each adapter is shaped so a real API can slot in later
(source_mode: live) without touching the ontology. Synthetic / no-PHI only.
"""
