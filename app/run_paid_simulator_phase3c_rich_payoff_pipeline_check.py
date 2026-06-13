"""
run_paid_simulator_phase3c_rich_payoff_pipeline_check.py

Phase 3C rich payoff-viewer pipeline check for the Covered Call Simulator.

This script verifies that the Phase 3C richer graphical payoff viewer is
installed, that its checker can run, and that optional snapshot outputs are
handled correctly.

The rich payoff snapshot files are optional because they are created only after
opening the Phase 3C Streamlit viewer and saving/exporting a setup.
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

REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"

REPORT_PATH = REPORTS_DIR / "phase3c_rich_payoff_pipeline_report.txt"


REQUIRED_FILES = [
    (
        "Phase 3C rich payoff viewer app",
        PAID_SIMULATOR_DIR / "phase3c_rich_payoff_viewer.py",
    ),
    (
        "Phase 3C rich payoff viewer launcher",
        APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer.py",
    ),
    (
        "Phase 3C rich payoff viewer check",
        APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer_check.py",
    ),
    (
        "Phase 3C rich payoff viewer documentation",
        DOCS_DIR / "paid_simulator_phase3c_rich_payoff_viewer.md",
    ),
]

CONTEXT_FILES = [
    (
        "Phase 3B checkpoint check",
        APP_DIR / "run_paid_simulator_phase3b_checkpoint_check.py",
    ),
    (
        "Phase 3B scenario overlay CSV",
        TABLES_DIR / "phase3_scenario_overlay.csv",
    ),
]

OPTIONAL_SNAPSHOT_FILES = [
    (
        "Phase 3C rich payoff snapshot CSV",
        TABLES_DIR / "phase3c_rich_payoff_snapshot.csv",
    ),
    (
        "Phase 3C rich payoff snapshot HTML",
        REPORTS_DIR / "phase3c_rich_payoff_snapshot.html",
    ),
]

VIEWER_CHECK = APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer_check.py"


class CheckRecorder:
    """Collects check lines and status counts for a readable report."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures = 0
        self.reviews = 0

    def add(self, status: str, label: str, detail: str = "") -> None:
        status = status.upper()
        if status in {"FAIL", "MISSING", "ERROR"}:
            self.failures += 1
        elif status in {"REVIEW", "OPTIONAL"}:
            self.reviews += 1
        self.lines.append(f"{status:<10} {label:<52} {detail}")

    def section(self, title: str) -> None:
        self.lines.append("")
        self.lines.append(title)
        self.lines.append("-" * 96)

    def text(self, value: str = "") -> None:
        self.lines.append(value)


def print_header(recorder: CheckRecorder) -> None:
    recorder.text("=" * 96)
    recorder.text("Phase 3C rich payoff-viewer pipeline check")
    recorder.text("=" * 96)
    recorder.text(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    recorder.text(f"Project root: {PROJECT_ROOT}")


def file_has_rows(path: Path) -> tuple[bool, int, str]:
    """Return whether a CSV exists and has at least one data row."""
    if not path.exists():
        return False, 0, "file missing"

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle))
    except Exception as exc:  # pragma: no cover - diagnostic path
        return False, 0, f"could not read CSV: {exc}"

    if not rows:
        return False, 0, "empty file"

    data_rows = max(0, len(rows) - 1)
    return data_rows > 0, data_rows, f"rows={data_rows}"


def run_script(path: Path) -> tuple[bool, str]:
    """Run a Python script and return success plus a compact diagnostic string."""
    if not path.exists():
        return False, "script missing"

    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return True, "returncode=0"

    output = (result.stdout or "") + "\n" + (result.stderr or "")
    output = output.strip().replace("\r", "")
    tail = output[-500:] if output else "no output"
    return False, f"returncode={result.returncode}; tail={tail}"


def main() -> int:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    recorder = CheckRecorder()
    print_header(recorder)

    recorder.section("Required Phase 3C files")
    for label, path in REQUIRED_FILES:
        if path.exists():
            recorder.add("FOUND", label, str(path))
        else:
            recorder.add("MISSING", label, str(path))

    recorder.section("Phase 3B context files")
    for label, path in CONTEXT_FILES:
        if path.exists():
            recorder.add("FOUND", label, str(path))
        else:
            recorder.add("REVIEW", label, f"not found: {path}")

    recorder.section("Run Phase 3C viewer check")
    success, detail = run_script(VIEWER_CHECK)
    if success:
        recorder.add("PASS", "Phase 3C rich payoff viewer check", detail)
    else:
        recorder.add("FAIL", "Phase 3C rich payoff viewer check", detail)

    recorder.section("Optional Phase 3C saved payoff snapshot outputs")
    for label, path in OPTIONAL_SNAPSHOT_FILES:
        if path.exists():
            if path.suffix.lower() == ".csv":
                ok, _rows, detail = file_has_rows(path)
                status = "PASS" if ok else "REVIEW"
                recorder.add(status, label, detail)
            else:
                recorder.add("FOUND", label, str(path))
        else:
            recorder.add(
                "OPTIONAL",
                label,
                "not found yet; acceptable until a setup is saved from the viewer",
            )

    recorder.section("Phase 3C pipeline result")
    if recorder.failures == 0 and recorder.reviews == 0:
        overall = "PASS"
        exit_code = 0
        recorder.text("Overall Phase 3C rich payoff pipeline status: PASS")
    elif recorder.failures == 0:
        overall = "PASS WITH OPTIONAL SNAPSHOT REVIEW"
        exit_code = 0
        recorder.text(
            "Overall Phase 3C rich payoff pipeline status: PASS WITH OPTIONAL SNAPSHOT REVIEW"
        )
        recorder.text(
            "Only optional/context items require review. This is acceptable if no Phase 3C setup has been saved yet."
        )
    else:
        overall = "REVIEW"
        exit_code = 1
        recorder.text("Overall Phase 3C rich payoff pipeline status: REVIEW")
        recorder.text("One or more required Phase 3C pipeline items need attention.")

    recorder.text("=" * 96)
    recorder.text(f"Saved pipeline report: {REPORT_PATH}")

    report_text = "\n".join(recorder.lines) + "\n"
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    print(report_text)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
