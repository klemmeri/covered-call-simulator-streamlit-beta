"""
run_paid_simulator_phase3_integration_readiness_check.py

Phase 3 integration-readiness checker for the Covered Call Simulator.

This script verifies that the Phase 3 interactive covered-call payoff
prototype is installed, testable, documented, and connected to the main
Developer-view dashboard.

It is intentionally conservative. It does not modify model files or dashboard
state. It only runs existing checks and verifies files, output reports, and
source markers.
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

REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = REPORT_DIR / "phase3_integration_readiness_report.txt"


class CheckRecorder:
    """Collects check results and formats a console/report summary."""

    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures = 0
        self.reviews = 0

    def write(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def section(self, title: str) -> None:
        self.write("\n" + title)
        self.write("-" * 96)

    def result(self, status: str, label: str, detail: str = "") -> None:
        status_upper = status.upper()
        if status_upper == "FAIL":
            self.failures += 1
        elif status_upper == "REVIEW":
            self.reviews += 1
        self.write(f"{status_upper:<10} {label:<52} {detail}")


def relative(path: Path) -> str:
    try:
        return str(path.relative_to(PROJECT_ROOT))
    except ValueError:
        return str(path)


def file_exists(rec: CheckRecorder, label: str, path: Path, required: bool = True) -> bool:
    exists = path.exists()
    if exists:
        rec.result("FOUND", label, str(path))
        return True
    rec.result("FAIL" if required else "REVIEW", label, f"Missing: {path}")
    return False


def read_text_safely(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        try:
            return path.read_text(errors="ignore")
        except Exception:
            return ""


def count_csv_rows(path: Path) -> int:
    if not path.exists():
        return 0
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        if not rows:
            return 0
        return max(0, len(rows) - 1)
    except Exception:
        return 0


def run_script(rec: CheckRecorder, label: str, script: Path, required: bool = True) -> bool:
    if not script.exists():
        rec.result("FAIL" if required else "REVIEW", label, f"Missing script: {script}")
        return False

    try:
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        rec.result("FAIL" if required else "REVIEW", label, "Timed out after 120 seconds")
        return False
    except Exception as exc:
        rec.result("FAIL" if required else "REVIEW", label, f"Could not run: {exc}")
        return False

    if completed.returncode == 0:
        rec.result("PASS", label, f"exit code {completed.returncode}")
        return True

    output_tail = "\n".join((completed.stdout + "\n" + completed.stderr).splitlines()[-8:])
    rec.result("FAIL" if required else "REVIEW", label, f"exit code {completed.returncode}")
    if output_tail:
        rec.write(output_tail)
    return False


def marker_check(
    rec: CheckRecorder,
    label: str,
    source_path: Path,
    markers: Iterable[str],
    required: bool = True,
) -> None:
    text = read_text_safely(source_path)
    for marker in markers:
        if marker in text:
            rec.result("PASS", f"{label} marker '{marker}'", marker)
        else:
            rec.result("FAIL" if required else "REVIEW", f"{label} marker '{marker}'", f"Missing in {relative(source_path)}")


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    rec = CheckRecorder()

    rec.write("=" * 96)
    rec.write("Phase 3 interactive payoff integration-readiness check")
    rec.write("=" * 96)
    rec.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rec.write(f"Project root: {PROJECT_ROOT}")

    rec.section("Required Phase 3 source files")
    required_files = [
        ("Phase 3 interactive payoff viewer", PROJECT_ROOT / "app" / "paid_simulator" / "phase3_interactive_payoff_viewer.py"),
        ("Main dashboard app", PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"),
        ("Main dashboard launcher", PROJECT_ROOT / "app" / "run_paid_simulator_form.py"),
    ]
    for label, path in required_files:
        file_exists(rec, label, path)

    rec.section("Required Phase 3 runner/check files")
    required_runners = [
        ("Phase 3 viewer launcher", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_interactive_payoff_viewer.py"),
        ("Phase 3 viewer check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_interactive_payoff_viewer_check.py"),
        ("Phase 3 pipeline check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_interactive_payoff_pipeline_check.py"),
        ("Phase 3 dashboard-tab check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_dashboard_tab_check.py"),
    ]
    for label, path in required_runners:
        file_exists(rec, label, path)

    rec.section("Phase 3 documentation")
    docs = [
        ("Phase 3 interactive payoff viewer", PROJECT_ROOT / "docs" / "paid_simulator_phase3_interactive_payoff_viewer.md"),
        ("Phase 3 interactive payoff pipeline", PROJECT_ROOT / "docs" / "paid_simulator_phase3_interactive_payoff_pipeline_check.md"),
        ("Phase 3 dashboard tab", PROJECT_ROOT / "docs" / "paid_simulator_phase3_dashboard_tab.md"),
        ("Phase 3 integration readiness", PROJECT_ROOT / "docs" / "paid_simulator_phase3_integration_readiness.md"),
    ]
    for label, path in docs:
        file_exists(rec, label, path)

    rec.section("Run Phase 3 checks")
    run_script(
        rec,
        "Phase 3 interactive payoff viewer check",
        PROJECT_ROOT / "app" / "run_paid_simulator_phase3_interactive_payoff_viewer_check.py",
    )
    run_script(
        rec,
        "Phase 3 interactive payoff pipeline check",
        PROJECT_ROOT / "app" / "run_paid_simulator_phase3_interactive_payoff_pipeline_check.py",
    )
    run_script(
        rec,
        "Phase 3 dashboard-tab check",
        PROJECT_ROOT / "app" / "run_paid_simulator_phase3_dashboard_tab_check.py",
    )

    rec.section("Expected Phase 3 reports and optional snapshots")
    expected_reports = [
        ("Phase 3 pipeline report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3_interactive_payoff_pipeline_report.txt", True),
    ]
    optional_outputs = [
        ("Phase 3 payoff snapshot CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase3_interactive_payoff_snapshot.csv", False),
        ("Phase 3 payoff snapshot HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3_interactive_payoff_snapshot.html", False),
    ]
    for label, path, required in expected_reports + optional_outputs:
        file_exists(rec, label, path, required=required)

    snapshot_csv = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase3_interactive_payoff_snapshot.csv"
    if snapshot_csv.exists():
        rows = count_csv_rows(snapshot_csv)
        if rows > 0:
            rec.result("PASS", "phase3_interactive_payoff_snapshot.csv", f"rows={rows}")
        else:
            rec.result("REVIEW", "phase3_interactive_payoff_snapshot.csv", "File exists but has no data rows")
    else:
        rec.result("REVIEW", "phase3_interactive_payoff_snapshot.csv", "Optional snapshot not yet created by viewer")

    rec.section("Main dashboard Phase 3 tab markers")
    dashboard = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    marker_check(
        rec,
        "Dashboard",
        dashboard,
        [
            "Phase 3 interactive payoff",
            "phase3_interactive_payoff_viewer",
            "run_paid_simulator_phase3_interactive_payoff_pipeline_check.py",
        ],
    )

    rec.section("Phase 3 viewer source markers")
    viewer = PROJECT_ROOT / "app" / "paid_simulator" / "phase3_interactive_payoff_viewer.py"
    marker_check(
        rec,
        "Viewer",
        viewer,
        [
            "Covered-call payoff",
            "Buy-and-hold",
            "Break-even",
            "Assignment",
        ],
        required=False,
    )

    rec.write("\n" + "=" * 96)
    if rec.failures == 0:
        status = "PASS"
        rec.write("Overall Phase 3 integration-readiness status: PASS")
        if rec.reviews:
            rec.write(f"Review notes: {rec.reviews} non-blocking item(s), usually optional snapshots or wording markers.")
    else:
        status = "REVIEW"
        rec.write("Overall Phase 3 integration-readiness status: REVIEW")
        rec.write("One or more Phase 3 integration items need attention.")
    rec.write("=" * 96)

    REPORT_PATH.write_text("\n".join(rec.lines), encoding="utf-8")
    rec.write(f"\nSaved integration-readiness report: {REPORT_PATH}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
