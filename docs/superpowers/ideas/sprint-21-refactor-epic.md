# Sprint 21 Refactor Epic

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rueegg |
| **Status** | Draft (idea capture) |
| **Previous Version** | n/a (initial idea capture) |
| **Sprint** | [Sprint 21 - Trusted External Signals](../../sprints/SPRINT_PLAN.md) |
| **Issue** | [#247](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/247) |

> Sprint 21 - Trusted External Signals: Fabric ingestion, ontology, semantic
> model & event triggering. Issue #247, urruegg/SwissHospitalCapacityPlatform.

We need to extend the scope of the sprint 21 and align it with the new
requirements we got as follows:

1. User Experience CSA and OCA show the signals by channel, they want to have an
   indicator batch for each channel to show if the channel is connected to real
   data source or to simulated data source (live versus simulated) to trust the
   signals.
2. Signals Data Provider needs to adapt a design pattern to enable onboarding new
   signal sources as new signal provider plugins to gather the signal data in a
   standard format to be streamed into the data platform ontology model to
   support the Foundry IQ and Fabric IQ layer. Also support internal signal
   channels to complete the full picture.
3. Establish for all known signal channels where we have an API an adapter to
   stream the real signals.
4. Establish for all signals where we don't have a real API a Simulator in a
   plugin architecture to simulate the signals.
5. Review the `2026-07-17-ama-trusted-external-signals-review.md` for what we can
   implement as real connected signals based on confirmed source endpoints
   (as-of mid-July 2026 - treat as a build-time verification list, not a
   guarantee).
6. Establish a probability risk exposure to the capacity forecast planning to
   trigger the CSA agents and onboard a new scenario and run the simulation based
   on the scenario.
7. Extend the CSA to identify new crisis scenarios automatically based on
   potential risk exposure and run the CSA simulation to recommend potential
   scenarios based on probability and risk exposure to mitigate the risk before
   the risk occurs. If risk is there, establish a mitigation recommendation. Keep
   the CSA Board as it is, just extend it with the data from Foundry IQ and
   Fabric IQ.
8. Evaluate how we can learn, improve, and act based on a closed learning loop for
   the CSA agent and how we can utilize the Fabric IQ Ontology Model to support it
   end to end.

Use superpower to brainstorm and design best-practices design and how we can
utilize the implementation in parallel or delegated to sub agents.
