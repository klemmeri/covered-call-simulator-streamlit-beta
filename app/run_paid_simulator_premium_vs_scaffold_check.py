"""
run_paid_simulator_premium_vs_scaffold_check.py

PyCharm runner for the Phase 2B premium-aware versus older Phase 2 payoff
comparison scaffold.
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

TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

OLD_PAYOFF_PATH = TABLE_DIR / "scenario_payoff_scaffold.csv"
PREMIUM_AWARE_PATH = TABLE_DIR / "premium_aware_payoff_scaffold.csv"
COMPARISON_CSV_PATH = TABLE_DIR / "premium_vs_scaffold_comparison.csv"
COMPARISON_HTML_PATH = REPORT_DIR / "premium_vs_scaffold_comparison.html"
DOC_PATH = PROJECT_ROOT / "docs" / "paid_simulator_phase2b_premium_vs_scaffold_comparison.md"


def print_header(title: str) -> None:
    print("=" * 88)
    print(title)
    print("=" * 88)


def print_section(title: str) -> None:
    print("\n" + "-" * 88)
    print(title)
    print("-" * 88)


def print_file_status(label: str, path: Path) -> bool:
    exists = path.exists()
    status = "FOUND" if exists else "MISSING"
    print(f"{status:<10} {label:<42} {path}")
    return exists


def main() -> None:
    print_header("Phase 2B premium-aware vs old payoff scaffold check")
    print(f"Project root: {PROJECT_ROOT}")

    ok = True

    print_section("Required input files")
    ok &= print_file_status("Old Phase 2 payoff scaffold CSV", OLD_PAYOFF_PATH)
    ok &= print_file_status("Premium-aware payoff CSV", PREMIUM_AWARE_PATH)
    ok &= print_file_status("Comparison documentation", DOC_PATH)

    print_section("Running comparison adapter")
    try:
        from app.paid_simulator.premium_vs_scaffold_comparison import build_premium_vs_scaffold_comparison

        result = build_premium_vs_scaffold_comparison()
        print("PASS - comparison adapter ran successfully.")
        print(f"Rows compared:          {result.row_count}")
        print(f"Premium-aware better:   {result.premium_better_count}")
        print(f"Premium-aware worse:    {result.premium_worse_count}")
        print(f"Effectively unchanged:  {result.premium_same_count}")
    except Exception as exc:  # noqa: BLE001 - checker should print actionable failure.
        print(f"FAILED - comparison adapter raised an error: {exc}")
        ok = False

    print_section("Expected output files")
    ok &= print_file_status("Premium vs scaffold comparison CSV", COMPARISON_CSV_PATH)
    ok &= print_file_status("Premium vs scaffold comparison HTML", COMPARISON_HTML_PATH)

    if COMPARISON_CSV_PATH.exists():
        try:
            df = pd.read_csv(COMPARISON_CSV_PATH)
            print_section("Output CSV summary")
            print(f"Rows excluding header: {len(df)}")
            required_cols = [
                "scenario",
                "old_phase2_relative_result",
                "premium_aware_relative_result",
                "premium_minus_old",
                "comparison_classification",
            ]
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                print(f"MISSING COLUMNS: {', '.join(missing_cols)}")
                ok = False
            else:
                print("Required comparison columns: PASS")
            if len(df) == 0:
                print("No comparison rows were produced.")
                ok = False
        except Exception as exc:  # noqa: BLE001
            print(f"Could not inspect comparison CSV: {exc}")
            ok = False

    print("\n" + "=" * 88)
    if ok:
        print("Overall premium-vs-scaffold comparison status: PASS")
        print("The premium-aware payoff output can be compared against the older Phase 2 scaffold.")
        exit_code = 0
    else:
        print("Overall premium-vs-scaffold comparison status: REVIEW")
        print("One or more comparison files, outputs, or structure checks need attention.")
        exit_code = 1
    print("=" * 88)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
