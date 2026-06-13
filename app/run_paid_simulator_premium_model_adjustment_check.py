"""
run_paid_simulator_premium_model_adjustment_check.py

Runner/checker for the Phase 2E controlled premium-model adjustment scaffold.

This script runs the adjustment module, verifies the expected outputs, and
writes a plain-text check report.
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
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

MODULE_PATH = PAID_SIMULATOR_DIR / "premium_model_adjustment.py"
CONFIG_PATH = CONFIG_DIR / "premium_model_adjustment_config.json"
INPUT_OPTION_PREMIUM_CSV = OUTPUT_TABLE_DIR / "option_premium_scaffold.csv"
INPUT_TUNING_CSV = OUTPUT_TABLE_DIR / "premium_model_tuning_recommendations.csv"
OUTPUT_CSV = OUTPUT_TABLE_DIR / "premium_model_adjusted_premiums.csv"
OUTPUT_HTML = OUTPUT_REPORT_DIR / "premium_model_adjustment_comparison.html"
OUTPUT_SUMMARY = OUTPUT_REPORT_DIR / "premium_model_adjustment_summary.txt"
DOC_PATH = DOCS_DIR / "paid_simulator_phase2e_premium_model_adjustment.md"
CHECK_REPORT = OUTPUT_REPORT_DIR / "phase2e_premium_model_adjustment_check_report.txt"


def line(label: str = "", char: str = "-") -> str:
    if not label:
        return char * 96
    return f"{label}\n{char * 96}"


def file_status(label: str, path: Path) -> tuple[bool, str]:
    exists = path.exists()
    status = "FOUND" if exists else "MISSING"
    return exists, f"{status:<10} {label:<48} {path}"


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        rows = list(reader)
    return max(len(rows) - 1, 0)


def run_module() -> tuple[bool, str]:
    cmd = [sys.executable, str(MODULE_PATH)]
    completed = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
    )
    output = []
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
    report_lines: list[str] = []
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_lines.append("=" * 96)
    report_lines.append("Phase 2E controlled premium-model adjustment check")
    report_lines.append("=" * 96)
    report_lines.append(f"Generated: {generated}")
    report_lines.append(f"Project root: {PROJECT_ROOT}")
    report_lines.append("")

    required_before_run = [
        ("Premium adjustment module", MODULE_PATH),
        ("Option premium scaffold CSV", INPUT_OPTION_PREMIUM_CSV),
        ("Premium-model tuning recommendations CSV", INPUT_TUNING_CSV),
        ("Phase 2E documentation", DOC_PATH),
    ]

    all_ok = True
    report_lines.append(line("Required files before run"))
    for label, path in required_before_run:
        ok, text = file_status(label, path)
        all_ok = all_ok and ok
        report_lines.append(text)
    report_lines.append("")

    if MODULE_PATH.exists() and INPUT_OPTION_PREMIUM_CSV.exists():
        ok, run_text = run_module()
        all_ok = all_ok and ok
        report_lines.append(line("Module run"))
        report_lines.append(run_text)
        report_lines.append("")
    else:
        all_ok = False
        report_lines.append(line("Module run"))
        report_lines.append("SKIPPED: Required source/input files are missing.")
        report_lines.append("")

    expected_after_run = [
        ("Premium adjustment config", CONFIG_PATH),
        ("Adjusted premium CSV", OUTPUT_CSV),
        ("Adjustment HTML report", OUTPUT_HTML),
        ("Adjustment summary text", OUTPUT_SUMMARY),
    ]

    report_lines.append(line("Expected outputs after run"))
    for label, path in expected_after_run:
        ok, text = file_status(label, path)
        all_ok = all_ok and ok
        report_lines.append(text)
    report_lines.append("")

    report_lines.append(line("CSV row checks"))
    for label, path in [
        ("option_premium_scaffold.csv", INPUT_OPTION_PREMIUM_CSV),
        ("premium_model_tuning_recommendations.csv", INPUT_TUNING_CSV),
        ("premium_model_adjusted_premiums.csv", OUTPUT_CSV),
    ]:
        rows = count_csv_rows(path)
        if rows > 0:
            report_lines.append(f"PASS       {label:<48} rows={rows}")
        else:
            all_ok = False
            report_lines.append(f"REVIEW     {label:<48} rows={rows}")
    report_lines.append("")

    report_lines.append("=" * 96)
    if all_ok:
        report_lines.append("Overall Phase 2E controlled premium adjustment status: PASS")
    else:
        report_lines.append("Overall Phase 2E controlled premium adjustment status: REVIEW")
    report_lines.append("=" * 96)
    report_lines.append(f"Saved check report: {CHECK_REPORT}")

    CHECK_REPORT.write_text("\n".join(report_lines), encoding="utf-8")
    print("\n".join(report_lines))
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
