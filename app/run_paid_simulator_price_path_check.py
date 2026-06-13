"""
run_paid_simulator_price_path_check.py

PyCharm runner for the Phase 2 price-path scaffold.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_price_paths_scaffold.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_scenarios() -> list[Any]:
    from app.paid_simulator import scenario_model

    candidate_names = [
        "build_default_scenarios",
        "get_default_scenarios",
        "default_scenarios",
        "build_scenarios",
        "get_scenarios",
    ]

    for name in candidate_names:
        func = getattr(scenario_model, name, None)
        if callable(func):
            scenarios = func()
            return list(scenarios)

    for attr in ["DEFAULT_SCENARIOS", "SCENARIOS", "SCENARIO_DEFINITIONS"]:
        value = getattr(scenario_model, attr, None)
        if value is not None:
            return list(value.values()) if isinstance(value, dict) else list(value)

    raise RuntimeError("Could not find default scenarios in scenario_model.py")


def main() -> None:
    print("=" * 88)
    print("Paid simulator Phase 2 price-path scaffold check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    try:
        from app.paid_simulator.scenario_price_paths import generate_all_price_paths
    except Exception as exc:
        print(f"FAILED - could not import scenario_price_paths: {exc}")
        print("Overall price-path scaffold status: REVIEW")
        raise SystemExit(1)

    try:
        scenarios = _load_scenarios()
        print(f"Loaded scenarios: {len(scenarios)}")
    except Exception as exc:
        print(f"FAILED - could not load scenarios: {exc}")
        print("Overall price-path scaffold status: REVIEW")
        raise SystemExit(1)

    try:
        df = generate_all_price_paths(scenarios=scenarios, starting_price=545.25, steps=30)
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUTPUT_PATH, index=False)
    except Exception as exc:
        print(f"FAILED - could not generate price paths: {exc}")
        print("Overall price-path scaffold status: REVIEW")
        raise SystemExit(1)

    print(f"Rows written: {len(df)}")
    print(f"Output path: {OUTPUT_PATH}")
    print()

    required_columns = [
        "scenario_name",
        "scenario_display_name",
        "step",
        "starting_price",
        "price",
        "final_target_price",
        "modeled_return_percent",
        "path_shape",
    ]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        print("FAILED - missing required columns:")
        for col in missing:
            print(f"  {col}")
        print("Overall price-path scaffold status: REVIEW")
        raise SystemExit(1)

    if df.empty:
        print("FAILED - generated DataFrame is empty")
        print("Overall price-path scaffold status: REVIEW")
        raise SystemExit(1)

    unique_scenarios = df["scenario_name"].nunique()
    if unique_scenarios < 1:
        print("FAILED - no unique scenarios found")
        print("Overall price-path scaffold status: REVIEW")
        raise SystemExit(1)

    print("Preview")
    print("-" * 88)
    preview_cols = ["scenario_display_name", "step", "price", "modeled_return_percent", "path_shape"]
    print(df[preview_cols].head(10).to_string(index=False))
    print()
    print("=" * 88)
    print("Overall price-path scaffold status: PASS")
    print("Phase 2 scenario price-path scaffold generated the expected CSV output.")
    print("=" * 88)


if __name__ == "__main__":
    main()
