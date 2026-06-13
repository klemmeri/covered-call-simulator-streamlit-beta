"""
run_paid_simulator_phase2d_tuning_pipeline_check.py

Phase 2D premium-model tuning pipeline checker for the Covered Call Strategy
Stress Test.

This script does not modify the customer-facing dashboard. It runs the Phase 2D
premium-model tuning workflow and verifies that the expected tuning outputs are
being produced.
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
CONFIG_DIR = PROJECT_ROOT / "config"
REPORT_PATH = REPORT_DIR / "phase2d_tuning_pipeline_report.txt"


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

    if item.kind == "json":
        try:
            text = item.path.read_text(encoding="utf-8", errors="replace").strip()
        except Exception as exc:
            return "FAIL", f"FAIL: {item.label} could not be read as JSON text: {exc}"
        if not (text.startswith("{") and text.endswith("}")):
            return "FAIL", f"FAIL: {item.label} does not look like a JSON object: {item.path}"
        return "PASS", f"PASS: {item.label} exists and looks like a JSON config file."

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
            name="Phase 2C checkpoint check",
            path=APP_DIR / "run_paid_simulator_phase2c_checkpoint_check.py",
            required=False,
        ),
        ScriptStep(
            name="Phase 2D premium-model tuning check",
            path=APP_DIR / "run_paid_simulator_premium_model_tuning_check.py",
            required=True,
        ),
        ScriptStep(
            name="Phase 2D premium-tuning viewer check",
            path=APP_DIR / "run_paid_simulator_phase2d_premium_tuning_viewer_check.py",
            required=True,
        ),
    ]

    file_checks = [
        FileCheck(
            label="Premium-model tuning config",
            path=CONFIG_DIR / "premium_model_tuning_config.json",
            kind="json",
        ),
        FileCheck(
            label="Premium-model tuning recommendations CSV",
            path=TABLE_DIR / "premium_model_tuning_recommendations.csv",
            kind="csv",
        ),
        FileCheck(
            label="Premium-model tuning recommendations HTML",
            path=REPORT_DIR / "premium_model_tuning_recommendations.html",
            kind="html",
        ),
        FileCheck(
            label="Premium-model tuning summary text",
            path=REPORT_DIR / "premium_model_tuning_summary.txt",
            kind="text",
        ),
        FileCheck(
            label="Phase 2D tuning check report",
            path=REPORT_DIR / "phase2d_premium_model_tuning_check_report.txt",
            kind="text",
        ),
        FileCheck(
            label="Option-premium scaffold CSV",
            path=TABLE_DIR / "option_premium_scaffold.csv",
            kind="csv",
        ),
        FileCheck(
            label="Premium-model validation CSV",
            path=TABLE_DIR / "premium_model_validation_scaffold.csv",
            kind="csv",
        ),
        FileCheck(
            label="Premium-aware payoff CSV",
            path=TABLE_DIR / "premium_aware_payoff_scaffold.csv",
            kind="csv",
        ),
    ]

    marker_checks = [
        MarkerCheck(
            label="Premium tuning summary",
            path=REPORT_DIR / "premium_model_tuning_summary.txt",
            markers=[
                "premium",
                "tuning",
                "recommend",
            ],
        ),
    ]

    lines: list[str] = []
    statuses: list[str] = []

    lines.append("=" * 96)
    lines.append("Phase 2D premium-model tuning pipeline check")
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

    lines.append("Expected Phase 2D files and outputs")
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
    lines.append(f"Overall Phase 2D tuning pipeline status: {overall}")
    lines.append("")

    if overall == "PASS":
        lines.append(
            "The Phase 2D tuning workflow is installed, runnable, and producing the "
            "expected tuning outputs. Recommendation rows marked REVIEW or TUNE are "
            "model-inspection signals, not installation failures."
        )
    else:
        lines.append(
            "One or more required Phase 2D tuning-pipeline items failed. Review the "
            "messages above before adding the Phase 2D tuning layer to the main dashboard."
        )

    report_text = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print(report_text)
    print(f"Saved report: {REPORT_PATH}")

    return 0 if overall == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
