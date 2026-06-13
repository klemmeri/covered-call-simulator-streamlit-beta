"""
run_paid_simulator_phase3_scenario_overlay_pipeline_check.py

Pipeline checker for Phase 3B: Scenario Overlay.

This script verifies that the Phase 3B scenario-overlay layer is installed,
runs its component checks, and confirms that the expected CSV/HTML/text outputs
exist and contain data.

It is intentionally add-only and does not modify the main dashboard.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable


CURRENT_FILE = Path(__file__).resolve()
APP_DIR = CURRENT_FILE.parent
PROJECT_ROOT = APP_DIR.parent

OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = OUTPUT_REPORT_DIR / "phase3b_scenario_overlay_pipeline_report.txt"


class CheckReport:
    """Collects check lines and prints/saves a readable report."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.has_failure = False
        self.has_review = False

    def add(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def section(self, title: str) -> None:
        self.add("")
        self.add(title)
        self.add("-" * 96)

    def status(self, status: str, label: str, detail: str = "") -> None:
        status_upper = status.upper()
        if status_upper in {"FAIL", "ERROR", "MISSING"}:
            self.has_failure = True
        if status_upper == "REVIEW":
            self.has_review = True
        self.add(f"{status_upper:<10} {label:<52} {detail}")

    def save(self) -> None:
        OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text("\n".join(self.lines) + "\n", encoding="utf-8")


def count_csv_rows(path: Path) -> int:
    """Return the number of data rows in a CSV file, excluding the header."""
    if not path.exists():
        return 0
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        if not rows:
            return 0
        return max(0, len(rows) - 1)
    except Exception:
        return 0


def check_file(report: CheckReport, path: Path, label: str, required: bool = True) -> None:
    if path.exists():
        report.status("FOUND", label, str(path))
    elif required:
        report.status("MISSING", label, str(path))
    else:
        report.status("REVIEW", label, f"Optional file not found: {path}")


def run_script(report: CheckReport, script_path: Path, label: str) -> None:
    if not script_path.exists():
        report.status("MISSING", label, str(script_path))
        return

    report.status("RUN", label, str(script_path))
    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
    except Exception as exc:
        report.status("ERROR", label, f"Could not run script: {exc}")
        return

    if completed.returncode == 0:
        report.status("PASS", label, "exit code 0")
    else:
        report.status("FAIL", label, f"exit code {completed.returncode}")
        if completed.stdout.strip():
            report.add("\nCaptured stdout:")
            report.add(completed.stdout.strip())
        if completed.stderr.strip():
            report.add("\nCaptured stderr:")
            report.add(completed.stderr.strip())


def main() -> int:
    report = CheckReport()

    report.add("=" * 96)
    report.add("Phase 3B scenario-overlay pipeline check")
    report.add("=" * 96)
    report.add(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.add(f"Project root: {PROJECT_ROOT}")

    required_files = [
        (PROJECT_ROOT / "app" / "paid_simulator" / "phase3_scenario_overlay_model.py", "Scenario-overlay model"),
        (PROJECT_ROOT / "app" / "paid_simulator" / "phase3_scenario_overlay_viewer.py", "Scenario-overlay viewer"),
        (PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_check.py", "Scenario-overlay model check"),
        (PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer.py", "Scenario-overlay viewer launcher"),
        (PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer_check.py", "Scenario-overlay viewer check"),
        (PROJECT_ROOT / "docs" / "paid_simulator_phase3_scenario_overlay_model.md", "Scenario-overlay model documentation"),
        (PROJECT_ROOT / "docs" / "paid_simulator_phase3_scenario_overlay_viewer.md", "Scenario-overlay viewer documentation"),
        (PROJECT_ROOT / "docs" / "paid_simulator_phase3_scenario_overlay_pipeline_check.md", "Scenario-overlay pipeline documentation"),
    ]

    report.section("Required Phase 3B files")
    for path, label in required_files:
        check_file(report, path, label, required=True)

    report.section("Running Phase 3B component checks")
    run_script(
        report,
        PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_check.py",
        "Scenario-overlay model check",
    )
    run_script(
        report,
        PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer_check.py",
        "Scenario-overlay viewer check",
    )

    expected_outputs = [
        (OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv", "Scenario-overlay CSV", True),
        (OUTPUT_REPORT_DIR / "phase3_scenario_overlay.html", "Scenario-overlay HTML", True),
        (OUTPUT_REPORT_DIR / "phase3_scenario_overlay_summary.txt", "Scenario-overlay text summary", True),
        (OUTPUT_TABLE_DIR / "phase3_interactive_payoff_snapshot.csv", "Optional interactive payoff snapshot CSV", False),
        (OUTPUT_REPORT_DIR / "phase3_interactive_payoff_snapshot.html", "Optional interactive payoff snapshot HTML", False),
    ]

    report.section("Expected Phase 3B outputs")
    for path, label, required in expected_outputs:
        check_file(report, path, label, required=required)

    report.section("CSV row checks")
    scenario_csv = OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv"
    rows = count_csv_rows(scenario_csv)
    if rows > 0:
        report.status("PASS", "phase3_scenario_overlay.csv", f"rows={rows}")
    else:
        report.status("FAIL", "phase3_scenario_overlay.csv", "No data rows found")

    snapshot_csv = OUTPUT_TABLE_DIR / "phase3_interactive_payoff_snapshot.csv"
    if snapshot_csv.exists():
        snapshot_rows = count_csv_rows(snapshot_csv)
        if snapshot_rows > 0:
            report.status("PASS", "optional phase3_interactive_payoff_snapshot.csv", f"rows={snapshot_rows}")
        else:
            report.status("REVIEW", "optional phase3_interactive_payoff_snapshot.csv", "File exists but has no data rows")
    else:
        report.status(
            "REVIEW",
            "optional phase3_interactive_payoff_snapshot.csv",
            "No snapshot yet; acceptable until a payoff setup is saved from the viewer",
        )

    report.add("")
    report.add("=" * 96)
    if report.has_failure:
        report.add("Overall Phase 3B scenario-overlay pipeline status: REVIEW")
        report.add("One or more required Phase 3B pipeline items need attention.")
        exit_code = 1
    elif report.has_review:
        report.add("Overall Phase 3B scenario-overlay pipeline status: PASS WITH OPTIONAL SNAPSHOT REVIEW")
        report.add("Only optional snapshot items require review. This is acceptable if no setup has been saved yet.")
        exit_code = 0
    else:
        report.add("Overall Phase 3B scenario-overlay pipeline status: PASS")
        exit_code = 0
    report.add("=" * 96)

    report.save()
    report.add(f"\nSaved pipeline report: {REPORT_PATH}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
