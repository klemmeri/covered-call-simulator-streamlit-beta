"""
runner.py

Compact runner for the paid simulator scenario comparison.

This version scales the path simulation to desired_contracts from:

    config/paid_simulator_config.json

It also prints a user-facing decision summary that mirrors the main
conclusions in the HTML stress-test report.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from position_sizing import (
    calculate_position_sizing,
    format_position_sizing_lines,
)
from scenario_comparison import (
    run_all_scenarios,
    summarize_scenario_comparison,
    write_scenario_comparison_csv,
)
from scenario_comparison_report import save_scenario_comparison_html_report
from session_config import (
    build_demo_simulation_input,
    build_demo_ticker_snapshot,
    describe_session_config,
    get_desired_contracts,
)


def safe_float(value: object, default: float = 0.0) -> float:
    """
    Convert a value to float safely.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: object, default: int = 0) -> int:
    """
    Convert a value to int safely.
    """
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def safe_bool(value: object, default: bool = False) -> bool:
    """
    Convert common boolean-like values safely.
    """
    if isinstance(value, bool):
        return value

    if value is None:
        return default

    if isinstance(value, str):
        normalized = value.strip().lower()

        if normalized in {"true", "yes", "y", "1"}:
            return True

        if normalized in {"false", "no", "n", "0"}:
            return False

    return bool(value)


def format_money(value: object) -> str:
    """
    Format a numeric value as dollars.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "N/A"

    return f"${number:,.2f}"


def format_signed_money(value: object) -> str:
    """
    Format a numeric value as signed dollars.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if number >= 0:
        return f"+${number:,.2f}"

    return f"-${abs(number):,.2f}"


def format_decimal_percent(value: object) -> str:
    """
    Format a decimal value as a percent.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "N/A"

    return f"{number:.2%}"


def get_project_root() -> Path:
    """
    Return the Covered Call Simulator project root.
    """
    return Path(__file__).resolve().parents[2]


def get_paid_simulator_table_dir() -> Path:
    """
    Return the paid-simulator table output directory.
    """
    return get_project_root() / "outputs" / "tables" / "paid_simulator"


def get_config_attribute(
    simulation_input: object,
    attribute_name: str,
    default: object = "N/A",
) -> object:
    """
    Read a config attribute safely.
    """
    return getattr(simulation_input, attribute_name, default)


def build_config_echo_rows(
    simulation_input: object,
    ticker_snapshot: object,
    comparison_rows: list[dict[str, object]],
) -> list[dict[str, object]]:
    """
    Build rows for a compact config/audit CSV.
    """
    first_row: dict[str, object] = comparison_rows[0] if comparison_rows else {}

    decision_summary = build_console_decision_summary(
        comparison_rows=comparison_rows,
    )

    rows = [
        {
            "category": "Session",
            "field": "ticker",
            "value": get_config_attribute(simulation_input, "ticker"),
        },
        {
            "category": "Session",
            "field": "account_size",
            "value": get_config_attribute(simulation_input, "account_size"),
        },
        {
            "category": "Session",
            "field": "risk_tier",
            "value": get_config_attribute(simulation_input, "risk_tier"),
        },
        {
            "category": "Sizing",
            "field": "position_size_cap",
            "value": get_config_attribute(simulation_input, "position_size_cap"),
        },
        {
            "category": "Sizing",
            "field": "desired_contracts",
            "value": first_row.get("desired_contracts", get_desired_contracts()),
        },
        {
            "category": "Sizing",
            "field": "max_contracts_allowed",
            "value": first_row.get("max_contracts_allowed", "N/A"),
        },
        {
            "category": "Sizing",
            "field": "desired_contracts_pass_screen",
            "value": first_row.get("desired_contracts_pass_screen", "N/A"),
        },
        {
            "category": "Strategy",
            "field": "management_rule",
            "value": get_config_attribute(simulation_input, "management_rule"),
        },
        {
            "category": "Strategy",
            "field": "target_delta",
            "value": get_config_attribute(simulation_input, "target_delta"),
        },
        {
            "category": "Strategy",
            "field": "target_dte",
            "value": get_config_attribute(simulation_input, "target_dte"),
        },
        {
            "category": "Strategy",
            "field": "strike_selection_method",
            "value": get_config_attribute(simulation_input, "strike_selection_method"),
        },
        {
            "category": "Strategy",
            "field": "rolling_rule",
            "value": get_config_attribute(simulation_input, "rolling_rule"),
        },
        {
            "category": "Strategy",
            "field": "reentry_rule",
            "value": get_config_attribute(simulation_input, "reentry_rule"),
        },
        {
            "category": "Costs",
            "field": "transaction_cost_per_contract",
            "value": get_config_attribute(
                simulation_input,
                "transaction_cost_per_contract",
            ),
        },
        {
            "category": "Costs",
            "field": "slippage_assumption",
            "value": get_config_attribute(simulation_input, "slippage_assumption"),
        },
        {
            "category": "Data",
            "field": "data_source",
            "value": get_config_attribute(simulation_input, "data_source"),
        },
        {
            "category": "Data",
            "field": "mode",
            "value": get_config_attribute(simulation_input, "mode"),
        },
        {
            "category": "Market snapshot",
            "field": "ticker_price",
            "value": getattr(ticker_snapshot, "price", "N/A"),
        },
        {
            "category": "Decision",
            "field": "decision_signal",
            "value": decision_summary.get("decision_signal", "N/A"),
        },
        {
            "category": "Decision",
            "field": "next_action",
            "value": decision_summary.get("next_action", "N/A"),
        },
        {
            "category": "Decision",
            "field": "best_environment",
            "value": decision_summary.get("best_environment", "N/A"),
        },
        {
            "category": "Decision",
            "field": "worst_environment",
            "value": decision_summary.get("worst_environment", "N/A"),
        },
    ]

    return rows


def write_config_echo_csv(
    simulation_input: object,
    ticker_snapshot: object,
    comparison_rows: list[dict[str, object]],
    output_path: Path | None = None,
) -> str:
    """
    Save a compact config/audit CSV for the paid simulator run.
    """
    if output_path is None:
        output_path = get_paid_simulator_table_dir() / "config_echo.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows = build_config_echo_rows(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
        comparison_rows=comparison_rows,
    )

    fieldnames = ["category", "field", "value"]

    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    return str(output_path)


def build_current_inputs() -> tuple[object, object]:
    """
    Build current simulation input and ticker snapshot from config.
    """
    now = datetime.now()

    simulation_input = build_demo_simulation_input(
        created_timestamp=now,
    )

    ticker_snapshot = build_demo_ticker_snapshot(
        timestamp=now,
    )

    return simulation_input, ticker_snapshot


def print_active_config(
    simulation_input: object,
    ticker_snapshot: object,
) -> None:
    """
    Print the active paid-simulator configuration.
    """
    config_summary = describe_session_config(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
    )

    print()
    print("Active paid simulator config")
    print("-" * 92)
    print(f"Config file:    {config_summary.get('config_path')}")
    print(f"Config exists:  {config_summary.get('config_file_exists')}")
    print(f"Ticker:         {config_summary.get('ticker')}")
    print(f"Account size:   {format_money(config_summary.get('account_size'))}")
    print(f"Risk tier:      {config_summary.get('risk_tier')}")
    print(f"Position cap:   {float(config_summary.get('position_size_cap')):.2%}")
    print(f"Desired cntr:   {config_summary.get('desired_contracts')}")
    print(f"Target delta:   {config_summary.get('target_delta')}")
    print(f"Target DTE:     {config_summary.get('target_dte')}")
    print(f"Demo price:     {format_money(config_summary.get('ticker_price'))}")
    print("-" * 92)


def print_position_sizing(
    simulation_input: object,
    ticker_snapshot: object,
) -> None:
    """
    Print position-sizing capacity for the active config.
    """
    position_sizing = calculate_position_sizing(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
        desired_contracts=get_desired_contracts(),
    )

    print()
    print("Position-sizing summary")
    print("-" * 92)

    for line in format_position_sizing_lines(position_sizing):
        print(line)

    print("-" * 92)


def print_compact_comparison_table(
    comparison_rows: list[dict[str, object]],
) -> None:
    """
    Print a compact scenario-comparison table.
    """
    print()
    print("Scenario comparison")
    print("-" * 92)
    print(
        f"{'Scenario':<22}"
        f"{'Covered Call':>16}"
        f"{'Buy & Hold':>16}"
        f"{'Difference':>16}"
        f"{'Final Stock':>16}"
    )
    print("-" * 92)

    for row in comparison_rows:
        scenario_name = str(row.get("scenario_display_name", ""))
        covered_call_equity = format_money(row.get("final_covered_call_equity"))
        buy_hold_equity = format_money(row.get("final_buy_hold_equity"))
        difference = format_signed_money(row.get("covered_call_minus_buy_hold"))
        final_stock_price = format_money(row.get("final_stock_price"))

        print(
            f"{scenario_name:<22}"
            f"{covered_call_equity:>16}"
            f"{buy_hold_equity:>16}"
            f"{difference:>16}"
            f"{final_stock_price:>16}"
        )

    print("-" * 92)


def print_summary(
    comparison_summary: dict[str, object],
) -> None:
    """
    Print the best/worst scenario summary.
    """
    print()
    print("Scenario comparison summary")
    print("-" * 92)
    print(f"Scenario count: {comparison_summary.get('scenario_count')}")
    print(
        "Best scenario: "
        f"{comparison_summary.get('best_scenario')} "
        f"({format_signed_money(comparison_summary.get('best_covered_call_minus_buy_hold'))})"
    )
    print(
        "Worst scenario: "
        f"{comparison_summary.get('worst_scenario')} "
        f"({format_signed_money(comparison_summary.get('worst_covered_call_minus_buy_hold'))})"
    )
    print("-" * 92)


def get_best_row(
    comparison_rows: list[dict[str, object]],
) -> dict[str, object] | None:
    """
    Return the row where covered call beats buy-and-hold by the most.
    """
    if not comparison_rows:
        return None

    return max(
        comparison_rows,
        key=lambda row: safe_float(row.get("covered_call_minus_buy_hold")),
    )


def get_worst_row(
    comparison_rows: list[dict[str, object]],
) -> dict[str, object] | None:
    """
    Return the row where covered call lags buy-and-hold by the most.
    """
    if not comparison_rows:
        return None

    return min(
        comparison_rows,
        key=lambda row: safe_float(row.get("covered_call_minus_buy_hold")),
    )


def build_console_decision_summary(
    comparison_rows: list[dict[str, object]],
) -> dict[str, str]:
    """
    Build a compact user-facing decision summary from comparison rows.
    """
    if not comparison_rows:
        return {
            "decision_signal": "N/A",
            "next_action": "No scenario rows available",
            "best_environment": "N/A",
            "worst_environment": "N/A",
            "desired_contracts": "N/A",
            "maximum_contracts": "N/A",
            "position_size_cap": "N/A",
        }

    first_row = comparison_rows[0]
    best_row = get_best_row(comparison_rows)
    worst_row = get_worst_row(comparison_rows)

    desired_contracts_pass = safe_bool(
        first_row.get("desired_contracts_pass_screen"),
        default=True,
    )

    if desired_contracts_pass:
        decision_signal = "Sizing rule passed"
        next_action = "Review upside tradeoff"
    else:
        decision_signal = "Analyze with caution"
        next_action = "Reduce contract count or adjust sizing"

    best_environment = "N/A"
    worst_environment = "N/A"

    if best_row is not None:
        best_environment = (
            f"{best_row.get('scenario_display_name')} "
            f"({format_signed_money(best_row.get('covered_call_minus_buy_hold'))})"
        )

    if worst_row is not None:
        worst_environment = (
            f"{worst_row.get('scenario_display_name')} "
            f"({format_signed_money(worst_row.get('covered_call_minus_buy_hold'))})"
        )

    return {
        "decision_signal": decision_signal,
        "next_action": next_action,
        "best_environment": best_environment,
        "worst_environment": worst_environment,
        "desired_contracts": str(safe_int(first_row.get("desired_contracts"))),
        "maximum_contracts": str(safe_int(first_row.get("max_contracts_allowed"))),
        "position_size_cap": format_decimal_percent(first_row.get("position_size_cap")),
    }


def print_paid_simulator_decision_summary(
    comparison_rows: list[dict[str, object]],
) -> None:
    """
    Print the user-facing decision summary.
    """
    decision_summary = build_console_decision_summary(
        comparison_rows=comparison_rows,
    )

    print()
    print("Paid simulator decision summary")
    print("-" * 92)
    print(f"Decision signal:        {decision_summary['decision_signal']}")
    print(f"Next action:            {decision_summary['next_action']}")
    print(f"Best environment:       {decision_summary['best_environment']}")
    print(f"Worst environment:      {decision_summary['worst_environment']}")
    print(f"Desired contracts:      {decision_summary['desired_contracts']}")
    print(f"Maximum contracts:      {decision_summary['maximum_contracts']}")
    print(f"Position-size cap:      {decision_summary['position_size_cap']}")
    print("-" * 92)


def run_smoke_test() -> None:
    """
    Run all paid-simulator scenarios and save corrected comparison output.
    """
    simulation_input, ticker_snapshot = build_current_inputs()

    print_active_config(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
    )

    print_position_sizing(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
    )

    now = datetime.now()

    comparison_rows = run_all_scenarios(
        timestamp=now,
        save_individual_reports=True,
    )

    comparison_csv_path = write_scenario_comparison_csv(
        rows=comparison_rows,
    )

    comparison_html_path = save_scenario_comparison_html_report(
        rows=comparison_rows,
    )

    config_echo_csv_path = write_config_echo_csv(
        simulation_input=simulation_input,
        ticker_snapshot=ticker_snapshot,
        comparison_rows=comparison_rows,
    )

    comparison_summary = summarize_scenario_comparison(
        rows=comparison_rows,
    )

    print_compact_comparison_table(
        comparison_rows=comparison_rows,
    )

    print_summary(
        comparison_summary=comparison_summary,
    )

    print_paid_simulator_decision_summary(
        comparison_rows=comparison_rows,
    )

    print()
    print("Saved outputs")
    print("-" * 92)
    print(f"Scenario comparison CSV:  {comparison_csv_path}")
    print(f"Config echo CSV:          {config_echo_csv_path}")
    print(f"Scenario comparison HTML: {comparison_html_path}")
    print("-" * 92)

    print()
    print("Simulation note")
    print("-" * 92)
    print("Path P/L is now scaled to desired_contracts from config.")
    print("If desired contracts fail the position-size screen, results are still")
    print("shown for analysis, but the sizing warning should be respected.")
    print("-" * 92)

    print()
    print("Smoke test complete.")


if __name__ == "__main__":
    run_smoke_test()
