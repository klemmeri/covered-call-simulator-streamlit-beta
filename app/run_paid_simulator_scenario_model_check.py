"""
run_paid_simulator_scenario_model_check.py

Standalone PyCharm checker for the Phase 2 scenario-model scaffold.
"""

from __future__ import annotations

import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def print_line(char: str = "=", width: int = 88) -> None:
    print(char * width)


def main() -> None:
    print_line()
    print("Phase 2 scenario-model scaffold check")
    print_line()
    print(f"Project root: {PROJECT_ROOT}")
    print()

    try:
        from app.paid_simulator.scenario_model import (
            build_scenario_summary_text,
            get_default_scenarios,
            scenarios_to_dataframe,
            validate_scenarios,
        )
    except Exception as exc:  # noqa: BLE001
        print("IMPORT FAILED")
        print(exc)
        print_line()
        print("Overall scenario-model status: REVIEW")
        raise SystemExit(1) from exc

    scenarios = get_default_scenarios()
    errors, warnings = validate_scenarios(scenarios)
    df = scenarios_to_dataframe(scenarios)

    print("Scenario count")
    print("-" * 88)
    print(len(scenarios))
    print()

    print("Scenario table")
    print("-" * 88)
    print(df.to_string(index=False))
    print()

    print("Scenario summary")
    print("-" * 88)
    print(build_scenario_summary_text(scenarios))
    print()

    print_line()
    if errors:
        print("Overall scenario-model status: REVIEW")
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print("Overall scenario-model status: PASS")
    if warnings:
        print("Nonblocking warnings:")
        for warning in warnings:
            print(f"- {warning}")
    else:
        print("Scenario-model scaffold is installed and valid.")
    print_line()


if __name__ == "__main__":
    main()
