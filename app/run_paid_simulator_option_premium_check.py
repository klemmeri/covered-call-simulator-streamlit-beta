"""
run_paid_simulator_option_premium_check.py

PyCharm runner for the Phase 2B option-premium model scaffold.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent
OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def print_header(title: str) -> None:
    print("=" * 88)
    print(title)
    print("=" * 88)


def print_section(title: str) -> None:
    print()
    print(title)
    print("-" * 88)


def main() -> None:
    print_header("Phase 2B option-premium scaffold check")
    print(f"Project root: {PROJECT_ROOT}")

    ok = True

    print_section("Import check")
    try:
        from app.paid_simulator.option_premium_model import (
            build_option_premium_results,
            export_option_premium_results,
        )
        print("PASS - option_premium_model imported")
    except Exception as exc:
        print(f"FAILED - could not import option premium module: {exc}")
        raise SystemExit(1)

    print_section("Build premium estimates")
    try:
        results = build_option_premium_results(
            underlying_price=545.25,
            target_delta=0.30,
            days_to_expiration=30,
            risk_free_rate=0.045,
            dividend_yield=0.0,
        )
        print(f"Rows generated: {len(results)}")
        if not results:
            print("FAILED - no premium rows generated")
            ok = False
        else:
            for row in results:
                print(
                    f"{row.scenario_name:<20} "
                    f"strike={row.estimated_strike:>8.2f} "
                    f"premium={row.estimated_call_premium:>8.2f} "
                    f"delta={row.estimated_call_delta:>6.3f} "
                    f"iv={row.implied_volatility:>6.3f}"
                )
    except Exception as exc:
        print(f"FAILED - premium build raised an error: {exc}")
        raise SystemExit(1)

    print_section("CSV export")
    try:
        export_option_premium_results(
            OUTPUT_PATH,
            underlying_price=545.25,
            target_delta=0.30,
            days_to_expiration=30,
            risk_free_rate=0.045,
            dividend_yield=0.0,
        )
        print(f"WROTE - {OUTPUT_PATH}")
    except Exception as exc:
        print(f"FAILED - CSV export raised an error: {exc}")
        raise SystemExit(1)

    print_section("CSV structure check")
    if not OUTPUT_PATH.exists():
        print("FAILED - output CSV missing")
        ok = False
    else:
        with OUTPUT_PATH.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            columns = reader.fieldnames or []
        required = [
            "scenario_name",
            "display_name",
            "underlying_price",
            "target_delta",
            "estimated_strike",
            "days_to_expiration",
            "implied_volatility",
            "estimated_call_premium",
            "estimated_call_delta",
            "moneyness_percent",
        ]
        missing = [col for col in required if col not in columns]
        print(f"Rows excluding header: {len(rows)}")
        print(f"Columns: {', '.join(columns)}")
        if missing:
            print(f"FAILED - missing required columns: {missing}")
            ok = False
        if len(rows) < 5:
            print("FAILED - expected at least 5 scenario rows")
            ok = False

    print()
    print("=" * 88)
    if ok:
        print("Overall option-premium scaffold status: PASS")
        print("The Phase 2B option-premium model scaffold is installed and writing output.")
        print("=" * 88)
        raise SystemExit(0)

    print("Overall option-premium scaffold status: REVIEW")
    print("One or more option-premium scaffold checks need attention.")
    print("=" * 88)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
