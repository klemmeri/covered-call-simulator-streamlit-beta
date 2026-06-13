"""
Run the Phase 2 scenario-payoff report adapter check.

This script reads outputs/tables/paid_simulator/scenario_payoff_scaffold.csv and
writes a cleaner report CSV/HTML scaffold. It does not modify the v0.1 dashboard.
"""

from __future__ import annotations

import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def print_header(title: str) -> None:
    print("=" * 88)
    print(title)
    print("=" * 88)


def main() -> int:
    print_header("Phase 2 scenario-payoff report adapter check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    try:
        from app.paid_simulator.scenario_payoff_report_adapter import run_report_adapter
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED - could not import report adapter: {exc}")
        print("Overall scenario-payoff report status: REVIEW")
        return 1

    print("Running scenario-payoff report adapter")
    print("-" * 88)
    try:
        result = run_report_adapter()
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED - report adapter raised an error: {exc}")
        print()
        print("Overall scenario-payoff report status: REVIEW")
        return 1

    print(f"Input:                  {result.input_path}")
    print(f"Output CSV:             {result.output_path}")
    print(f"Output HTML:            {result.html_path}")
    print(f"Rows:                   {result.row_count}")
    print(f"Scenario column:        {result.scenario_column}")
    print(f"Relative column:        {result.relative_column}")
    print(f"Best scenario:          {result.best_scenario}")
    print(f"Worst scenario:         {result.worst_scenario}")
    print(f"Average relative result:{result.average_relative_result}")
    print()

    if result.row_count <= 0 or not result.output_path.exists() or not result.html_path.exists():
        print("Overall scenario-payoff report status: REVIEW")
        return 1

    print("Overall scenario-payoff report status: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
