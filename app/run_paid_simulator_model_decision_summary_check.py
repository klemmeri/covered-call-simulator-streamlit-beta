"""
run_paid_simulator_model_decision_summary_check.py

Runs and verifies the Phase 2F model-decision summary.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"

if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

from paid_simulator.model_decision_summary import run_model_decision_summary


REQUIRED_INPUTS = [
    TABLE_DIR / "option_premium_scaffold.csv",
    TABLE_DIR / "premium_aware_payoff_scaffold.csv",
    TABLE_DIR / "premium_vs_scaffold_comparison.csv",
    TABLE_DIR / "premium_model_validation_scaffold.csv",
    TABLE_DIR / "premium_model_tuning_recommendations.csv",
    TABLE_DIR / "premium_model_adjusted_premiums.csv",
    TABLE_DIR / "adjusted_premium_payoff_comparison.csv",
]

EXPECTED_OUTPUTS = [
    TABLE_DIR / "model_decision_summary.csv",
    REPORT_DIR / "model_decision_summary.html",
    REPORT_DIR / "model_decision_summary.txt",
]

CHECK_REPORT = REPORT_DIR / "phase2f_model_decision_summary_check_report.txt"


def print_section(title: str) -> None:
    print("\n" + title)
    print("-" * 96)


def file_status(path: Path) -> tuple[bool, int]:
    if not path.exists():
        return False, 0
    if path.suffix.lower() == ".csv":
        try:
            return True, len(pd.read_csv(path))
        except Exception:
            return True, -1
    return True, path.stat().st_size


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    def record(text: str = "") -> None:
        print(text)
        lines.append(text)

    record("=" * 96)
    record("Phase 2F model-decision summary check")
    record("=" * 96)
    record(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    record(f"Project root: {PROJECT_ROOT}")

    ok = True

    print_section("Required input files")
    lines.append("")
    lines.append("Required input files")
    lines.append("-" * 96)
    for path in REQUIRED_INPUTS:
        exists, rows = file_status(path)
        status = "FOUND" if exists else "MISSING"
        if not exists or rows == 0 or rows == -1:
            ok = False
            status = "REVIEW" if exists else "MISSING"
        message = f"{status:<10} rows={rows:<5} {path}"
        record(message)

    record("\nRunning Phase 2F model-decision summary...")
    try:
        df = run_model_decision_summary()
        record(f"Generated summary rows: {len(df)}")
        if df.empty:
            ok = False
    except Exception as exc:
        ok = False
        record(f"ERROR: Phase 2F model-decision summary failed: {exc}")
        df = pd.DataFrame()

    print_section("Expected output files")
    lines.append("")
    lines.append("Expected output files")
    lines.append("-" * 96)
    for path in EXPECTED_OUTPUTS:
        exists, rows_or_size = file_status(path)
        status = "FOUND" if exists else "MISSING"
        if not exists or rows_or_size == 0 or rows_or_size == -1:
            ok = False
            status = "REVIEW" if exists else "MISSING"
        if path.suffix.lower() == ".csv":
            message = f"{status:<10} rows={rows_or_size:<5} {path}"
        else:
            message = f"{status:<10} size={rows_or_size:<5} {path}"
        record(message)

    print_section("Required output columns")
    lines.append("")
    lines.append("Required output columns")
    lines.append("-" * 96)
    required_columns = [
        "scenario",
        "original_premium",
        "adjusted_premium",
        "premium_change",
        "premium_aware_relative_result",
        "adjusted_relative_result",
        "adjusted_minus_original",
        "validation_status",
        "tuning_status",
        "model_decision",
        "decision_reason",
    ]
    for col in required_columns:
        if col in df.columns:
            record(f"PASS       column '{col}'")
        else:
            ok = False
            record(f"MISSING    column '{col}'")

    print_section("Overall result")
    lines.append("")
    lines.append("Overall result")
    lines.append("-" * 96)
    if ok:
        record("Overall Phase 2F model-decision summary status: PASS")
        exit_code = 0
    else:
        record("Overall Phase 2F model-decision summary status: REVIEW")
        exit_code = 1

    CHECK_REPORT.write_text("\n".join(lines), encoding="utf-8")
    record(f"\nSaved check report: {CHECK_REPORT}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
