"""
run_paid_simulator_scenario_assumptions_check.py

PyCharm runner/checker for the Phase 2 scenario-assumptions scaffold.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent
OUTPUT_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "tables"
    / "paid_simulator"
    / "scenario_assumptions_scaffold.csv"
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def print_rule(title: str = "") -> None:
    if title:
        print("\n" + title)
    print("-" * 88)


def main() -> None:
    print("=" * 88)
    print("Phase 2 scenario-assumptions scaffold check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")

    try:
        from app.paid_simulator import scenario_assumptions as module
    except Exception as exc:  # noqa: BLE001
        print(f"\nFAILED - could not import scenario assumptions module: {exc}")
        raise SystemExit(1)

    getter_names = [
        "get_default_scenario_assumptions",
        "build_default_scenario_assumptions",
        "build_scenario_assumptions",
        "get_scenario_assumptions",
    ]
    getter = None
    for name in getter_names:
        candidate = getattr(module, name, None)
        if callable(candidate):
            getter = candidate
            break

    if getter is None:
        print("\nFAILED - no recognized scenario-assumption getter was found.")
        raise SystemExit(1)

    try:
        assumptions = getter()
        if not assumptions:
            print("\nFAILED - scenario-assumption getter returned no assumptions.")
            raise SystemExit(1)

        if hasattr(module, "assumptions_to_dataframe"):
            df = module.assumptions_to_dataframe(assumptions)
        else:
            df = pd.DataFrame([getattr(item, "__dict__", dict(item)) for item in assumptions])

        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False)
    except Exception as exc:  # noqa: BLE001
        print(f"\nFAILED - could not build or write scenario assumptions: {exc}")
        raise SystemExit(1)

    required_columns = [
        "scenario_name",
        "scenario_display_name",
        "modeled_total_return_percent",
        "realized_volatility_label",
        "implied_volatility_bias",
        "skew_bias",
        "path_shape",
        "covered_call_profile",
        "plain_english_interpretation",
    ]

    print_rule("Generated scenario assumptions")
    print(f"Output path: {OUTPUT_PATH}")
    print(f"Rows:        {len(df)}")
    print(f"Columns:     {', '.join(map(str, df.columns))}")

    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print("\nFAILED - missing required columns:")
        for col in missing:
            print(f"  - {col}")
        raise SystemExit(1)

    if len(df) < 5:
        print("\nFAILED - expected at least five scenario assumptions.")
        raise SystemExit(1)

    print_rule("Scenario assumptions table")
    display_cols = [
        "scenario_name",
        "scenario_display_name",
        "modeled_total_return_percent",
        "path_shape",
        "realized_volatility_label",
    ]
    print(df[display_cols].to_string(index=False))

    print("\n" + "=" * 88)
    print("Overall scenario-assumptions scaffold status: PASS")
    print("Scenario assumptions were generated and written successfully.")
    print("=" * 88)


if __name__ == "__main__":
    main()
