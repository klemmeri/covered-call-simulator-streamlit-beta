"""
run_paid_simulator_phase2_v0_comparison_check.py

PyCharm runner for the Phase 2 vs v0 comparison scaffold.
"""

from __future__ import annotations

import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.paid_simulator.phase2_v0_comparison_adapter import (  # noqa: E402
    OUTPUT_CSV,
    OUTPUT_HTML,
    PHASE2_REPORT_CSV,
    V0_SCENARIO_CSV,
    run_adapter,
)


def print_line(label: str, path: Path) -> bool:
    exists = path.exists()
    status = "FOUND" if exists else "MISSING"
    print(f"{status:<10} {label:<45} {path}")
    return exists


def main() -> None:
    print("=" * 88)
    print("Phase 2 vs v0 comparison scaffold check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    print("Input files")
    print("-" * 88)
    v0_ok = print_line("v0 scenario comparison CSV", V0_SCENARIO_CSV)
    phase2_ok = print_line("Phase 2 scenario-payoff report CSV", PHASE2_REPORT_CSV)
    print()

    if not (v0_ok and phase2_ok):
        print("Overall Phase 2 vs v0 comparison status: REVIEW")
        print("Create the missing input files before running this adapter.")
        raise SystemExit(1)

    print("Running comparison adapter")
    print("-" * 88)
    try:
        status = run_adapter()
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED - adapter raised an error: {exc}")
        print("Overall Phase 2 vs v0 comparison status: REVIEW")
        raise SystemExit(1) from exc

    print(status.message)
    print(f"Rows written: {status.row_count}")
    print()

    print("Output files")
    print("-" * 88)
    out_csv_ok = print_line("Phase 2 vs v0 comparison CSV", OUTPUT_CSV)
    out_html_ok = print_line("Phase 2 vs v0 comparison HTML", OUTPUT_HTML)
    print()

    if status.row_count > 0 and out_csv_ok and out_html_ok:
        print("=" * 88)
        print("Overall Phase 2 vs v0 comparison status: PASS")
        print("The comparison scaffold was created successfully.")
        print("=" * 88)
    else:
        print("Overall Phase 2 vs v0 comparison status: REVIEW")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
