"""
run_paid_simulator_phase2g_model_promotion_pipeline_check.py

Phase 2G model-promotion pipeline checker for the Covered Call Simulator.

This script runs the Phase 2G controlled model-promotion workflow end-to-end:

1. Phase 2F checkpoint check
2. Phase 2G model-promotion planning check
3. Phase 2G model-promotion viewer check

It then verifies that the expected Phase 2G outputs exist and contain data.

This is an internal developer check. It does not promote any model into the
customer dashboard.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase2g_model_promotion_pipeline_report.txt"


CHECKS_TO_RUN = [
    (
        "Phase 2F checkpoint check",
        APP_DIR / "run_paid_simulator_phase2f_checkpoint_check.py",
    ),
    (
        "Phase 2G model-promotion planning check",
        APP_DIR / "run_paid_simulator_model_promotion_planning_check.py",
    ),
    (
        "Phase 2G model-promotion viewer check",
        APP_DIR / "run_paid_simulator_phase2g_model_promotion_viewer_check.py",
    ),
]


EXPECTED_FILES = [
    (
        "Model-promotion plan CSV",
        TABLE_DIR / "model_promotion_plan.csv",
    ),
    (
        "Model-promotion plan HTML",
        REPORT_DIR / "model_promotion_plan.html",
    ),
    (
        "Model-promotion plan text summary",
        REPORT_DIR / "model_promotion_plan.txt",
    ),
    (
        "Phase 2G planning check report",
        REPORT_DIR / "phase2g_model_promotion_planning_check_report.txt",
    ),
    (
        "Phase 2G viewer check report",
        REPORT_DIR / "phase2g_model_promotion_viewer_check_report.txt",
    ),
]


EXPECTED_CONTEXT_FILES = [
    (
        "Phase 2F model-decision CSV",
        TABLE_DIR / "model_decision_summary.csv",
    ),
    (
        "Adjusted payoff comparison CSV",
        TABLE_DIR / "adjusted_premium_payoff_comparison.csv",
    ),
    (
        "Premium tuning recommendations CSV",
        TABLE_DIR / "premium_model_tuning_recommendations.csv",
    ),
    (
        "Premium validation CSV",
        TABLE_DIR / "premium_model_validation_scaffold.csv",
    ),
    (
        "Option premium CSV",
        TABLE_DIR / "option_premium_scaffold.csv",
    ),
]


EXPECTED_DOCS = [
    (
        "Phase 2G model-promotion planning documentation",
        PROJECT_ROOT / "docs" / "paid_simulator_phase2g_model_promotion_planning.md",
    ),
    (
        "Phase 2G model-promotion viewer documentation",
        PROJECT_ROOT / "docs" / "paid_simulator_phase2g_model_promotion_viewer.md",
    ),
]


def line(title: str = "", width: int = 96, char: str = "=") -> str:
    if not title:
        return char * width
    return f"{title}\n" + (char * width)


def status_line(status: str, label: str, detail: str = "") -> str:
    return f"{status:<10} {label:<55} {detail}"


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return -1
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
    except Exception:
        return -1
    if not rows:
        return 0
    return max(0, len(rows) - 1)


def run_check(label: str, script_path: Path) -> tuple[bool, list[str]]:
    output: list[str] = []

    if not script_path.exists():
        output.append(status_line("MISSING", label, str(script_path)))
        return False, output

    output.append(status_line("RUNNING", label, str(script_path)))

    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception as exc:
        output.append(status_line("ERROR", label, f"Could not run script: {exc}"))
        return False, output

    if completed.returncode == 0:
        output.append(status_line("PASS", label, "return code 0"))
        return True, output

    output.append(status_line("REVIEW", label, f"return code {completed.returncode}"))
    if completed.stdout.strip():
        output.append("--- stdout tail ---")
        output.extend(completed.stdout.strip().splitlines()[-12:])
    if completed.stderr.strip():
        output.append("--- stderr tail ---")
        output.extend(completed.stderr.strip().splitlines()[-12:])
    return False, output


def check_files(section_title: str, files: list[tuple[str, Path]]) -> tuple[bool, list[str]]:
    output: list[str] = [line(section_title, char="-")]
    ok = True
    for label, path in files:
        if path.exists():
            output.append(status_line("FOUND", label, str(path)))
        else:
            output.append(status_line("MISSING", label, str(path)))
            ok = False
    return ok, output


def check_csv_rows(files: list[tuple[str, Path]]) -> tuple[bool, list[str]]:
    output: list[str] = [line("CSV row checks", char="-")]
    ok = True
    for label, path in files:
        rows = csv_row_count(path)
        if rows > 0:
            output.append(status_line("PASS", path.name, f"rows={rows}"))
        elif rows == 0:
            output.append(status_line("REVIEW", path.name, "rows=0"))
            ok = False
        else:
            output.append(status_line("MISSING", path.name, "could not read CSV"))
            ok = False
    return ok, output


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    output: list[str] = []
    output.append(line("Phase 2G model-promotion pipeline check"))
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append(f"Project root: {PROJECT_ROOT}")
    output.append("")

    overall_ok = True

    output.append(line("Running prerequisite checks", char="-"))
    for label, script_path in CHECKS_TO_RUN:
        check_ok, check_output = run_check(label, script_path)
        output.extend(check_output)
        overall_ok = overall_ok and check_ok
        output.append("")

    file_ok, file_output = check_files("Expected Phase 2G outputs", EXPECTED_FILES)
    output.extend(file_output)
    output.append("")
    overall_ok = overall_ok and file_ok

    context_ok, context_output = check_files("Expected Phase 2G context outputs", EXPECTED_CONTEXT_FILES)
    output.extend(context_output)
    output.append("")
    overall_ok = overall_ok and context_ok

    doc_ok, doc_output = check_files("Phase 2G documentation", EXPECTED_DOCS)
    output.extend(doc_output)
    output.append("")
    overall_ok = overall_ok and doc_ok

    csv_ok, csv_output = check_csv_rows(
        [("Model-promotion plan", TABLE_DIR / "model_promotion_plan.csv")]
    )
    output.extend(csv_output)
    output.append("")
    overall_ok = overall_ok and csv_ok

    output.append(line())
    if overall_ok:
        output.append("Overall Phase 2G model-promotion pipeline status: PASS")
        output.append("The Phase 2G model-promotion workflow is connected end-to-end.")
        exit_code = 0
    else:
        output.append("Overall Phase 2G model-promotion pipeline status: REVIEW")
        output.append("One or more Phase 2G pipeline items need attention before dashboard integration.")
        exit_code = 1
    output.append(line())
    output.append("")
    output.append(f"Saved pipeline report: {REPORT_PATH}")

    report_text = "\n".join(output)
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    print(report_text)

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
