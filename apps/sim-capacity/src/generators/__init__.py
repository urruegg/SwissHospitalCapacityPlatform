"""Event generator subpackage for the sim-capacity simulator.

Each generator emits an iterator of envelopes for one ``eventKind`` (design
spec §4.3). Generators share the envelope helper in
:mod:`sim_capacity.envelope` and are seeded through their inputs so the same
seed reproduces the same event stream.
"""
