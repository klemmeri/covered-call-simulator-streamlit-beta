"""
run_paid_simulator_health_check.py

Health-check utility for the paid Covered Call Simulator prototype.

Run this after:

    app/run_paid_simulator.py

The script checks that the main paid-simulator output files exist and that
the scenario comparison and config echo CSV files contain the expected fields.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

CONFIG_PATH = PROJECT_ROOT / "config" / "paid_simulator_config.json"

SCENARIO_COMPARISON_CSV = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "paid_simulator"
    / "scenario_comparison.csv"
)

CONFIG_ECHO_CSV = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "paid_simulator"
    / "config_echo.csv"
)

SCENARIO_COMPARISON_HTML = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "paid_simulator"
    / "scenario_comparison_report.html"
)


REQUIRED_SCENARIO_COLUMNS = [
    "scenario_name",
    "scenario_display_name",
    "ticker",
    "account_size",
    "risk_tier",
    "position_size_cap",
    "desired_contracts",
    "max_contracts_allowed",
    "desired_contracts_pass_screen",
    "target_delta",
    "target_dte",
    "management_rule",
    "strike_selection_method",
    "rolling_rule",
    "reentry_rule",
    "transaction_cost_per_contract",
    "slippage_assumption",
    "data_source",
    "mode",
    "selected_strike",
    "selected_delta",
    "selected_premium_per_contract",
    "selected_total_premium",
    "final_covered_call_equity",
    "final_buy_hold_equity",
    "covered_call_minus_buy_hold",
]

REQUIRED_CONFIG_ECHO_FIELDS = [
    "ticker",
    "account_size",
    "risk_tier",
    "position_size_cap",
    "desired_contracts",
    "max_contracts_allowed",
    "desired_contracts_pass_screen",
    "management_rule",
    "target_delta",
    "target_dte",
    "strike_selection_method",
    "rolling_rule",
    "reentry_rule",
    "transaction_cost_per_contract",
    "slippage_assumption",
    "data_source",
    "mode",
    "ticker_price",
    "decision_signal",
    "next_action",
    "best_environment",
    "worst_environment",
]


def format_money(value: Any) -> str:
    """
    Format a value as dollars.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "N/A"

    return f"${number:,.2f}"


def format_signed_money(value: Any) -> str:
    """
    Format a value as signed dollars.
    """
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "N/A"

    if number >= 0:
        return f"+${number:,.2f}"

    return f"-${abs(number):,.2f}"


def read_json(path: Path) -> dict[str, Any]:
    """
    Read a JSON file safely.
    """
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    """
    Read CSV rows safely.
    """
    if not path.exists():
        return []

    with path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return list(reader)


def print_file_check(label: str, path: Path) -> bool:
    """
    Print whether an expected file exists.
    """
    exists = path.exists()
    status = "FOUND" if exists else "MISSING"

    print(f"{status:<8} {label:<32} {path}")

    return exists


def check_required_columns(
    rows: list[dict[str, str]],
    required_columns: list[str],
) -> list[str]:
    """
    Return required columns missing from a CSV row set.
    """
    if not rows:
        return required_columns

    available_columns = set(rows[0].keys())

    return [
        column
        for column in required_columns
        if column not in available_columns
    ]


def get_config_echo_value(
    config_echo_rows: list[dict[str, str]],
    field_name: str,
) -> str:
    """
    Return a value from config_echo.csv by field name.
    """
    for row in config_echo_rows:
        if row.get("field") == field_name:
            return row.get("value", "")

    return ""


def summarize_scenario_rows(
    scenario_rows: list[dict[str, str]],
) -> dict[str, Any]:
    """
    Summarize best and worst scenario rows.
    """
    if not scenario_rows:
        return {}

    def difference(row: dict[str, str]) -> float:
        try:
            return float(row.get("covered_call_minus_buy_hold", 0.0))
        except (TypeError, ValueError):
            return 0.0

    best_row = max(scenario_rows, key=difference)
    worst_row = min(scenario_rows, key=difference)

    return {
        "scenario_count": len(scenario_rows),
        "best_scenario": best_row.get("scenario_display_name", "N/A"),
        "best_difference": best_row.get("covered_call_minus_buy_hold", "N/A"),
        "worst_scenario": worst_row.get("scenario_display_name", "N/A"),
        "worst_difference": worst_row.get("covered_call_minus_buy_hold", "N/A"),
    }


def run_health_check() -> None:
    """
    Run the paid-simulator output health check.
    """
    print("=" * 92)
    print("Paid simulator health check")
    print("=" * 92)
    print(f"Project root: {PROJECT_ROOT}")

    print()
    print("Expected files")
    print("-" * 92)

    config_exists = print_file_check(
        label="Config file",
        path=CONFIG_PATH,
    )

    scenario_csv_exists = print_file_check(
        label="Scenario comparison CSV",
        path=SCENARIO_COMPARISON_CSV,
    )

    config_echo_exists = print_file_check(
        label="Config echo CSV",
        path=CONFIG_ECHO_CSV,
    )

    html_exists = print_file_check(
        label="Scenario comparison HTML",
        path=SCENARIO_COMPARISON_HTML,
    )

    config = read_json(CONFIG_PATH)
    scenario_rows = read_csv_rows(SCENARIO_COMPARISON_CSV)
    config_echo_rows = read_csv_rows(CONFIG_ECHO_CSV)

    print()
    print("Config summary")
    print("-" * 92)

    if config_exists and config:
        print(f"Ticker:              {config.get('ticker', 'N/A')}")
        print(f"Account size:        {format_money(config.get('account_size'))}")
        print(f"Risk tier:           {config.get('risk_tier', 'N/A')}")
        print(f"Desired contracts:   {config.get('desired_contracts', 'N/A')}")
        print(f"Target delta:        {config.get('target_delta', 'N/A')}")
        print(f"Target DTE:          {config.get('target_dte', 'N/A')}")
        print(f"Management rule:     {config.get('management_rule', 'N/A')}")
    else:
        print("Config could not be read.")

    print()
    print("Scenario comparison CSV audit")
    print("-" * 92)

    scenario_missing_columns = check_required_columns(
        rows=scenario_rows,
        required_columns=REQUIRED_SCENARIO_COLUMNS,
    )

    if not scenario_csv_exists:
        print("Scenario comparison CSV is missing.")
    elif not scenario_rows:
        print("Scenario comparison CSV exists but contains no rows.")
    elif scenario_missing_columns:
        print("Missing required scenario columns:")
        for column in scenario_missing_columns:
            print(f"  - {column}")
    else:
        print("Scenario comparison CSV columns: PASS")

    scenario_summary = summarize_scenario_rows(
        scenario_rows=scenario_rows,
    )

    if scenario_summary:
        print(f"Scenario count:      {scenario_summary.get('scenario_count')}")
        print(
            "Best environment:   "
            f"{scenario_summary.get('best_scenario')} "
            f"({format_signed_money(scenario_summary.get('best_difference'))})"
        )
        print(
            "Worst environment:  "
            f"{scenario_summary.get('worst_scenario')} "
            f"({format_signed_money(scenario_summary.get('worst_difference'))})"
        )

    print()
    print("Config echo CSV audit")
    print("-" * 92)

    config_echo_missing_fields = []

    if config_echo_rows:
        available_fields = {
            row.get("field", "")
            for row in config_echo_rows
        }

        config_echo_missing_fields = [
            field
            for field in REQUIRED_CONFIG_ECHO_FIELDS
            if field not in available_fields
        ]
    else:
        config_echo_missing_fields = REQUIRED_CONFIG_ECHO_FIELDS

    if not config_echo_exists:
        print("Config echo CSV is missing.")
    elif not config_echo_rows:
        print("Config echo CSV exists but contains no rows.")
    elif config_echo_missing_fields:
        print("Missing required config echo fields:")
        for field in config_echo_missing_fields:
            print(f"  - {field}")
    else:
        print("Config echo CSV fields: PASS")

    if config_echo_rows:
        print(
            "Decision signal:    "
            f"{get_config_echo_value(config_echo_rows, 'decision_signal')}"
        )
        print(
            "Next action:        "
            f"{get_config_echo_value(config_echo_rows, 'next_action')}"
        )
        print(
            "Max contracts:      "
            f"{get_config_echo_value(config_echo_rows, 'max_contracts_allowed')}"
        )

    print()
    print("Overall health-check result")
    print("-" * 92)

    passed = (
        config_exists
        and scenario_csv_exists
        and config_echo_exists
        and html_exists
        and bool(scenario_rows)
        and bool(config_echo_rows)
        and not scenario_missing_columns
        and not config_echo_missing_fields
    )

    if passed:
        print("PASS: Paid simulator outputs are present and structurally valid.")
    else:
        print("CHECK NEEDED: One or more paid simulator outputs need attention.")

    print("=" * 92)


if __name__ == "__main__":
    run_health_check()
