"""Sprint 41 WS-EVAL Task EVAL.3: registration stub for wiring
golden_questions.yaml into Foundry's managed evaluation service
(dataset_create -> suite_create -> suite_run), so PO-agent regressions are
tracked once live credentials and a Foundry project connection are
available.

evals/lib/ (harness.py, online.py) is Sprint 30's continuous-eval pattern
for the decision-sim copilots (bmca/ooa/etc.): it scores flat
DC-AGENT-INTERACTION-v1 JSONL records with its own six evaluators
(citation_coverage, groundedness, refusal_correctness, phi_leak,
actionability, advisory_voice). The PO agent's golden_questions.yaml is a
per-persona Q&A grounding dataset with a different shape (question/persona/
tier/chunks) and its own scoring (run_evals.py + relevancy.py), so this
script does not reuse evals/lib/ directly - it does not generalise to this
Q&A grounding shape. This module only loads the dataset; it does NOT
fabricate a working live registration call.

Run manually or from po-agent-live-eval.yml:
    python evals/product-owner-agent/register_foundry_eval.py
"""

from __future__ import annotations

import yaml


def load_dataset_rows(path: str = "evals/product-owner-agent/golden_questions.yaml") -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    return [
        {"question": q["question"], "persona": q["persona"], "tier": q["tier"], "expect": q["expect"]}
        for q in doc["questions"]
    ]


def main() -> None:
    rows = load_dataset_rows()
    # Uses the Foundry evaluation MCP / SDK (evaluation_dataset_create ->
    # evaluation_suite_create -> evaluation_suite_run) - see the design spec
    # WS-EVAL section for the exact tool sequence; project connection details
    # come from the same ai-ihzhhpf-sit-eastus2 project agent-host already uses.
    print(f"Loaded {len(rows)} golden questions for Foundry evaluation registration.")


if __name__ == "__main__":
    main()
