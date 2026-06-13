"""
run_paid_simulator_phase2_pipeline_check.py

End-to-end Phase 2 scaffold pipeline checker for the Covered Call Strategy
Stress Test paid simulator.

This is an add-only diagnostic script. It does not modify dashboard code.
It runs the Phase 2 scaffold check scripts in sequence and reports whether
all expected scaffold outputs are present.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from datetime import datetime


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

CHECKS = [
    ("Phase 2 readiness", APP_DIR / "run_paid_simulator_phase2_readiness_check.py"),
    ("Scenario model", APP_DIR / "run_paid_simulator_scenario_model_check.py"),
    ("Scenario price paths", APP_DIR / "run_paid_simulator_price_path_check.py"),
    ("Option payoff", APP_DIR / "run_paid_simulator_option_payoff_check.py"),
    ("Scenario payoff", APP_DIR / "run_paid_simulator_scenario_payoff_check.py"),
    ("Scenario payoff report", APP_DIR / "run_paid_simulator_scenario_payoff_report_check.py"),
    ("Phase 2 vs v0 comparison", APP_DIR / "run_paid_simulator_phase2_v0_comparison_check.py"),
]

EXPECTED_OUTPUTS = [
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_price_paths_scaffold.csv",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_payoff_scaffold.csv",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_scaffold.csv",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "scenario_payoff_report_scaffold.csv",
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "scenario_payoff_report_scaffold.html",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase2_v0_comparison_scaffold.csv",
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2_v0_comparison_scaffold.html",
]

DOCS = [
    PROJECT_ROOT / "docs" / "paid_simulator_phase2_decision_plan.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2_modeling_scaffold.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2_scenario_model_scaffold.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2_price_path_scaffold.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2_option_payoff_scaffold.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2_scenario_payoff_scaffold.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2_scenario_payoff_report_adapter.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2_v0_comparison_adapter.md",
]


def line(char: str = "=", width: int = 88) -> None:
    print(char * width)


def run_check(label: str, script_path: Path) -> tuple[bool, str]:
    if not script_path.exists():
        return False, f"MISSING SCRIPT: {script_path}"

    completed = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    output = completed.stdout or ""
    if completed.stderr:
        output += "\n--- STDERR ---\n" + completed.stderr
    return completed.returncode == 0, output


def file_status(path: Path) -> str:
    return "FOUND" if path.exists() else "MISSING"


def main() -> int:
    line()
    print("Phase 2 scaffold pipeline check")
    line()
    print(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    all_ok = True
    outputs_by_check: list[tuple[str, bool, str]] = []

    line("-")
    print("Running Phase 2 check scripts")
    line("-")

    for label, script_path in CHECKS:
        ok, output = run_check(label, script_path)
        outputs_by_check.append((label, ok, output))
        status = "PASS" if ok else "REVIEW"
        print(f"{status:<10} {label:<32} {script_path}")
        if not ok:
            all_ok = False

    print()
    line("-")
    print("Expected Phase 2 scaffold outputs")
    line("-")
    for path in EXPECTED_OUTPUTS:
        status = file_status(path)
        print(f"{status:<10} {path}")
        if status != "FOUND":
            all_ok = False

    print()
    line("-")
    print("Phase 2 documentation")
    line("-")
    for path in DOCS:
        status = file_status(path)
        print(f"{status:<10} {path}")
        if status != "FOUND":
            all_ok = False

    print()
    if not all_ok:
        line("-")
        print("Failed check output tails")
        line("-")
        for label, ok, output in outputs_by_check:
            if not ok:
                print(f"\n[{label}] output tail")
                print("-" * 40)
                print(output[-2500:])

    print()
    line()
    if all_ok:
        print("Overall Phase 2 pipeline status: PASS")
        print("All Phase 2 scaffold checks passed and expected scaffold outputs are present.")
        return 0
    print("Overall Phase 2 pipeline status: REVIEW")
    print("One or more Phase 2 scaffold checks, outputs, or docs need attention.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
