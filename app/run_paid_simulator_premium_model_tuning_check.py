"""
run_paid_simulator_premium_model_tuning_check.py

Checker for the Phase 2D premium-model assumption tuning scaffold.

Run from PyCharm or the command line:

    python app/run_paid_simulator_premium_model_tuning_check.py
"""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
CONFIG_DIR = PROJECT_ROOT / "config"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))


OPTION_PREMIUM_CHECK = APP_DIR / "run_paid_simulator_option_premium_check.py"
PREMIUM_VALIDATION_CHECK = APP_DIR / "run_paid_simulator_premium_model_validation_check.py"
TUNING_MODULE = PAID_SIMULATOR_DIR / "premium_model_tuning.py"

REQUIRED_FILES = [
    ("Option premium model", PAID_SIMULATOR_DIR / "option_premium_model.py"),
    ("Premium model validation module", PAID_SIMULATOR_DIR / "premium_model_validation.py"),
    ("Premium model tuning module", TUNING_MODULE),
    ("Option premium check", OPTION_PREMIUM_CHECK),
    ("Premium model validation check", PREMIUM_VALIDATION_CHECK),
]

EXPECTED_OUTPUTS = [
    ("Option premium CSV", OUTPUT_TABLE_DIR / "option_premium_scaffold.csv"),
    ("Premium validation CSV", OUTPUT_TABLE_DIR / "premium_model_validation_scaffold.csv"),
    ("Premium tuning CSV", OUTPUT_TABLE_DIR / "premium_model_tuning_recommendations.csv"),
    ("Premium tuning HTML", OUTPUT_REPORT_DIR / "premium_model_tuning_recommendations.html"),
    ("Premium tuning summary", OUTPUT_REPORT_DIR / "premium_model_tuning_summary.txt"),
    ("Premium tuning config", CONFIG_DIR / "premium_model_tuning_config.json"),
]

CHECK_REPORT = OUTPUT_REPORT_DIR / "phase2d_premium_model_tuning_check_report.txt"


def print_header(title: str) -> None:
    print("\n" + title)
    print("-" * 96)


def run_script(path: Path) -> bool:
    if not path.exists():
        print(f"MISSING   {path}")
        return False
    print(f"RUNNING   {path}")
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        print(f"REVIEW    Script exited with code {result.returncode}: {path.name}")
        return False
    print(f"PASS      {path.name}")
    return True


def check_file(label: str, path: Path) -> bool:
    if path.exists():
        print(f"FOUND     {label:<45} {path}")
        return True
    print(f"MISSING   {label:<45} {path}")
    return False


def check_csv_rows(label: str, path: Path, min_rows: int = 1) -> bool:
    if not path.exists():
        print(f"MISSING   {label:<45} {path}")
        return False
    try:
        df = pd.read_csv(path)
    except Exception as exc:  # noqa: BLE001
        print(f"REVIEW    {label:<45} could not read CSV: {exc}")
        return False
    if len(df) >= min_rows:
        print(f"PASS      {label:<45} rows={len(df)}")
        return True
    print(f"REVIEW    {label:<45} rows={len(df)}")
    return False


def write_report(lines: list[str]) -> None:
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CHECK_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    report_lines: list[str] = []
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log(line: str) -> None:
        print(line)
        report_lines.append(line)

    log("=" * 96)
    log("Phase 2D premium-model tuning check")
    log("=" * 96)
    log(f"Generated: {generated}")
    log(f"Project root: {PROJECT_ROOT}")

    ok = True

    print_header("Required files")
    report_lines.append("\nRequired files")
    report_lines.append("-" * 96)
    for label, path in REQUIRED_FILES:
        result = check_file(label, path)
        report_lines.append(("FOUND" if result else "MISSING") + f" {label}: {path}")
        ok = ok and result

    print_header("Generating prerequisite outputs")
    report_lines.append("\nGenerating prerequisite outputs")
    report_lines.append("-" * 96)
    for script in [OPTION_PREMIUM_CHECK, PREMIUM_VALIDATION_CHECK]:
        result = run_script(script)
        report_lines.append(("PASS" if result else "REVIEW") + f" {script.name}")
        ok = ok and result

    print_header("Running Phase 2D tuning module")
    report_lines.append("\nRunning Phase 2D tuning module")
    report_lines.append("-" * 96)
    result = run_script(TUNING_MODULE)
    report_lines.append(("PASS" if result else "REVIEW") + f" {TUNING_MODULE.name}")
    ok = ok and result

    print_header("Expected outputs")
    report_lines.append("\nExpected outputs")
    report_lines.append("-" * 96)
    for label, path in EXPECTED_OUTPUTS:
        result = check_file(label, path)
        report_lines.append(("FOUND" if result else "MISSING") + f" {label}: {path}")
        ok = ok and result

    print_header("CSV row checks")
    report_lines.append("\nCSV row checks")
    report_lines.append("-" * 96)
    for label, path in [
        ("Option premium CSV", OUTPUT_TABLE_DIR / "option_premium_scaffold.csv"),
        ("Premium validation CSV", OUTPUT_TABLE_DIR / "premium_model_validation_scaffold.csv"),
        ("Premium tuning CSV", OUTPUT_TABLE_DIR / "premium_model_tuning_recommendations.csv"),
    ]:
        result = check_csv_rows(label, path, min_rows=1)
        report_lines.append(("PASS" if result else "REVIEW") + f" {label}: {path}")
        ok = ok and result

    print("\n" + "=" * 96)
    if ok:
        print("Overall Phase 2D premium-model tuning status: PASS")
        report_lines.append("\nOverall Phase 2D premium-model tuning status: PASS")
        exit_code = 0
    else:
        print("Overall Phase 2D premium-model tuning status: REVIEW")
        report_lines.append("\nOverall Phase 2D premium-model tuning status: REVIEW")
        exit_code = 1
    print("=" * 96)

    write_report(report_lines)
    print(f"\nSaved check report: {CHECK_REPORT}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
