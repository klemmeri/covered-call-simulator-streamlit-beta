"""
Readiness check for the Phase 2 scaffold viewer.
"""

from __future__ import annotations

from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent

EXPECTED_FILES = [
    ("Phase 2 viewer launcher", PROJECT_ROOT / "app" / "run_paid_simulator_phase2_viewer.py"),
    ("Phase 2 viewer app", PROJECT_ROOT / "app" / "paid_simulator" / "phase2_scaffold_viewer.py"),
    ("Phase 2 pipeline check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2_pipeline_check.py"),
    ("Scenario price paths CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_price_paths_scaffold.csv"),
    ("Option payoff CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_payoff_scaffold.csv"),
    ("Scenario payoff CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_scaffold.csv"),
    ("Scenario payoff report CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_report_scaffold.csv"),
    ("Scenario payoff report HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_payoff_report_scaffold.html"),
    ("Phase 2 vs v0 comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase2_v0_comparison_scaffold.csv"),
    ("Phase 2 vs v0 comparison HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2_v0_comparison_scaffold.html"),
]


def main() -> None:
    print("=" * 88)
    print("Phase 2 scaffold viewer readiness check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    missing = []
    for label, path in EXPECTED_FILES:
        status = "FOUND" if path.exists() else "MISSING"
        print(f"{status:<10} {label:<38} {path}")
        if not path.exists():
            missing.append((label, path))

    print()
    print("=" * 88)
    if missing:
        print("Overall Phase 2 viewer status: REVIEW")
        print("One or more files or scaffold outputs are missing.")
        raise SystemExit(1)
    print("Overall Phase 2 viewer status: PASS")
    print("The Phase 2 scaffold viewer files and expected outputs are present.")
    print("=" * 88)


if __name__ == "__main__":
    main()
