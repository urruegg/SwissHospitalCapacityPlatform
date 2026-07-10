"""BVA KPI reference formulas (Sprint 15 · T5).

Single, tested source of truth for the **semantics** of every BVA KPI measure.
The DAX measures in
``data-platform/reports/capacity-dashboard.SemanticModel/definition/tables/bva_measures.tmdl``
mirror these formulas one-for-one; the DAX↔Python mapping is catalogued in
``docs/adr/0025-bva-kpi-catalog.md``.

Because the sandbox cannot evaluate DAX, this module lets the golden tests
(`data-platform/reports/tests/test_bva_kpi_golden.py`) validate the KPI
arithmetic and calibration against the synthetic seed. It is pure (stdlib only),
takes the Gold fact rows produced by :mod:`bva_transforms`, and returns a flat
``{kpi_name: value}`` dict.

All target / rate constants are **synthetic** and documented so every board KPI
stays explainable. No PHI, no real financials.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping

# --- Synthetic calibration constants (mirrored as literals in the DAX) --------
TARGET_ANNUAL_BENEFIT_CHF = 1_200_000.0  # CEO benefit-realization denominator
TARGET_ACTIVE_USERS = 120.0              # CEO strategic-adoption denominator
BED_DAYS_PER_DECISION_CYCLE = 0.02       # COO avoidable bed-day proxy
MANUAL_TOUCHES_PER_DECISION_CYCLE = 0.5  # COO manual-touch proxy
COPILOT_TURNS_PER_USER_YEAR = 144.0      # CTO cost-per-turn denominator (12/mo)
MONTHS_PER_YEAR = 12.0


def _safe_div(numerator: float, denominator: float) -> float:
    """DAX ``DIVIDE`` semantics: return 0.0 when the denominator is zero."""
    if not denominator:
        return 0.0
    return numerator / denominator


def _sum(rows: Iterable[Mapping], column: str) -> float:
    return float(sum(float(r.get(column, 0) or 0) for r in rows))


def _distinct(rows: Iterable[Mapping], column: str) -> int:
    return len({r.get(column) for r in rows if r.get(column) is not None})


def compute_kpis(
    consumption_facts: Iterable[Mapping],
    budget_facts: Iterable[Mapping],
    value_facts: Iterable[Mapping],
) -> dict[str, float]:
    """Compute every BVA KPI from the Gold fact rows.

    Args:
        consumption_facts: rows of ``gold.bva_fact_azure_consumption``.
        budget_facts: rows of ``gold.bva_fact_budget``.
        value_facts: rows of ``gold.bva_fact_value_realization``.

    Returns:
        Flat mapping of KPI name → value. Names match the DAX measure names.
    """
    consumption = list(consumption_facts)
    budget = list(budget_facts)
    value = list(value_facts)

    # --- Base aggregates -----------------------------------------------------
    effective_cost = _sum(consumption, "effective_cost")
    list_cost = _sum(consumption, "list_cost")
    plan_cost = _sum(budget, "plan_cost")
    budget_variance = _sum(budget, "variance_cost")
    benefit_realized = _sum(value, "benefit_realized")
    active_users = _sum(value, "adoption_count")
    decision_cycles = _sum(value, "decision_cycles")
    months_in_scope = float(
        _distinct([{"month_key": str(r.get("date_key", ""))[:7]}
                   for r in consumption], "month_key"))
    capability_count = float(_distinct(value, "capability_key")) or 1.0

    # --- Annualisation helpers ----------------------------------------------
    actual_tco_annual = _safe_div(effective_cost, months_in_scope) * MONTHS_PER_YEAR
    benefit_annual = _safe_div(benefit_realized, months_in_scope) * MONTHS_PER_YEAR
    net_annual_benefit = benefit_annual - actual_tco_annual

    kpis: dict[str, float] = {
        # base
        "Effective Cost": effective_cost,
        "List Cost": list_cost,
        "Plan Cost": plan_cost,
        "Budget Variance": budget_variance,
        "Benefit Realized": benefit_realized,
        "Active Users": active_users,
        "Decision Cycles": decision_cycles,
        "Months In Scope": months_in_scope,
        # CEO
        "Actual TCO (Annualized)": actual_tco_annual,
        "Benefit Realized (Annualized)": benefit_annual,
        "Net Annual Benefit": net_annual_benefit,
        "Net Value Realized (3yr)": net_annual_benefit * 3.0,
        "Benefit Realization %": _safe_div(benefit_annual, TARGET_ANNUAL_BENEFIT_CHF),
        "ROI %": _safe_div(net_annual_benefit, actual_tco_annual),
        "Strategic Adoption %": _safe_div(active_users, TARGET_ACTIVE_USERS),
        # CFO
        "Budget Variance %": _safe_div(budget_variance, plan_cost),
        "Cost-to-Value Ratio": _safe_div(actual_tco_annual, benefit_annual),
        "Azure Spend (Period)": effective_cost,
        "Payback (Months)": _safe_div(actual_tco_annual, net_annual_benefit) * MONTHS_PER_YEAR,
        # CIO
        "Azure Run-Rate (Monthly)": _safe_div(effective_cost, months_in_scope),
        "Cost Optimization Realized": list_cost - effective_cost,
        "Cost Avoidance %": _safe_div(list_cost - effective_cost, list_cost),
        # COO (synthetic operational proxies)
        "Avoidable Bed-Day Index": decision_cycles * BED_DAYS_PER_DECISION_CYCLE,
        "Manual Touches Saved": decision_cycles * MANUAL_TOUCHES_PER_DECISION_CYCLE,
        # CTO
        "Cost per Decision Cycle": _safe_div(effective_cost, decision_cycles),
        "Cost per Copilot Turn": _safe_div(
            effective_cost, active_users * COPILOT_TURNS_PER_USER_YEAR),
        "Cost per Capability": _safe_div(effective_cost, capability_count),
        "Inference Efficiency (cycles/CHF)": _safe_div(decision_cycles, effective_cost),
    }
    return kpis


HEADLINE_KPIS: dict[str, tuple[str, ...]] = {
    "CEO": ("Net Value Realized (3yr)", "Benefit Realization %"),
    "CFO": ("Actual TCO (Annualized)", "Budget Variance %"),
    "CIO": ("Azure Run-Rate (Monthly)", "Cost Optimization Realized"),
    "COO": ("Avoidable Bed-Day Index",),
    "CTO": ("Cost per Copilot Turn",),
}
