"""
run_paid_simulator_phase2_integration_readiness_check.py

Robust Phase 2 integration-readiness checker for the Covered Call Strategy
Stress Test paid simulator.

This script is intentionally read-only. It checks that the Phase 2 scaffold
modules, generated outputs, and documentation are present and that the CSV
outputs contain enough recognizable structure to support a developer-view
Phase 2 tab in the main dashboard.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

PAID_APP = PROJECT_ROOT / "app" / "paid_simulator"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"

MODULE_FILES = [
    PAID_APP / "scenario_model.py",
    PAID_APP / "scenario_price_paths.py",
    PAID_APP / "option_payoff_model.py",
    PAID_APP / "scenario_payoff_runner.py",
    PAID_APP / "scenario_payoff_report_adapter.py",
    PAID_APP / "phase2_v0_comparison_adapter.py",
    PAID_APP / "phase2_scaffold_viewer.py",
]

CHECK_SCRIPTS = [
    APP_DIR / "run_paid_simulator_phase2_readiness_check.py",
    APP_DIR / "run_paid_simulator_scenario_model_check.py",
    APP_DIR / "run_paid_simulator_price_path_check.py",
    APP_DIR / "run_paid_simulator_option_payoff_check.py",
    APP_DIR / "run_paid_simulator_scenario_payoff_check.py",
    APP_DIR / "run_paid_simulator_scenario_payoff_report_check.py",
    APP_DIR / "run_paid_simulator_phase2_v0_comparison_check.py",
    APP_DIR / "run_paid_simulator_phase2_pipeline_check.py",
    APP_DIR / "run_paid_simulator_phase2_viewer_check.py",
]

OUTPUT_FILES = [
    OUTPUT_TABLE_DIR / "scenario_price_paths_scaffold.csv",
    OUTPUT_TABLE_DIR / "option_payoff_scaffold.csv",
    OUTPUT_TABLE_DIR / "scenario_payoff_scaffold.csv",
    OUTPUT_TABLE_DIR / "scenario_payoff_report_scaffold.csv",
    OUTPUT_REPORT_DIR / "scenario_payoff_report_scaffold.html",
    OUTPUT_TABLE_DIR / "phase2_v0_comparison_scaffold.csv",
    OUTPUT_REPORT_DIR / "phase2_v0_comparison_scaffold.html",
]

DOC_FILES = [
    DOCS_DIR / "paid_simulator_phase2_decision_plan.md",
    DOCS_DIR / "paid_simulator_phase2_modeling_scaffold.md",
    DOCS_DIR / "paid_simulator_phase2_scenario_model_scaffold.md",
    DOCS_DIR / "paid_simulator_phase2_price_path_scaffold.md",
    DOCS_DIR / "paid_simulator_phase2_option_payoff_scaffold.md",
    DOCS_DIR / "paid_simulator_phase2_scenario_payoff_scaffold.md",
    DOCS_DIR / "paid_simulator_phase2_scenario_payoff_report_adapter.md",
    DOCS_DIR / "paid_simulator_phase2_v0_comparison_adapter.md",
    DOCS_DIR / "paid_simulator_phase2_pipeline_check.md",
    DOCS_DIR / "paid_simulator_phase2_scaffold_viewer.md",
]

CSV_STRUCTURE_RULES: dict[str, list[list[str]]] = {
    "scenario_price_paths_scaffold.csv": [
        ["scenario", "name", "label"],
        ["step", "day", "index"],
        ["price"],
    ],
    "option_payoff_scaffold.csv": [
        ["buy", "hold"],
        ["covered", "call"],
        ["relative", "minus", "difference"],
    ],
    "scenario_payoff_scaffold.csv": [
        ["scenario", "name", "label"],
        ["buy", "hold"],
        ["covered", "call"],
    ],
    "scenario_payoff_report_scaffold.csv": [
        ["scenario", "name", "label"],
        ["relative", "result", "minus", "difference"],
    ],
    "phase2_v0_comparison_scaffold.csv": [
        ["scenario", "name", "label"],
        ["phase2", "phase_2"],
        ["v0", "v0_1"],
    ],
}


def print_header(title: str) -> None:
    print("=" * 88)
    print(title)
    print("=" * 88)


def print_section(title: str) -> None:
    print("\n" + "-" * 88)
    print(title)
    print("-" * 88)


def path_status(path: Path, label: str | None = None) -> bool:
    exists = path.exists()
    status = "FOUND" if exists else "MISSING"
    display_label = label or path.name
    print(f"{status:<10} {display_label:<45} {path}")
    return exists


def read_csv_header(path: Path) -> list[str]:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.reader(file)
            return next(reader, [])
    except Exception:
        return []


def normalized_header(path: Path) -> list[str]:
    return [col.strip().lower().replace(" ", "_").replace("-", "_") for col in read_csv_header(path)]


def header_matches_any_token(header: list[str], tokens: list[str]) -> bool:
    joined = " ".join(header)
    return any(token.lower() in joined for token in tokens)


def check_csv_structure(path: Path) -> bool:
    if not path.exists():
        print(f"MISSING    {path.name:<45} {path}")
        return False

    header = normalized_header(path)
    if not header:
        print(f"REVIEW     {path.name:<45} CSV header could not be read")
        return False

    rules = CSV_STRUCTURE_RULES.get(path.name, [])
    failed_groups: list[str] = []
    for token_group in rules:
        if not header_matches_any_token(header, token_group):
            failed_groups.append("/".join(token_group))

    if failed_groups:
        print(f"REVIEW     {path.name:<45} Missing recognizable columns: {', '.join(failed_groups)}")
        print(f"           Available columns: {', '.join(header)}")
        return False

    # Nonempty row check.
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as file:
            row_count = max(sum(1 for _ in file) - 1, 0)
    except Exception:
        row_count = 0
    if row_count <= 0:
        print(f"REVIEW     {path.name:<45} CSV has no data rows")
        return False

    print(f"PASS       {path.name:<45} Rows: {row_count}; columns recognized")
    return True


def run_check_script(script_path: Path) -> tuple[bool, str]:
    if not script_path.exists():
        return False, f"Script missing: {script_path}"
    completed = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    output = (completed.stdout or "")
    if completed.stderr:
        output += "\n--- STDERR ---\n" + completed.stderr
    return completed.returncode == 0, output


def main() -> None:
    print_header("Phase 2 integration-readiness check")
    print(f"Project root: {PROJECT_ROOT}")

    problems: list[str] = []

    print_section("Phase 2 scaffold modules")
    for path in MODULE_FILES:
        if not path_status(path):
            problems.append(f"Missing module: {path}")

    print_section("Phase 2 checker scripts")
    for path in CHECK_SCRIPTS:
        if not path_status(path):
            problems.append(f"Missing checker script: {path}")

    print_section("Expected Phase 2 scaffold outputs")
    for path in OUTPUT_FILES:
        if not path_status(path):
            problems.append(f"Missing output: {path}")

    print_section("CSV structure checks")
    for csv_path in [p for p in OUTPUT_FILES if p.suffix.lower() == ".csv"]:
        if not check_csv_structure(csv_path):
            problems.append(f"CSV structure needs review: {csv_path}")

    print_section("Phase 2 documentation")
    for path in DOC_FILES:
        if not path_status(path):
            problems.append(f"Missing doc: {path}")

    print_section("Optional live checks")
    live_checks = [
        ("Phase 2 pipeline check", APP_DIR / "run_paid_simulator_phase2_pipeline_check.py"),
        ("Phase 2 viewer check", APP_DIR / "run_paid_simulator_phase2_viewer_check.py"),
    ]
    live_failures: list[tuple[str, str]] = []
    for label, script_path in live_checks:
        ok, output = run_check_script(script_path)
        status = "PASS" if ok else "REVIEW"
        print(f"{status:<10} {label:<45} {script_path.name}")
        if not ok:
            problems.append(f"Live check failed: {label}")
            live_failures.append((label, output[-3000:]))

    if live_failures:
        print_section("Failed live-check output tails")
        for label, tail in live_failures:
            print(f"\n[{label}] output tail")
            print("-" * 40)
            print(tail)

    print("\n" + "=" * 88)
    if problems:
        print("Overall Phase 2 integration-readiness status: REVIEW")
        print("One or more Phase 2 files, outputs, docs, or structure checks need attention.")
        print("\nItems needing attention:")
        for problem in problems:
            print(f"- {problem}")
        print("=" * 88)
        raise SystemExit(1)

    print("Overall Phase 2 integration-readiness status: PASS")
    print("Phase 2 scaffold outputs are ready for a developer-view-only dashboard tab.")
    print("=" * 88)


if __name__ == "__main__":
    main()
