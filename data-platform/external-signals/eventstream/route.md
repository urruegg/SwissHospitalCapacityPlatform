# External Signal Eventstream Route

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-22 |
| **Author** | Urs Rueegg |
| **Status** | Draft |
| **Previous Version** | n/a |

## Purpose

Route trusted external-signal events from the shared real-time ingress stream to
Eventhouse for hot-path TriggerRule evaluation and future Activator/Reflex
handoff. This route is authored for Sprint 21 M6 and remains configuration
only until the GA gate in ADR-0014 is satisfied.

## Route

| Setting | Value |
| ------- | ----- |
| Source Eventstream | `es-ihzhhpf-events` |
| Filter | `eventKind == "ext-signal"` |
| Destination | Eventhouse |
| Destination table | `ExternalSignal` |
| Contract | `DC-EXT-SIGNAL-v1` |
| Trigger path | Activator/Reflex rule in `../activator/reflex-rule.json` |

## Authoring notes

* Use the repository `eventstream-authoring` skill for Fabric Eventstream
  definition changes.
* Retrieve the current Eventstream definition with `getDefinition`, add a
  filter operator for `eventKind == "ext-signal"`, wire the filtered stream to
  the Eventhouse `ExternalSignal` table, then submit the topology using the
  Fabric `updateDefinition` REST action.
* Keep the scheduled poller workflow as the active bridge until Activator/Reflex
  is approved for the target environment.
* The route carries public-authority or synthetic signal records only. It must
  not contain PHI or patient-flow operational mutations.

## Validation

The route is validated as documentation/configuration in this milestone. Live
Fabric updates require a separate plan, environment evidence, and the ADR-0014
GA approval gate.
