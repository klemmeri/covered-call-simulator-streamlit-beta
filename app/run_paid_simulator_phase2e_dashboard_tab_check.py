"""
run_paid_simulator_phase2e_dashboard_tab_check.py

Checks that the Developer-view-only Phase 2E premium-adjustment tab is
installed in the main paid-simulator dashboard and that the key Phase 2E
outputs are present.
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

REQUIRED_FILES = [
    ("Main dashboard", DASHBOARD_PATH),
    ("Phase 2E adjustment module", PROJECT_ROOT / "app" / "paid_simulator" / "premium_model_adjustment.py"),
    ("Phase 2E adjusted payoff comparison module", PROJECT_ROOT / "app" / "paid_simulator" / "adjusted_premium_payoff_comparison.py"),
    ("Phase 2E adjustment viewer", PROJECT_ROOT / "app" / "paid_simulator" / "phase2e_adjustment_viewer.py"),
    ("Phase 2E adjustment pipeline checker", PROJECT_ROOT / "app" / "run_paid_simulator_phase2e_adjustment_pipeline_check.py"),
    ("Phase 2E adjusted premiums CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_adjusted_premiums.csv"),
    ("Phase 2E adjusted payoff comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "adjusted_premium_payoff_comparison.csv"),
    ("Phase 2E adjustment summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_adjustment_summary.txt"),
    ("Phase 2E adjusted payoff summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "adjusted_premium_payoff_summary.txt"),
]

REQUIRED_MARKERS = [
    "Phase 2E adjustment",
    "show_phase2e_adjustment_tab",
    "PHASE2E_ADJUSTED_PREMIUMS_PATH",
    "PHASE2E_ADJUSTED_PAYOFF_COMPARISON_PATH",
    "run_paid_simulator_phase2e_adjustment_pipeline_check.py",
    "phase2e_adjustment_viewer",
]


def print_line(label: str, status: str, detail: str = "") -> None:
    print(f"{status:<10} {label:<55} {detail}")


def main() -> int:
    print("=" * 96)
    print("Phase 2E premium-adjustment dashboard-tab check")
    print("=" * 96)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    all_ok = True

    print("Required files")
    print("-" * 96)
    for label, path in REQUIRED_FILES:
        if path.exists():
            print_line(label, "FOUND", str(path))
        else:
            print_line(label, "MISSING", str(path))
            all_ok = False
    print()

    print("Dashboard source markers")
    print("-" * 96)
    if DASHBOARD_PATH.exists():
        text = DASHBOARD_PATH.read_text(encoding="utf-8", errors="replace")
        for marker in REQUIRED_MARKERS:
            if marker in text:
                print_line(f"Marker '{marker}'", "PASS")
            else:
                print_line(f"Marker '{marker}'", "REVIEW")
                all_ok = False
    else:
        print_line("Dashboard source", "MISSING", str(DASHBOARD_PATH))
        all_ok = False
    print()

    print("=" * 96)
    if all_ok:
        print("PASS: The Developer-view-only Phase 2E adjustment tab is installed and the Phase 2E outputs are present.")
        print("=" * 96)
        return 0

    print("REVIEW: One or more Phase 2E dashboard-tab items need attention.")
    print("=" * 96)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
