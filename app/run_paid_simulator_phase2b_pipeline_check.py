"""
run_paid_simulator_phase2b_pipeline_check.py

End-to-end checker for the Phase 2B premium-model scaffold.

Run this file from PyCharm. It executes the Phase 2B premium-model checks
in sequence and verifies that the expected premium-aware outputs exist.

This script is intentionally add-only and does not modify the main paid
simulator dashboard.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

CHECK_SCRIPTS = [
    ("Option premium model", PROJECT_ROOT / "app" / "run_paid_simulator_option_premium_check.py"),
    ("Premium-aware payoff", PROJECT_ROOT / "app" / "run_paid_simulator_premium_aware_payoff_check.py"),
    ("Premium vs scaffold comparison", PROJECT_ROOT / "app" / "run_paid_simulator_premium_vs_scaffold_check.py"),
    ("Phase 2B premium viewer", PROJECT_ROOT / "app" / "run_paid_simulator_phase2b_premium_viewer_check.py"),
]

EXPECTED_OUTPUTS = [
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv",
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_aware_payoff_scaffold.html",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_vs_scaffold_comparison.csv",
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_vs_scaffold_comparison.html",
]

EXPECTED_MODULES = [
    PROJECT_ROOT / "app" / "paid_simulator" / "option_premium_model.py",
    PROJECT_ROOT / "app" / "paid_simulator" / "premium_aware_payoff_runner.py",
    PROJECT_ROOT / "app" / "paid_simulator" / "premium_vs_scaffold_comparison.py",
    PROJECT_ROOT / "app" / "paid_simulator" / "phase2b_premium_viewer.py",
]

EXPECTED_DOCS = [
    PROJECT_ROOT / "docs" / "paid_simulator_phase2_option_premium_model_scaffold.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2b_premium_aware_payoff.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2b_premium_vs_scaffold_comparison.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2b_premium_viewer.md",
    PROJECT_ROOT / "docs" / "paid_simulator_phase2b_pipeline_check.md",
]


def print_rule(title: str) -> None:
    print("\n" + title)
    print("-" * 88)


def file_status(path: Path) -> bool:
    exists = path.exists()
    print(f"{'FOUND' if exists else 'MISSING':<10} {path}")
    return exists


def count_csv_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.reader(file)
            rows = list(reader)
        if not rows:
            return 0
        return max(len(rows) - 1, 0)
    except Exception:
        return None


def run_check(label: str, script_path: Path) -> tuple[bool, str]:
    if not script_path.exists():
        return False, f"Script not found: {script_path}"

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


def main() -> None:
    print("=" * 88)
    print("Phase 2B premium-model pipeline check")
    print("=" * 88)
    print(f"Project root: {PROJECT_ROOT}")

    overall_ok = True
    failed_outputs: list[tuple[str, str]] = []

    print_rule("Required Phase 2B modules")
    for path in EXPECTED_MODULES:
        overall_ok = file_status(path) and overall_ok

    print_rule("Phase 2B documentation")
    for path in EXPECTED_DOCS:
        overall_ok = file_status(path) and overall_ok

    print_rule("Running Phase 2B checks")
    for label, script_path in CHECK_SCRIPTS:
        ok, output = run_check(label, script_path)
        print(f"{'PASS' if ok else 'FAILED':<10} {label:<35} {script_path.name}")
        if not ok:
            overall_ok = False
            failed_outputs.append((label, output[-2500:]))

    print_rule("Expected Phase 2B outputs")
    for path in EXPECTED_OUTPUTS:
        found = file_status(path)
        overall_ok = found and overall_ok
        if path.suffix.lower() == ".csv" and found:
            row_count = count_csv_rows(path)
            if row_count is None:
                print(f"{'REVIEW':<10} Could not count CSV rows: {path.name}")
                overall_ok = False
            elif row_count <= 0:
                print(f"{'REVIEW':<10} CSV has no data rows: {path.name}")
                overall_ok = False
            else:
                print(f"{'ROWS':<10} {path.name}: {row_count}")

    if failed_outputs:
        print_rule("Failed check output tails")
        for label, output in failed_outputs:
            print(f"\n[{label}] output tail")
            print("-" * 40)
            print(output)

    print("\n" + "=" * 88)
    if overall_ok:
        print("Overall Phase 2B pipeline status: PASS")
        print("The premium-model scaffold, premium-aware payoff, comparison, and viewer checks are passing.")
        exit_code = 0
    else:
        print("Overall Phase 2B pipeline status: REVIEW")
        print("One or more Phase 2B files, checks, outputs, or docs need attention.")
        exit_code = 1
    print("=" * 88)
    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
