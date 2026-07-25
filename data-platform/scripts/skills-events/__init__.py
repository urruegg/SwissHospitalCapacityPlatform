"""Skills-events package (Sprint 23 WS-A4 / design D4).

The near-real-time skills-events lane: a dependency-free event seeder + normalize
helpers for the three ``DC-SKILL-EVENT-v1`` event kinds (credential-expiry,
consent-grant-or-revoke, newly-confirmed-assertion) that the WS-A4 Eventstream
lane carries. Mirrors ``external-signals`` / ``skills-evidence``.

Synthetic / no-PHI only (ADR-0013 / ADR-0016).
"""
