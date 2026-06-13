"""
scenario_comparison.py

Scenario-comparison runner for the paid Covered Call Simulator.

This module runs the same covered-call setup across every scenario in
scenario_library.py and saves a compact comparison table.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any

from account import check_account_feasibility
from html_report import save_html_report
from option_candidates import (
    build_demo_option_candidates,
    select_candidate_by_method,
)
from path_report import save_path_report
from path_runner import (
    run_multi_step_path,
    summarize_path_result,
)
from position_sizing import calculate_position_sizing
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
    build_demo_simulation_input,
    build_demo_ticker_snapshot,
    get_desired_contracts,
)
from trade_execution import simulate_initial_covered_call_placement


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.
    """
    return Path(__file__).resolve().parents[2]


def get_default_output_dir() -> Path:
    """
    Return the default paid-simulator table output directory.
    """
    return get_project_root() / "outputs" / "tables" / "paid_simulator"


def get_config_value(
    simulation_input: object,
    field_name: str,
    default: Any = None,
) -> Any:
    """
    Safely read a configuration field from the simulation input object.

    This keeps report generation resilient while the paid-simulator
    configuration schema is still evolving.
    """
    return getattr(simulation_input, field_name, default)


def add_scenario_metadata_to_summary(
    path_summary: dict[str, object],
    scenario_description: dict[str, object],
) -> dict[str, object]:
    """
    Add selected scenario metadata to a path summary.
    """
    enriched_summary = dict(path_summary)

    enriched_summary["scenario_name"] = scenario_description.get("name")
    enriched_summary["scenario_display_name"] = scenario_description.get(
        "display_name"
    )
    enriched_summary["scenario_description"] = scenario_description.get(
        "description"
    )
    enriched_summary["scenario_total_simple_return_percent"] = scenario_description.get(
        "total_simple_return_percent"
    )

    return enriched_summary


def run_one_scenario(
    scenario_name: str,
    timestamp: datetime,
    save_individual_reports: bool = True,
) -> dict[str, object]:
    """
    Run the paid simulator for one named scenario.
    """
    desired_contracts = get_desired_contracts()

    scenario_description = describe_scenario(
        scenario_name=scenario_name,
    )

    base_simulation_input = build_demo_simulation_input(
        created_timestamp=timestamp,
    )

    simulation_input = build_demo_simulation_input(
        created_timestamp=timestamp,
    )

    simulation_input.session_id = (
        f"{base_simulation_input.session_id}_{scenario_name}"
    )

    ticker_snapshot = build_demo_ticker_snapshot(
        timestamp=timestamp,
    )

    position_sizing = calculate_position_sizing(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
        desired_contracts=desired_contracts,
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
        contract_count=desired_contracts,
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

    path_summary = summarize_path_result(
        simulation_input=simulation_input,
        opening_position_state=opening_position_state,
        equity_snapshots=equity_snapshots,
    )

    enriched_path_summary = add_scenario_metadata_to_summary(
        path_summary=path_summary,
        scenario_description=scenario_description,
    )

    saved_equity_curve_csv = None
    saved_path_summary_csv = None
    saved_html_report = None

    if save_individual_reports:
        saved_report_paths = save_path_report(
            equity_snapshots=equity_snapshots,
            path_summary=enriched_path_summary,
            session_id=simulation_input.session_id,
        )

        saved_equity_curve_csv = saved_report_paths.get("equity_curve_csv")
        saved_path_summary_csv = saved_report_paths.get("path_summary_csv")

        saved_html_report = save_html_report(
            session_id=simulation_input.session_id,
        )

    final_snapshot = equity_snapshots[-1] if equity_snapshots else None

    final_total_equity = None
    final_buy_hold_equity = None
    final_stock_price = None
    final_short_call_value = None
    final_unrealized_option_pl = None

    if final_snapshot is not None:
        final_total_equity = final_snapshot.total_equity
        final_buy_hold_equity = final_snapshot.benchmark_buy_hold_equity
        final_stock_price = final_snapshot.stock_price
        final_short_call_value = final_snapshot.short_call_value
        final_unrealized_option_pl = final_snapshot.unrealized_option_pl

    return {
        "scenario_name": scenario_description["name"],
        "scenario_display_name": scenario_description["display_name"],
        "scenario_steps": scenario_description["steps"],
        "scenario_total_simple_return_percent": scenario_description[
            "total_simple_return_percent"
        ],
        "session_id": simulation_input.session_id,
        "ticker": simulation_input.ticker,
        "account_size": simulation_input.account_size,
        "risk_tier": simulation_input.risk_tier,
        "position_size_cap": simulation_input.position_size_cap,
        "desired_contracts": position_sizing.get("desired_contracts"),
        "stock_value_per_contract": position_sizing.get(
            "stock_value_per_contract"
        ),
        "desired_position_value": position_sizing.get(
            "desired_position_value"
        ),
        "desired_position_percent": position_sizing.get(
            "desired_position_percent"
        ),
        "allowed_position_value": position_sizing.get(
            "allowed_position_value"
        ),
        "minimum_equity_required": position_sizing.get(
            "minimum_equity_required"
        ),
        "max_contracts_allowed": position_sizing.get(
            "max_contracts_allowed"
        ),
        "passes_account_screen": position_sizing.get(
            "passes_account_screen"
        ),
        "desired_contracts_pass_screen": position_sizing.get(
            "desired_contracts_pass_screen"
        ),
        "required_equity_for_desired_contracts": position_sizing.get(
            "required_equity_for_desired_contracts"
        ),
        "required_extra_equity_for_desired_contracts": position_sizing.get(
            "required_extra_equity_for_desired_contracts"
        ),
        "remaining_position_capacity": position_sizing.get(
            "remaining_position_capacity"
        ),
        "target_delta": simulation_input.target_delta,
        "target_dte": simulation_input.target_dte,
        "management_rule": simulation_input.management_rule,
        "profit_take_percent": get_config_value(
            simulation_input,
            "profit_take_percent",
        ),
        "strike_selection_method": get_config_value(
            simulation_input,
            "strike_selection_method",
        ),
        "rolling_rule": get_config_value(
            simulation_input,
            "rolling_rule",
        ),
        "reentry_rule": get_config_value(
            simulation_input,
            "reentry_rule",
        ),
        "transaction_cost_per_contract": get_config_value(
            simulation_input,
            "transaction_cost_per_contract",
        ),
        "slippage_assumption": get_config_value(
            simulation_input,
            "slippage_assumption",
        ),
        "data_source": get_config_value(
            simulation_input,
            "data_source",
        ),
        "mode": get_config_value(
            simulation_input,
            "mode",
        ),
        "selected_strike": selected_option.strike,
        "selected_delta": selected_option.delta,
        "selected_premium_per_contract": selected_option.estimated_premium,
        "selected_total_premium": selected_option.estimated_premium * desired_contracts,
        "pre_trade_premium_yield_percent": round(
            pre_trade_impact.premium_yield * 100.0,
            4,
        ),
        "pre_trade_if_assigned_return_percent": round(
            pre_trade_impact.if_assigned_return * 100.0,
            4,
        ),
        "account_feasibility_passes_account_screen": (
            account_feasibility.passes_account_screen
        ),
        "account_feasibility_minimum_equity_required": (
            account_feasibility.minimum_equity_required
        ),
        "starting_equity_after_entry": enriched_path_summary.get(
            "starting_equity_after_entry"
        ),
        "final_stock_price": final_stock_price,
        "final_covered_call_equity": final_total_equity,
        "final_buy_hold_equity": final_buy_hold_equity,
        "covered_call_pl_after_entry": enriched_path_summary.get(
            "covered_call_pl_after_entry"
        ),
        "buy_hold_pl_from_initial_account": enriched_path_summary.get(
            "buy_hold_pl_from_initial_account"
        ),
        "covered_call_minus_buy_hold": enriched_path_summary.get(
            "covered_call_minus_buy_hold"
        ),
        "final_short_call_value": final_short_call_value,
        "final_unrealized_option_pl": final_unrealized_option_pl,
        "total_missed_upside": enriched_path_summary.get("total_missed_upside"),
        "saved_equity_curve_csv": saved_equity_curve_csv,
        "saved_path_summary_csv": saved_path_summary_csv,
        "saved_html_report": saved_html_report,
    }


def run_all_scenarios(
    timestamp: datetime | None = None,
    save_individual_reports: bool = True,
) -> list[dict[str, object]]:
    """
    Run the paid simulator across all available scenarios.
    """
    if timestamp is None:
        timestamp = datetime.now()

    rows: list[dict[str, object]] = []

    for scenario_name in SCENARIOS:
        row = run_one_scenario(
            scenario_name=scenario_name,
            timestamp=timestamp,
            save_individual_reports=save_individual_reports,
        )
        rows.append(row)

    return rows


def write_scenario_comparison_csv(
    rows: list[dict[str, object]],
    output_path: Path | None = None,
) -> str:
    """
    Save scenario-comparison rows to CSV.
    """
    if output_path is None:
        output_path = get_default_output_dir() / "scenario_comparison.csv"

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


def summarize_scenario_comparison(
    rows: list[dict[str, object]],
) -> dict[str, object]:
    """
    Build a compact scenario-comparison summary.
    """
    if not rows:
        return {
            "scenario_count": 0,
            "message": "No scenarios were run.",
        }

    best_row = max(
        rows,
        key=lambda row: float(row.get("covered_call_minus_buy_hold") or 0.0),
    )

    worst_row = min(
        rows,
        key=lambda row: float(row.get("covered_call_minus_buy_hold") or 0.0),
    )

    return {
        "scenario_count": len(rows),
        "best_scenario": best_row.get("scenario_display_name"),
        "best_covered_call_minus_buy_hold": best_row.get(
            "covered_call_minus_buy_hold"
        ),
        "worst_scenario": worst_row.get("scenario_display_name"),
        "worst_covered_call_minus_buy_hold": worst_row.get(
            "covered_call_minus_buy_hold"
        ),
    }
