"""
run_paid_simulator_phase2_checkpoint_check.py

Checkpoint verifier for the Covered Call Strategy Stress Test Phase 2 scaffold.

This script is intentionally read-only. It checks that the Phase 2 scaffold files,
outputs, viewer, pipeline check, integration-readiness check, and dashboard-tab
support files are present after the Phase 2 scaffold milestone.
"""

from __future__ import annotations

from pathlib import Path
import csv


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

REQUIRED_FILES = [
    ("Scenario model scaffold", PROJECT_ROOT / "app" / "paid_simulator" / "scenario_model.py"),
    ("Scenario price-path scaffold", PROJECT_ROOT / "app" / "paid_simulator" / "scenario_price_paths.py"),
    ("Option payoff scaffold", PROJECT_ROOT / "app" / "paid_simulator" / "option_payoff_model.py"),
    ("Scenario payoff runner", PROJECT_ROOT / "app" / "paid_simulator" / "scenario_payoff_runner.py"),
    ("Scenario payoff report adapter", PROJECT_ROOT / "app" / "paid_simulator" / "scenario_payoff_report_adapter.py"),
    ("Phase 2 vs v0 comparison adapter", PROJECT_ROOT / "app" / "paid_simulator" / "phase2_v0_comparison_adapter.py"),
    ("Phase 2 scaffold viewer", PROJECT_ROOT / "app" / "paid_simulator" / "phase2_scaffold_viewer.py"),
    ("Phase 2 pipeline check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2_pipeline_check.py"),
    ("Phase 2 integration-readiness check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2_integration_readiness_check.py"),
    ("Phase 2 dashboard-tab check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2_dashboard_tab_check.py"),
    ("Main dashboard app", PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"),
    ("Main dashboard launcher", PROJECT_ROOT / "app" / "run_paid_simulator_form.py"),
]

EXPECTED_OUTPUTS = [
    ("Scenario price paths CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_price_paths_scaffold.csv"),
    ("Option payoff CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_payoff_scaffold.csv"),
    ("Scenario payoff CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_scaffold.csv"),
    ("Scenario payoff report CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_report_scaffold.csv"),
    ("Scenario payoff report HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_payoff_report_scaffold.html"),
    ("Phase 2 vs v0 comparison CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase2_v0_comparison_scaffold.csv"),
    ("Phase 2 vs v0 comparison HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2_v0_comparison_scaffold.html"),
]

DOCS = [
    ("Phase 2 decision plan", PROJECT_ROOT / "docs" / "paid_simulator_phase2_decision_plan.md"),
    ("Phase 2 modeling scaffold", PROJECT_ROOT / "docs" / "paid_simulator_phase2_modeling_scaffold.md"),
    ("Phase 2 scenario model scaffold", PROJECT_ROOT / "docs" / "paid_simulator_phase2_scenario_model_scaffold.md"),
    ("Phase 2 price-path scaffold", PROJECT_ROOT / "docs" / "paid_simulator_phase2_price_path_scaffold.md"),
    ("Phase 2 option payoff scaffold", PROJECT_ROOT / "docs" / "paid_simulator_phase2_option_payoff_scaffold.md"),
    ("Phase 2 scenario payoff scaffold", PROJECT_ROOT / "docs" / "paid_simulator_phase2_scenario_payoff_scaffold.md"),
    ("Phase 2 scenario payoff report adapter", PROJECT_ROOT / "docs" / "paid_simulator_phase2_scenario_payoff_report_adapter.md"),
    ("Phase 2 vs v0 comparison adapter", PROJECT_ROOT / "docs" / "paid_simulator_phase2_v0_comparison_adapter.md"),
    ("Phase 2 pipeline check", PROJECT_ROOT / "docs" / "paid_simulator_phase2_pipeline_check.md"),
    ("Phase 2 scaffold viewer", PROJECT_ROOT / "docs" / "paid_simulator_phase2_scaffold_viewer.md"),
    ("Phase 2 integration readiness", PROJECT_ROOT / "docs" / "paid_simulator_phase2_integration_readiness.md"),
    ("Phase 2 dashboard tab", PROJECT_ROOT / "docs" / "paid_simulator_phase2_dashboard_tab.md"),
    ("Phase 2 checkpoint summary", PROJECT_ROOT / "docs" / "paid_simulator_phase2_checkpoint_summary.md"),
]

CSV_MIN_ROWS = {
    "scenario_price_paths_scaffold.csv": 5,
    "option_payoff_scaffold.csv": 1,
    "scenario_payoff_scaffold.csv": 5,
    "scenario_payoff_report_scaffold.csv": 5,
    "phase2_v0_comparison_scaffold.csv": 1,
}


def print_header(title: str) -> None:
    print("\n" + title)
    print("-" * 88)


def check_file(label: str, path: Path) -> bool:
    exists = path.exists()
    print(f"{'FOUND' if exists else 'MISSING':<10} {label:<42} {path}")
    return exists


def count_csv_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        return max(len(rows) - 1, 0)
    except Exception:
        return None


def main() -> None:
    print("=" * 88)
    print("Phase 2 scaffold checkpoint check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")

    ok = True

    print_header("Required Phase 2 source and runner files")
    for label, path in REQUIRED_FILES:
        ok = check_file(label, path) and ok

    print_header("Expected Phase 2 generated outputs")
    for label, path in EXPECTED_OUTPUTS:
        ok = check_file(label, path) and ok

    print_header("Phase 2 documentation")
    for label, path in DOCS:
        ok = check_file(label, path) and ok

    print_header("CSV row checks")
    for filename, min_rows in CSV_MIN_ROWS.items():
        path = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / filename
        rows = count_csv_rows(path)
        if rows is None:
            print(f"REVIEW     {filename:<42} could not be read")
            ok = False
        elif rows < min_rows:
            print(f"REVIEW     {filename:<42} rows={rows}, expected at least {min_rows}")
            ok = False
        else:
            print(f"PASS       {filename:<42} rows={rows}")

    print("\n" + "=" * 88)
    if ok:
        print("Overall Phase 2 checkpoint status: PASS")
        print("The Phase 2 scaffold milestone files, outputs, and docs are present.")
    else:
        print("Overall Phase 2 checkpoint status: REVIEW")
        print("One or more Phase 2 checkpoint items need attention.")
    print("=" * 88)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
