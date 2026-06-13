"""
run_paid_simulator_adjusted_premium_payoff_comparison_check.py

Runner/checker for the Phase 2E adjusted-premium payoff comparison scaffold.

This script runs the adjusted-payoff comparison module, verifies expected files
and row counts, and writes a plain-text check report.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

MODULE_PATH = PAID_SIMULATOR_DIR / "adjusted_premium_payoff_comparison.py"
PRICE_PATHS_CSV = OUTPUT_TABLE_DIR / "scenario_price_paths_scaffold.csv"
ADJUSTED_PREMIUM_CSV = OUTPUT_TABLE_DIR / "premium_model_adjusted_premiums.csv"
PRIOR_PAYOFF_CSV = OUTPUT_TABLE_DIR / "premium_aware_payoff_scaffold.csv"
OUTPUT_CSV = OUTPUT_TABLE_DIR / "adjusted_premium_payoff_comparison.csv"
OUTPUT_HTML = OUTPUT_REPORT_DIR / "adjusted_premium_payoff_comparison.html"
OUTPUT_SUMMARY = OUTPUT_REPORT_DIR / "adjusted_premium_payoff_summary.txt"
DOC_PATH = DOCS_DIR / "paid_simulator_phase2e_adjusted_premium_payoff_comparison.md"
CHECK_REPORT = OUTPUT_REPORT_DIR / "phase2e_adjusted_premium_payoff_comparison_check_report.txt"


def section(label: str = "", char: str = "-") -> str:
    if not label:
        return char * 96
    return f"{label}\n{char * 96}"


def file_status(label: str, path: Path) -> tuple[bool, str]:
    exists = path.exists()
    status = "FOUND" if exists else "MISSING"
    return exists, f"{status:<10} {label:<52} {path}"


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)
    return max(len(rows) - 1, 0)


def file_contains_any(path: Path, markers: list[str]) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    return any(marker.lower() in text for marker in markers)


def run_module() -> tuple[bool, str]:
    cmd = [sys.executable, str(MODULE_PATH)]
    completed = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )
    output: list[str] = []
    output.append(f"Command: {' '.join(cmd)}")
    output.append(f"Return code: {completed.returncode}")
    output.append("")
    output.append("STDOUT")
    output.append("------")
    output.append(completed.stdout.strip() or "<empty>")
    output.append("")
    output.append("STDERR")
    output.append("------")
    output.append(completed.stderr.strip() or "<empty>")
    return completed.returncode == 0, "\n".join(output)


def main() -> int:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines: list[str] = []
    all_ok = True

    report_lines.append("=" * 96)
    report_lines.append("Phase 2E adjusted-premium payoff comparison check")
    report_lines.append("=" * 96)
    report_lines.append(f"Generated: {generated}")
    report_lines.append(f"Project root: {PROJECT_ROOT}")
    report_lines.append("")

    required_before_run = [
        ("Adjusted payoff comparison module", MODULE_PATH),
        ("Scenario price-path scaffold CSV", PRICE_PATHS_CSV),
        ("Adjusted premium CSV", ADJUSTED_PREMIUM_CSV),
        ("Prior premium-aware payoff CSV", PRIOR_PAYOFF_CSV),
        ("Phase 2E adjusted payoff documentation", DOC_PATH),
    ]

    report_lines.append(section("Required files before run"))
    for label, path in required_before_run:
        ok, text = file_status(label, path)
        all_ok = all_ok and ok
        report_lines.append(text)
    report_lines.append("")

    if MODULE_PATH.exists() and PRICE_PATHS_CSV.exists() and ADJUSTED_PREMIUM_CSV.exists():
        ok, run_text = run_module()
        all_ok = all_ok and ok
        report_lines.append(section("Module run"))
        report_lines.append(run_text)
        report_lines.append("")
    else:
        all_ok = False
        report_lines.append(section("Module run"))
        report_lines.append("SKIPPED: Required source/input files are missing.")
        report_lines.append("")

    expected_after_run = [
        ("Adjusted payoff comparison CSV", OUTPUT_CSV),
        ("Adjusted payoff comparison HTML", OUTPUT_HTML),
        ("Adjusted payoff summary text", OUTPUT_SUMMARY),
    ]

    report_lines.append(section("Expected outputs after run"))
    for label, path in expected_after_run:
        ok, text = file_status(label, path)
        all_ok = all_ok and ok
        report_lines.append(text)
    report_lines.append("")

    report_lines.append(section("CSV row checks"))
    for label, path in [
        ("scenario_price_paths_scaffold.csv", PRICE_PATHS_CSV),
        ("premium_model_adjusted_premiums.csv", ADJUSTED_PREMIUM_CSV),
        ("premium_aware_payoff_scaffold.csv", PRIOR_PAYOFF_CSV),
        ("adjusted_premium_payoff_comparison.csv", OUTPUT_CSV),
    ]:
        rows = count_csv_rows(path)
        if rows > 0:
            report_lines.append(f"PASS       {label:<52} rows={rows}")
        else:
            all_ok = False
            report_lines.append(f"REVIEW     {label:<52} rows={rows}")
    report_lines.append("")

    report_lines.append(section("Summary marker checks"))
    marker_checks = [
        ("Adjusted payoff summary label", OUTPUT_SUMMARY, ["Adjusted Premium Payoff Comparison Summary"]),
        ("Overall marker", OUTPUT_SUMMARY, ["Overall"]),
    ]
    for label, path, markers in marker_checks:
        if file_contains_any(path, markers):
            report_lines.append(f"PASS       {label}")
        else:
            all_ok = False
            report_lines.append(f"REVIEW     {label}")
    report_lines.append("")

    report_lines.append("=" * 96)
    if all_ok:
        report_lines.append("Overall Phase 2E adjusted premium payoff comparison status: PASS")
    else:
        report_lines.append("Overall Phase 2E adjusted premium payoff comparison status: REVIEW")
    report_lines.append("=" * 96)
    report_lines.append(f"Saved check report: {CHECK_REPORT}")

    CHECK_REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    print("\n".join(report_lines))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
