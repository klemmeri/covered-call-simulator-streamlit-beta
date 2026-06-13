"""
accounting_audit.py

Accounting audit for the paid Covered Call Simulator.

Purpose:
    Verify the covered-call and buy-and-hold accounting identities before
    treating scenario-comparison results as economically meaningful.

The audit checks:

    1. Opening covered-call equity identity.
    2. Final covered-call equity identity.
    3. Reported buy-and-hold benchmark.
    4. Component-based buy-and-hold benchmark.
    5. Reported covered-call minus buy-and-hold.
    6. Component-based covered-call minus buy-and-hold.
    7. Short-call mark versus intrinsic value.

This is intentionally diagnostic. It is not a user-facing report yet.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from account import check_account_feasibility
from option_candidates import (
    build_demo_option_candidates,
    select_candidate_by_method,
)
from path_runner import (
    run_multi_step_path,
    summarize_path_result,
)
from pre_trade import (
    build_selected_option_from_candidate,
    calculate_pre_trade_impact,
)
from scenario_library import (
    SCENARIOS,
    describe_scenario,
    generate_scenario_price_path,
)
from session_config import (
    DEFAULT_ACCOUNT_SIZE,
    DEFAULT_DATA_SOURCE,
    DEFAULT_MANAGEMENT_RULE,
    DEFAULT_POSITION_SIZE_CAP,
    DEFAULT_PROFIT_TAKE_PERCENT,
    DEFAULT_REENTRY_RULE,
    DEFAULT_RISK_TIER,
    DEFAULT_ROLLING_RULE,
    DEFAULT_SLIPPAGE_ASSUMPTION,
    DEFAULT_STRIKE_SELECTION_METHOD,
    DEFAULT_TARGET_DELTA,
    DEFAULT_TARGET_DTE,
    DEFAULT_TICKER,
    DEFAULT_TRANSACTION_COST_PER_CONTRACT,
    build_simulation_input,
    build_ticker_snapshot,
)
from trade_execution import simulate_initial_covered_call_placement


CONTRACT_MULTIPLIER = 100


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.
    """
    return Path(__file__).resolve().parents[2]


def get_default_output_dir() -> Path:
    """
    Return the default paid-simulator output table directory.
    """
    return get_project_root() / "outputs" / "tables" / "paid_simulator"


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Convert a value to float safely.
    """
    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def round_money(value: Any) -> float:
    """
    Round a value to two decimals.
    """
    return round(safe_float(value), 2)


def build_audit_simulation_input(
    timestamp: datetime,
    scenario_name: str,
) -> Any:
    """
    Build a SimulationInput for one audit scenario.
    """
    return build_simulation_input(
        created_timestamp=timestamp,
        session_id=f"audit_session_001_{scenario_name}",
        ticker=DEFAULT_TICKER,
        account_size=DEFAULT_ACCOUNT_SIZE,
        risk_tier=DEFAULT_RISK_TIER,
        position_size_cap=DEFAULT_POSITION_SIZE_CAP,
        target_delta=DEFAULT_TARGET_DELTA,
        target_dte=DEFAULT_TARGET_DTE,
        strike_selection_method=DEFAULT_STRIKE_SELECTION_METHOD,
        management_rule=DEFAULT_MANAGEMENT_RULE,
        profit_take_percent=DEFAULT_PROFIT_TAKE_PERCENT,
        rolling_rule=DEFAULT_ROLLING_RULE,
        reentry_rule=DEFAULT_REENTRY_RULE,
        transaction_cost_per_contract=DEFAULT_TRANSACTION_COST_PER_CONTRACT,
        slippage_assumption=DEFAULT_SLIPPAGE_ASSUMPTION,
        data_source=DEFAULT_DATA_SOURCE,
    )


def get_total_premium(selected_option: Any) -> float:
    """
    Get total premium received for one option contract.
    """
    estimated_premium = getattr(selected_option, "estimated_premium", None)

    if estimated_premium is not None:
        return safe_float(estimated_premium)

    selected_price = safe_float(getattr(selected_option, "selected_price", 0.0))
    return selected_price * CONTRACT_MULTIPLIER


def audit_one_scenario(
    scenario_name: str,
    timestamp: datetime,
) -> dict[str, object]:
    """
    Run one scenario and return detailed accounting-audit fields.
    """
    scenario_description = describe_scenario(
        scenario_name=scenario_name,
    )

    simulation_input = build_audit_simulation_input(
        timestamp=timestamp,
        scenario_name=scenario_name,
    )

    ticker_snapshot = build_ticker_snapshot(
        timestamp=timestamp,
        ticker=simulation_input.ticker,
    )

    account_feasibility = check_account_feasibility(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
    )

    option_candidates = build_demo_option_candidates(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
    )

    selected_candidate = select_candidate_by_method(
        candidates=option_candidates,
        simulation_input=simulation_input,
    )

    if selected_candidate is None:
        raise RuntimeError(f"No option candidate selected for {scenario_name}.")

    selected_option = build_selected_option_from_candidate(
        candidate=selected_candidate,
        selection_timestamp=timestamp,
        transaction_cost_per_contract=(
            simulation_input.transaction_cost_per_contract
        ),
    )

    pre_trade_impact = calculate_pre_trade_impact(
        stock_price=float(ticker_snapshot.price),
        strike_price=selected_option.strike,
        option_price=selected_option.selected_price,
        delta=selected_option.delta,
    )

    trade_events, opening_position_state = simulate_initial_covered_call_placement(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
        selected_option=selected_option,
    )

    path_prices = generate_scenario_price_path(
        starting_price=float(ticker_snapshot.price),
        scenario_name=scenario_name,
    )

    position_states, equity_snapshots = run_multi_step_path(
        simulation_input=simulation_input,
        opening_position_state=opening_position_state,
        selected_option=selected_option,
        path_prices=path_prices,
        start_timestamp=timestamp,
        days_per_step=1,
    )

    if not equity_snapshots:
        raise RuntimeError(f"No equity snapshots generated for {scenario_name}.")

    final_snapshot = equity_snapshots[-1]

    path_summary = summarize_path_result(
        simulation_input=simulation_input,
        opening_position_state=opening_position_state,
        equity_snapshots=equity_snapshots,
    )

    account_size = safe_float(simulation_input.account_size)
    opening_stock_price = safe_float(ticker_snapshot.price)
    final_stock_price = safe_float(final_snapshot.stock_price)
    share_count = CONTRACT_MULTIPLIER
    stock_cost = opening_stock_price * share_count
    final_stock_value = final_stock_price * share_count

    total_premium_received = get_total_premium(selected_option)
    transaction_cost = safe_float(
        simulation_input.transaction_cost_per_contract
    )

    selected_strike = safe_float(selected_option.strike)
    final_intrinsic_value = max(final_stock_price - selected_strike, 0.0) * share_count

    opening_cash_expected = (
        account_size
        - stock_cost
        + total_premium_received
        - transaction_cost
    )

    opening_short_call_liability_expected = -total_premium_received

    opening_equity_expected = (
        opening_cash_expected
        + stock_cost
        + opening_short_call_liability_expected
    )

    opening_equity_reported = safe_float(
        getattr(opening_position_state, "total_equity", opening_equity_expected)
    )

    opening_equity_identity_error = opening_equity_reported - opening_equity_expected

    final_cash = safe_float(final_snapshot.cash)
    final_short_call_value = safe_float(final_snapshot.short_call_value)
    final_total_equity_reported = safe_float(final_snapshot.total_equity)
    final_buy_hold_reported = safe_float(final_snapshot.benchmark_buy_hold_equity)

    final_equity_from_components = (
        final_cash
        + final_stock_value
        + final_short_call_value
    )

    final_equity_identity_error = (
        final_total_equity_reported
        - final_equity_from_components
    )

    buy_hold_equity_from_components = (
        account_size
        - stock_cost
        + final_stock_value
    )

    buy_hold_benchmark_error = (
        final_buy_hold_reported
        - buy_hold_equity_from_components
    )

    reported_difference = safe_float(
        path_summary.get("covered_call_minus_buy_hold")
    )

    difference_from_reported_values = (
        final_total_equity_reported
        - final_buy_hold_reported
    )

    difference_from_component_benchmark = (
        final_total_equity_reported
        - buy_hold_equity_from_components
    )

    reported_difference_error = (
        reported_difference
        - difference_from_reported_values
    )

    short_call_mark_value = -final_short_call_value
    short_call_mark_minus_intrinsic = (
        short_call_mark_value
        - final_intrinsic_value
    )

    option_pl_from_mark = (
        total_premium_received
        + final_short_call_value
        - transaction_cost
    )

    stock_pl = (
        final_stock_price
        - opening_stock_price
    ) * share_count

    covered_call_pl_from_components = (
        stock_pl
        + total_premium_received
        + final_short_call_value
        - transaction_cost
    )

    reported_covered_call_pl_after_entry = safe_float(
        path_summary.get("covered_call_pl_after_entry")
    )

    component_pl_error = (
        reported_covered_call_pl_after_entry
        - covered_call_pl_from_components
    )

    return {
        "scenario_name": scenario_description["name"],
        "scenario_display_name": scenario_description["display_name"],
        "scenario_total_simple_return_percent": scenario_description[
            "total_simple_return_percent"
        ],
        "passes_account_screen": account_feasibility.passes_account_screen,
        "account_size": round_money(account_size),
        "opening_stock_price": round_money(opening_stock_price),
        "final_stock_price": round_money(final_stock_price),
        "share_count": share_count,
        "stock_cost": round_money(stock_cost),
        "final_stock_value": round_money(final_stock_value),
        "selected_strike": round_money(selected_strike),
        "selected_delta": safe_float(selected_option.delta),
        "selected_option_price": safe_float(selected_option.selected_price),
        "total_premium_received": round_money(total_premium_received),
        "transaction_cost": round_money(transaction_cost),
        "pre_trade_premium_yield_percent": round(
            safe_float(pre_trade_impact.premium_yield) * 100.0,
            4,
        ),
        "opening_cash_expected": round_money(opening_cash_expected),
        "opening_short_call_liability_expected": round_money(
            opening_short_call_liability_expected
        ),
        "opening_equity_expected": round_money(opening_equity_expected),
        "opening_equity_reported": round_money(opening_equity_reported),
        "opening_equity_identity_error": round_money(opening_equity_identity_error),
        "final_cash": round_money(final_cash),
        "final_short_call_value": round_money(final_short_call_value),
        "final_intrinsic_value": round_money(final_intrinsic_value),
        "short_call_mark_value": round_money(short_call_mark_value),
        "short_call_mark_minus_intrinsic": round_money(
            short_call_mark_minus_intrinsic
        ),
        "final_total_equity_reported": round_money(final_total_equity_reported),
        "final_equity_from_components": round_money(final_equity_from_components),
        "final_equity_identity_error": round_money(final_equity_identity_error),
        "final_buy_hold_reported": round_money(final_buy_hold_reported),
        "buy_hold_equity_from_components": round_money(
            buy_hold_equity_from_components
        ),
        "buy_hold_benchmark_error": round_money(buy_hold_benchmark_error),
        "reported_covered_call_minus_buy_hold": round_money(reported_difference),
        "difference_from_reported_values": round_money(
            difference_from_reported_values
        ),
        "difference_from_component_benchmark": round_money(
            difference_from_component_benchmark
        ),
        "reported_difference_error": round_money(reported_difference_error),
        "stock_pl": round_money(stock_pl),
        "option_pl_from_mark": round_money(option_pl_from_mark),
        "covered_call_pl_from_components": round_money(
            covered_call_pl_from_components
        ),
        "reported_covered_call_pl_after_entry": round_money(
            reported_covered_call_pl_after_entry
        ),
        "component_pl_error": round_money(component_pl_error),
    }


def run_accounting_audit(
    timestamp: datetime | None = None,
) -> list[dict[str, object]]:
    """
    Run the accounting audit for all scenarios.
    """
    if timestamp is None:
        timestamp = datetime.now()

    rows: list[dict[str, object]] = []

    for scenario_name in SCENARIOS:
        rows.append(
            audit_one_scenario(
                scenario_name=scenario_name,
                timestamp=timestamp,
            )
        )

    return rows


def write_accounting_audit_csv(
    rows: list[dict[str, object]],
    output_path: Path | None = None,
) -> str:
    """
    Save audit rows to CSV.
    """
    if output_path is None:
        output_path = get_default_output_dir() / "accounting_audit.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        output_path.write_text("", encoding="utf-8")
        return str(output_path)

    fieldnames = list(rows[0].keys())

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    return str(output_path)


def summarize_accounting_audit(
    rows: list[dict[str, object]],
) -> dict[str, object]:
    """
    Summarize major audit errors across scenarios.
    """
    if not rows:
        return {
            "scenario_count": 0,
            "message": "No audit rows were generated.",
        }

    max_opening_equity_identity_error = max(
        abs(safe_float(row.get("opening_equity_identity_error")))
        for row in rows
    )

    max_final_equity_identity_error = max(
        abs(safe_float(row.get("final_equity_identity_error")))
        for row in rows
    )

    max_buy_hold_benchmark_error = max(
        abs(safe_float(row.get("buy_hold_benchmark_error")))
        for row in rows
    )

    max_reported_difference_error = max(
        abs(safe_float(row.get("reported_difference_error")))
        for row in rows
    )

    max_component_pl_error = max(
        abs(safe_float(row.get("component_pl_error")))
        for row in rows
    )

    scenarios_with_underpriced_intrinsic = [
        row.get("scenario_display_name")
        for row in rows
        if safe_float(row.get("short_call_mark_minus_intrinsic")) < -0.01
    ]

    return {
        "scenario_count": len(rows),
        "max_opening_equity_identity_error": round_money(
            max_opening_equity_identity_error
        ),
        "max_final_equity_identity_error": round_money(
            max_final_equity_identity_error
        ),
        "max_buy_hold_benchmark_error": round_money(
            max_buy_hold_benchmark_error
        ),
        "max_reported_difference_error": round_money(
            max_reported_difference_error
        ),
        "max_component_pl_error": round_money(max_component_pl_error),
        "scenarios_with_underpriced_intrinsic": scenarios_with_underpriced_intrinsic,
    }


def print_accounting_audit(rows: list[dict[str, object]]) -> None:
    """
    Print compact audit diagnostics to the console.
    """
    print()
    print("Accounting audit")

    for row in rows:
        scenario = row.get("scenario_display_name")
        reported_diff = safe_float(row.get("reported_covered_call_minus_buy_hold"))
        component_diff = safe_float(row.get("difference_from_component_benchmark"))
        benchmark_error = safe_float(row.get("buy_hold_benchmark_error"))
        final_equity_error = safe_float(row.get("final_equity_identity_error"))

        print(
            f"{scenario}: "
            f"reported diff ${reported_diff:,.2f}, "
            f"component diff ${component_diff:,.2f}, "
            f"buy-hold benchmark error ${benchmark_error:,.2f}, "
            f"final equity identity error ${final_equity_error:,.2f}"
        )
