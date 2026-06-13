"""
run_paid_simulator_premium_aware_payoff_check.py

PyCharm runner/checker for the Phase 2B premium-aware payoff scaffold.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

OUTPUT_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv"
OUTPUT_HTML = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_aware_payoff_scaffold.html"
PRICE_PATHS_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_price_paths_scaffold.csv"
OPTION_PREMIUM_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv"


def print_header(title: str) -> None:
    print("=" * 88)
    print(title)
    print("=" * 88)


def print_section(title: str) -> None:
    print("\n" + "-" * 88)
    print(title)
    print("-" * 88)


def check_file(label: str, path: Path) -> bool:
    exists = path.exists()
    status = "FOUND" if exists else "MISSING"
    print(f"{status:<10} {label:<42} {path}")
    return exists


def main() -> None:
    print_header("Phase 2B premium-aware payoff scaffold check")
    print(f"Project root: {PROJECT_ROOT}")

    print_section("Required inputs")
    ok = True
    ok &= check_file("Scenario price paths CSV", PRICE_PATHS_CSV)
    ok &= check_file("Option premium scaffold CSV", OPTION_PREMIUM_CSV)

    if not ok:
        print("\nOverall premium-aware payoff status: REVIEW")
        print("One or more required input files are missing.")
        raise SystemExit(1)

    print_section("Running premium-aware payoff scaffold")
    try:
        from app.paid_simulator.premium_aware_payoff_runner import run_premium_aware_payoff

        df = run_premium_aware_payoff()
        print(f"Rows created: {len(df)}")
        print(df.to_string(index=False))
    except Exception as exc:  # noqa: BLE001 - checker should print clear failure details.
        print(f"FAILED - scaffold run raised an error: {exc}")
        print("\nOverall premium-aware payoff status: REVIEW")
        raise SystemExit(1)

    print_section("Expected outputs")
    ok &= check_file("Premium-aware payoff CSV", OUTPUT_CSV)
    ok &= check_file("Premium-aware payoff HTML", OUTPUT_HTML)

    print_section("Output structure")
    try:
        out_df = pd.read_csv(OUTPUT_CSV)
        required_columns = [
            "scenario_name",
            "scenario_display_name",
            "starting_price",
            "final_price",
            "call_strike",
            "call_premium",
            "buy_and_hold_pl",
            "covered_call_pl",
            "covered_call_minus_buy_hold",
            "assigned",
            "interpretation",
        ]
        missing = [col for col in required_columns if col not in out_df.columns]
        if missing:
            ok = False
            print("MISSING COLUMNS")
            for col in missing:
                print(f"  {col}")
        else:
            print("All required columns are present.")
        if len(out_df) < 5:
            ok = False
            print(f"Expected at least 5 rows; found {len(out_df)}.")
        else:
            print(f"Rows: {len(out_df)}")
    except Exception as exc:  # noqa: BLE001
        ok = False
        print(f"FAILED - could not inspect output CSV: {exc}")

    print("\n" + "=" * 88)
    if ok:
        print("Overall premium-aware payoff status: PASS")
        print("The Phase 2B premium-aware payoff scaffold produced the expected outputs.")
        print("=" * 88)
        raise SystemExit(0)

    print("Overall premium-aware payoff status: REVIEW")
    print("One or more premium-aware payoff checks need attention.")
    print("=" * 88)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
