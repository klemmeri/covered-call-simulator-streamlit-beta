"""
scenario_payoff_runner.py

Phase 2 scenario-payoff connector scaffold for the paid covered-call simulator.

This module intentionally stays separate from the working v0.1 dashboard and
simulator engine. It connects, where possible, the Phase 2 scaffold modules:

    app.paid_simulator.scenario_model
    app.paid_simulator.scenario_price_paths
    app.paid_simulator.option_payoff_model

The earlier scaffold expected a function named build_default_scenarios(). This
replacement is more defensive: it supports several likely function names and
falls back to a small internal scenario set if needed. That prevents the Phase 2
connector from breaking merely because an earlier scaffold used a different
helper name.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any

import csv
import importlib
import math
import sys


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[2]
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_scaffold.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@dataclass
class FallbackScenario:
    name: str
    display_name: str
    total_return: float
    volatility_label: str
    path_shape: str
    interpretation: str


FALLBACK_SCENARIOS: list[FallbackScenario] = [
    FallbackScenario(
        name="downtrend",
        display_name="Downtrend",
        total_return=-0.08,
        volatility_label="moderate",
        path_shape="front_loaded",
        interpretation="A declining path where option premium can cushion part of the stock loss.",
    ),
    FallbackScenario(
        name="sideways_choppy",
        display_name="Sideways Choppy",
        total_return=0.00,
        volatility_label="moderate",
        path_shape="choppy",
        interpretation="A flat but noisy path where premium income may help relative to buy-and-hold.",
    ),
    FallbackScenario(
        name="moderate_uptrend",
        display_name="Moderate Uptrend",
        total_return=0.05,
        volatility_label="low",
        path_shape="linear",
        interpretation="A moderate rally where covered calls can still participate but may begin to lag.",
    ),
    FallbackScenario(
        name="strong_rally",
        display_name="Strong Rally",
        total_return=0.14,
        volatility_label="low",
        path_shape="back_loaded",
        interpretation="A strong rally where the short call can cap upside and cause underperformance.",
    ),
    FallbackScenario(
        name="volatile_whipsaw",
        display_name="Volatile Whipsaw",
        total_return=0.02,
        volatility_label="high",
        path_shape="whipsaw",
        interpretation="A large two-way path where realized volatility matters more than endpoint return.",
    ),
]


def _object_to_dict(obj: Any) -> dict[str, Any]:
    """Convert common scaffold objects to dictionaries."""
    if isinstance(obj, dict):
        return dict(obj)
    if is_dataclass(obj):
        return asdict(obj)
    out: dict[str, Any] = {}
    for key in [
        "name",
        "scenario_name",
        "display_name",
        "scenario_display_name",
        "total_return",
        "total_simple_return",
        "total_modeled_return",
        "volatility_label",
        "path_shape",
        "interpretation",
    ]:
        if hasattr(obj, key):
            out[key] = getattr(obj, key)
    return out


def _normalize_scenario(raw: Any) -> dict[str, Any]:
    data = _object_to_dict(raw)
    name = data.get("name") or data.get("scenario_name") or data.get("scenario") or "scenario"
    display_name = data.get("display_name") or data.get("scenario_display_name") or str(name).replace("_", " ").title()

    total_return = (
        data.get("total_return")
        if data.get("total_return") is not None
        else data.get("total_simple_return")
        if data.get("total_simple_return") is not None
        else data.get("total_modeled_return")
    )
    try:
        total_return_float = float(total_return)
    except Exception:
        total_return_float = 0.0

    return {
        "scenario_name": str(name),
        "scenario_display_name": str(display_name),
        "total_return": total_return_float,
        "volatility_label": str(data.get("volatility_label", "not specified")),
        "path_shape": str(data.get("path_shape", "linear")),
        "interpretation": str(data.get("interpretation", "No interpretation provided.")),
    }


def load_phase2_scenarios() -> list[dict[str, Any]]:
    """Load scenarios from scenario_model.py, tolerating different helper names."""
    try:
        scenario_model = importlib.import_module("app.paid_simulator.scenario_model")
    except Exception:
        return [_normalize_scenario(item) for item in FALLBACK_SCENARIOS]

    candidate_function_names = [
        "build_default_scenarios",
        "get_default_scenarios",
        "default_scenarios",
        "build_scenarios",
        "get_scenarios",
        "load_default_scenarios",
    ]

    for func_name in candidate_function_names:
        func = getattr(scenario_model, func_name, None)
        if callable(func):
            try:
                scenarios = func()
                return [_normalize_scenario(item) for item in scenarios]
            except Exception:
                continue

    for attr_name in ["DEFAULT_SCENARIOS", "SCENARIOS", "PHASE2_SCENARIOS"]:
        value = getattr(scenario_model, attr_name, None)
        if value:
            try:
                return [_normalize_scenario(item) for item in value]
            except Exception:
                continue

    return [_normalize_scenario(item) for item in FALLBACK_SCENARIOS]


def final_price_from_scenario(start_price: float, scenario: dict[str, Any]) -> float:
    return start_price * (1.0 + float(scenario.get("total_return", 0.0)))


def estimate_call_strike(start_price: float, target_delta: float = 0.30) -> float:
    """Simple scaffold strike estimator.

    Lower deltas are placed farther OTM; higher deltas are placed closer to ATM.
    This is not a full option-pricing model.
    """
    target_delta = max(0.05, min(0.50, float(target_delta)))
    otm_fraction = max(0.01, 0.16 - 0.30 * target_delta)
    raw_strike = start_price * (1.0 + otm_fraction)
    return round(raw_strike / 5.0) * 5.0


def estimate_call_premium(start_price: float, strike: float, target_dte: int = 30, target_delta: float = 0.30) -> float:
    """Simple scaffold premium estimator per share."""
    dte_scale = math.sqrt(max(1, int(target_dte)) / 30.0)
    delta_scale = max(0.10, min(0.60, float(target_delta))) / 0.30
    base = start_price * 0.0125 * dte_scale * delta_scale
    otm_discount = max(0.45, 1.0 - max(strike - start_price, 0.0) / max(start_price, 1.0))
    return round(base * otm_discount, 2)


def calculate_covered_call_payoff(
    start_price: float,
    final_price: float,
    contracts: int = 1,
    target_delta: float = 0.30,
    target_dte: int = 30,
    transaction_cost: float = 1.00,
    slippage_assumption: float = 0.01,
) -> dict[str, Any]:
    """Calculate simplified one-cycle covered-call payoff for scaffold testing."""
    shares = int(contracts) * 100
    strike = estimate_call_strike(start_price, target_delta)
    premium_per_share = estimate_call_premium(start_price, strike, target_dte, target_delta)
    premium_income = premium_per_share * shares
    buy_hold_pl = (final_price - start_price) * shares
    call_intrinsic_loss = max(final_price - strike, 0.0) * shares
    total_costs = float(transaction_cost) * max(int(contracts), 1) + float(slippage_assumption) * shares
    covered_call_pl = buy_hold_pl + premium_income - call_intrinsic_loss - total_costs
    relative_result = covered_call_pl - buy_hold_pl
    return {
        "shares": shares,
        "strike": strike,
        "premium_per_share": premium_per_share,
        "premium_income": premium_income,
        "call_intrinsic_loss": call_intrinsic_loss,
        "transaction_and_slippage_costs": total_costs,
        "buy_hold_p_l": buy_hold_pl,
        "covered_call_p_l": covered_call_pl,
        "covered_call_minus_buy_hold": relative_result,
        "assigned_flag": bool(final_price > strike),
    }


def run_scenario_payoff_scaffold(
    start_price: float = 545.25,
    contracts: int = 1,
    target_delta: float = 0.30,
    target_dte: int = 30,
    transaction_cost: float = 1.00,
    slippage_assumption: float = 0.01,
    output_path: Path = OUTPUT_PATH,
) -> list[dict[str, Any]]:
    """Run the standalone Phase 2 scenario-payoff scaffold."""
    scenarios = load_phase2_scenarios()
    rows: list[dict[str, Any]] = []

    for scenario in scenarios:
        final_price = final_price_from_scenario(start_price, scenario)
        payoff = calculate_covered_call_payoff(
            start_price=start_price,
            final_price=final_price,
            contracts=contracts,
            target_delta=target_delta,
            target_dte=target_dte,
            transaction_cost=transaction_cost,
            slippage_assumption=slippage_assumption,
        )
        rows.append(
            {
                "scenario_name": scenario["scenario_name"],
                "scenario_display_name": scenario["scenario_display_name"],
                "volatility_label": scenario["volatility_label"],
                "path_shape": scenario["path_shape"],
                "start_price": start_price,
                "final_modeled_price": round(final_price, 4),
                "realized_path_return_percent": round(float(scenario["total_return"]) * 100.0, 4),
                **payoff,
                "interpretation": scenario["interpretation"],
            }
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    return rows


if __name__ == "__main__":
    result_rows = run_scenario_payoff_scaffold()
    print(f"Wrote {len(result_rows)} scenario-payoff rows to: {OUTPUT_PATH}")
