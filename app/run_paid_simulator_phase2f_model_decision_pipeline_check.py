"""
run_paid_simulator_phase2f_model_decision_pipeline_check.py

Phase 2F model-decision pipeline checker for the Covered Call Strategy Stress Test.

This script runs the Phase 2F model-decision workflow and verifies that the
consolidated model-decision outputs are being produced. It does not modify the
customer-facing dashboard.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase2f_model_decision_pipeline_report.txt"


@dataclass
class ScriptStep:
    name: str
    path: Path
    required: bool = True


@dataclass
class FileCheck:
    label: str
    path: Path
    kind: str
    required: bool = True


@dataclass
class MarkerCheck:
    label: str
    path: Path
    markers: list[str]
    required: bool = True


def run_script(step: ScriptStep) -> tuple[str, str]:
    """Run one Python script and return a status plus summary text."""
    if not step.path.exists():
        status = "FAIL" if step.required else "SKIP"
        return status, f"{status}: {step.name} script not found: {step.path}"

    completed = subprocess.run(
        [sys.executable, str(step.path)],
        cwd=str(PROJECT_ROOT),
        text=True,
        capture_output=True,
    )

    combined_output = "\n".join(
        part for part in [completed.stdout.strip(), completed.stderr.strip()] if part
    )

    if completed.returncode == 0:
        return "PASS", f"PASS: {step.name} completed successfully."

    return (
        "FAIL",
        f"FAIL: {step.name} exited with return code {completed.returncode}.\n"
        f"Script: {step.path}\n"
        f"Output:\n{combined_output}",
    )


def count_csv_rows(path: Path) -> int:
    """Count data rows in a CSV file, excluding the header."""
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)
    if not rows:
        return 0
    return max(len(rows) - 1, 0)


def check_file(item: FileCheck) -> tuple[str, str]:
    """Verify that one expected file exists and has reasonable content."""
    if not item.path.exists():
        status = "FAIL" if item.required else "SKIP"
        return status, f"{status}: {item.label} missing: {item.path}"

    if item.kind == "csv":
        try:
            row_count = count_csv_rows(item.path)
        except Exception as exc:
            return "FAIL", f"FAIL: {item.label} could not be read as CSV: {exc}"
        if row_count <= 0:
            return "FAIL", f"FAIL: {item.label} exists but has no data rows: {item.path}"
        return "PASS", f"PASS: {item.label} exists with {row_count} data rows."

    if item.kind == "text":
        try:
            text = item.path.read_text(encoding="utf-8", errors="replace").strip()
        except Exception as exc:
            return "FAIL", f"FAIL: {item.label} could not be read as text: {exc}"
        if not text:
            return "FAIL", f"FAIL: {item.label} exists but is empty: {item.path}"
        return "PASS", f"PASS: {item.label} exists and is not empty."

    if item.kind == "html":
        try:
            text = item.path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:
            return "FAIL", f"FAIL: {item.label} could not be read as HTML: {exc}"
        lower = text.lower()
        if "<html" not in lower and "<table" not in lower:
            return "FAIL", f"FAIL: {item.label} does not look like an HTML report: {item.path}"
        return "PASS", f"PASS: {item.label} exists and looks like an HTML report."

    return "FAIL", f"FAIL: Unknown file-check kind for {item.label}: {item.kind}"


def check_markers(item: MarkerCheck) -> tuple[str, list[str]]:
    """Check that a text file contains expected marker strings."""
    if not item.path.exists():
        status = "FAIL" if item.required else "SKIP"
        return status, [f"{status}: {item.label} missing: {item.path}"]

    try:
        text = item.path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return "FAIL", [f"FAIL: {item.label} could not be read: {exc}"]

    lower_text = text.lower()
    lines: list[str] = []
    statuses: list[str] = []
    for marker in item.markers:
        if marker.lower() in lower_text:
            statuses.append("PASS")
            lines.append(f"PASS: {item.label} marker found: {marker}")
        else:
            statuses.append("FAIL")
            lines.append(f"FAIL: {item.label} marker missing: {marker}")

    return ("FAIL" if "FAIL" in statuses else "PASS"), lines


def final_status(statuses: list[str]) -> str:
    """Return PASS only if no required item failed."""
    return "FAIL" if any(status == "FAIL" for status in statuses) else "PASS"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    script_steps = [
        ScriptStep(
            name="Phase 2E checkpoint check",
            path=APP_DIR / "run_paid_simulator_phase2e_checkpoint_check.py",
            required=False,
        ),
        ScriptStep(
            name="Phase 2F model-decision summary check",
            path=APP_DIR / "run_paid_simulator_model_decision_summary_check.py",
            required=True,
        ),
        ScriptStep(
            name="Phase 2F model-decision viewer check",
            path=APP_DIR / "run_paid_simulator_phase2f_model_decision_viewer_check.py",
            required=True,
        ),
    ]

    file_checks = [
        FileCheck(
            label="Model-decision summary CSV",
            path=TABLE_DIR / "model_decision_summary.csv",
            kind="csv",
        ),
        FileCheck(
            label="Model-decision summary HTML",
            path=REPORT_DIR / "model_decision_summary.html",
            kind="html",
        ),
        FileCheck(
            label="Model-decision summary text",
            path=REPORT_DIR / "model_decision_summary.txt",
            kind="text",
        ),
        FileCheck(
            label="Model-decision summary check report",
            path=REPORT_DIR / "phase2f_model_decision_summary_check_report.txt",
            kind="text",
        ),
        FileCheck(
            label="Model-decision viewer check report",
            path=REPORT_DIR / "phase2f_model_decision_viewer_check_report.txt",
            kind="text",
        ),
        FileCheck(
            label="Option premium scaffold CSV",
            path=TABLE_DIR / "option_premium_scaffold.csv",
            kind="csv",
        ),
        FileCheck(
            label="Premium-aware payoff CSV",
            path=TABLE_DIR / "premium_aware_payoff_scaffold.csv",
            kind="csv",
        ),
        FileCheck(
            label="Premium validation CSV",
            path=TABLE_DIR / "premium_model_validation_scaffold.csv",
            kind="csv",
        ),
        FileCheck(
            label="Premium tuning recommendations CSV",
            path=TABLE_DIR / "premium_model_tuning_recommendations.csv",
            kind="csv",
        ),
        FileCheck(
            label="Adjusted premiums CSV",
            path=TABLE_DIR / "premium_model_adjusted_premiums.csv",
            kind="csv",
        ),
        FileCheck(
            label="Adjusted payoff comparison CSV",
            path=TABLE_DIR / "adjusted_premium_payoff_comparison.csv",
            kind="csv",
        ),
    ]

    marker_checks = [
        MarkerCheck(
            label="Model-decision text summary",
            path=REPORT_DIR / "model_decision_summary.txt",
            markers=[
                "model",
                "decision",
            ],
        ),
        MarkerCheck(
            label="Model-decision summary check report",
            path=REPORT_DIR / "phase2f_model_decision_summary_check_report.txt",
            markers=[
                "Overall Phase 2F model-decision summary status",
            ],
        ),
        MarkerCheck(
            label="Model-decision viewer check report",
            path=REPORT_DIR / "phase2f_model_decision_viewer_check_report.txt",
            markers=[
                "Overall Phase 2F model-decision viewer status",
            ],
        ),
    ]

    lines: list[str] = []
    statuses: list[str] = []

    lines.append("=" * 96)
    lines.append("Phase 2F model-decision pipeline check")
    lines.append("=" * 96)
    lines.append(f"Generated:    {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    lines.append("Script steps")
    lines.append("-" * 96)
    for step in script_steps:
        status, message = run_script(step)
        if step.required or status == "FAIL":
            statuses.append(status)
        lines.append(message)
    lines.append("")

    lines.append("Expected Phase 2F files and context outputs")
    lines.append("-" * 96)
    for item in file_checks:
        status, message = check_file(item)
        if item.required or status == "FAIL":
            statuses.append(status)
        lines.append(message)
    lines.append("")

    lines.append("Content markers")
    lines.append("-" * 96)
    for item in marker_checks:
        status, messages = check_markers(item)
        if item.required or status == "FAIL":
            statuses.append(status)
        lines.extend(messages)
    lines.append("")

    overall = final_status(statuses)
    lines.append("Summary")
    lines.append("-" * 96)
    lines.append(f"Overall Phase 2F model-decision pipeline status: {overall}")
    lines.append("")

    if overall == "PASS":
        lines.append(
            "The Phase 2F model-decision workflow is installed, runnable, and "
            "producing the expected consolidated model-decision outputs."
        )
    else:
        lines.append(
            "One or more required Phase 2F model-decision pipeline items failed. "
            "Review the messages above before adding Phase 2F to the main dashboard."
        )

    report_text = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print(report_text)
    print(f"Saved report: {REPORT_PATH}")

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
