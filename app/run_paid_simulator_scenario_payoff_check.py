"""
run_paid_simulator_scenario_payoff_check.py

PyCharm runner for the Phase 2 scenario-payoff connector scaffold.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_scaffold.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> int:
    print("=" * 88)
    print("Phase 2 scenario-payoff scaffold check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    try:
        from app.paid_simulator.scenario_payoff_runner import run_scenario_payoff_scaffold
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED - could not import scenario-payoff runner: {exc}")
        print("Overall scenario-payoff scaffold status: REVIEW")
        return 1

    print("Running scenario-payoff scaffold")
    print("-" * 88)
    try:
        rows = run_scenario_payoff_scaffold()
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED - scaffold run raised an error: {exc}")
        print("Overall scenario-payoff scaffold status: REVIEW")
        return 1

    if not rows:
        print("FAILED - scaffold returned no rows.")
        print("Overall scenario-payoff scaffold status: REVIEW")
        return 1

    if not OUTPUT_PATH.exists():
        print(f"FAILED - expected output file was not created: {OUTPUT_PATH}")
        print("Overall scenario-payoff scaffold status: REVIEW")
        return 1

    with OUTPUT_PATH.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        output_rows = list(reader)
        columns = reader.fieldnames or []

    required_columns = [
        "scenario_name",
        "scenario_display_name",
        "start_price",
        "final_modeled_price",
        "realized_path_return_percent",
        "buy_hold_p_l",
        "covered_call_p_l",
        "covered_call_minus_buy_hold",
        "assigned_flag",
    ]
    missing = [col for col in required_columns if col not in columns]

    print(f"Rows returned: {len(rows)}")
    print(f"Rows written:  {len(output_rows)}")
    print(f"Output file:   {OUTPUT_PATH}")
    print()
    print("Required column check")
    print("-" * 88)
    if missing:
        for col in missing:
            print(f"MISSING - {col}")
        print()
        print("Overall scenario-payoff scaffold status: REVIEW")
        return 1

    for col in required_columns:
        print(f"FOUND   - {col}")

    print()
    print("Sample rows")
    print("-" * 88)
    for row in output_rows[:5]:
        print(
            f"{row.get('scenario_display_name', ''):<22} "
            f"return={row.get('realized_path_return_percent', ''):>8}%  "
            f"relative={row.get('covered_call_minus_buy_hold', '')}"
        )

    print()
    print("=" * 88)
    print("Overall scenario-payoff scaffold status: PASS")
    print("Scenario definitions, modeled endpoints, and scaffold covered-call payoffs are connected.")
    print("=" * 88)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
