"""
run_paid_simulator_phase2c_validation_pipeline_check.py

Phase 2C validation pipeline checker for the Covered Call Strategy Stress Test.

This script is intentionally conservative. It does not modify the customer-facing
paid simulator dashboard. It verifies that the Phase 2C premium-model validation
layer can run end-to-end and that the expected validation outputs are produced.
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
REPORT_PATH = REPORT_DIR / "phase2c_validation_pipeline_report.txt"


@dataclass
class ScriptStep:
    name: str
    path: Path
    required: bool = True


@dataclass
class OutputCheck:
    label: str
    path: Path
    kind: str
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


def check_output(item: OutputCheck) -> tuple[str, str]:
    """Verify that one expected output exists and has reasonable content."""
    if not item.path.exists():
        status = "FAIL" if item.required else "SKIP"
        return status, f"{status}: {item.label} missing: {item.path}"

    if item.kind == "csv":
        try:
            row_count = count_csv_rows(item.path)
        except Exception as exc:  # pragma: no cover - diagnostic path
            return "FAIL", f"FAIL: {item.label} could not be read as CSV: {exc}"
        if row_count <= 0:
            return "FAIL", f"FAIL: {item.label} exists but has no data rows: {item.path}"
        return "PASS", f"PASS: {item.label} exists with {row_count} data rows."

    if item.kind == "text":
        try:
            text = item.path.read_text(encoding="utf-8", errors="replace").strip()
        except Exception as exc:  # pragma: no cover - diagnostic path
            return "FAIL", f"FAIL: {item.label} could not be read as text: {exc}"
        if not text:
            return "FAIL", f"FAIL: {item.label} exists but is empty: {item.path}"
        return "PASS", f"PASS: {item.label} exists and is not empty."

    if item.kind == "html":
        try:
            text = item.path.read_text(encoding="utf-8", errors="replace")
        except Exception as exc:  # pragma: no cover - diagnostic path
            return "FAIL", f"FAIL: {item.label} could not be read as HTML: {exc}"
        if "<html" not in text.lower() and "<table" not in text.lower():
            return "FAIL", f"FAIL: {item.label} does not look like an HTML report: {item.path}"
        return "PASS", f"PASS: {item.label} exists and looks like an HTML report."

    return "FAIL", f"FAIL: Unknown output kind for {item.label}: {item.kind}"


def overall_status(statuses: list[str]) -> str:
    """Return PASS only if no required step/check failed."""
    return "FAIL" if any(status == "FAIL" for status in statuses) else "PASS"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    script_steps = [
        ScriptStep(
            name="Phase 2B premium-model pipeline check",
            path=APP_DIR / "run_paid_simulator_phase2b_pipeline_check.py",
            required=False,
        ),
        ScriptStep(
            name="Phase 2C premium-model validation check",
            path=APP_DIR / "run_paid_simulator_premium_model_validation_check.py",
            required=True,
        ),
        ScriptStep(
            name="Phase 2C premium-validation viewer check",
            path=APP_DIR / "run_paid_simulator_phase2c_premium_validation_viewer_check.py",
            required=True,
        ),
    ]

    expected_outputs = [
        OutputCheck(
            label="Premium-model validation CSV",
            path=TABLE_DIR / "premium_model_validation_scaffold.csv",
            kind="csv",
        ),
        OutputCheck(
            label="Premium-model validation HTML report",
            path=REPORT_DIR / "premium_model_validation_scaffold.html",
            kind="html",
        ),
        OutputCheck(
            label="Premium-model validation summary text",
            path=REPORT_DIR / "premium_model_validation_summary.txt",
            kind="text",
        ),
        OutputCheck(
            label="Option-premium scaffold CSV",
            path=TABLE_DIR / "option_premium_scaffold.csv",
            kind="csv",
        ),
        OutputCheck(
            label="Premium-aware payoff scaffold CSV",
            path=TABLE_DIR / "premium_aware_payoff_scaffold.csv",
            kind="csv",
        ),
    ]

    lines: list[str] = []
    statuses: list[str] = []

    lines.append("=" * 92)
    lines.append("Phase 2C premium-model validation pipeline check")
    lines.append("=" * 92)
    lines.append(f"Timestamp:    {datetime.now().isoformat(timespec='seconds')}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    lines.append("Script steps")
    lines.append("-" * 92)
    for step in script_steps:
        status, message = run_script(step)
        statuses.append(status)
        lines.append(message)
    lines.append("")

    lines.append("Expected outputs")
    lines.append("-" * 92)
    for item in expected_outputs:
        status, message = check_output(item)
        statuses.append(status)
        lines.append(message)
    lines.append("")

    final_status = overall_status(statuses)
    lines.append("Summary")
    lines.append("-" * 92)
    lines.append(f"Overall Phase 2C validation pipeline status: {final_status}")
    lines.append("")

    if final_status == "PASS":
        lines.append(
            "The Phase 2C validation layer is installed, runnable, and producing the "
            "expected validation outputs. This does not mean the option-premium "
            "assumptions are final; it means the validation workflow is ready for "
            "assumption tuning."
        )
    else:
        lines.append(
            "One or more required Phase 2C validation checks failed. Review the failure "
            "messages above before integrating Phase 2C into the main dashboard."
        )

    report_text = "\n".join(lines) + "\n"
    REPORT_PATH.write_text(report_text, encoding="utf-8")

    print(report_text)
    print(f"Saved report: {REPORT_PATH}")

    return 0 if final_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
