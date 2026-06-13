"""
run_paid_simulator_phase3c_integration_readiness_check.py

Phase 3C rich payoff integration-readiness checker for the Covered Call
Simulator paid dashboard.

This checker is intentionally conservative. It verifies that the Phase 3C
richer graphical payoff layer is installed, connected to the Developer-view
main dashboard, and able to run its own local checks. Snapshot outputs are
non-blocking because they are created only after a user opens the Phase 3C
viewer and saves/exports a setup.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_APP_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = OUTPUT_REPORTS_DIR / "phase3c_integration_readiness_report.txt"


class CheckRecorder:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str, str]] = []
        self.blocking_failures = 0
        self.optional_reviews = 0

    def add(self, status: str, label: str, detail: str = "") -> None:
        status = status.upper()
        self.rows.append((status, label, detail))
        if status in {"MISSING", "FAIL", "ERROR"}:
            self.blocking_failures += 1
        elif status in {"OPTIONAL", "REVIEW"}:
            self.optional_reviews += 1

    def print_section(self, title: str) -> None:
        print("\n" + title)
        print("-" * 96)

    def print_row(self, status: str, label: str, detail: str = "") -> None:
        print(f"{status:<10} {label:<48} {detail}")

    def add_and_print(self, status: str, label: str, detail: str = "") -> None:
        self.add(status, label, detail)
        self.print_row(status, label, detail)

    def final_status(self) -> str:
        if self.blocking_failures:
            return "REVIEW"
        if self.optional_reviews:
            return "PASS WITH OPTIONAL SNAPSHOT REVIEW"
        return "PASS"


def path_status(path: Path) -> tuple[str, str]:
    if path.exists():
        return "FOUND", str(path)
    return "MISSING", str(path)


def optional_path_status(path: Path) -> tuple[str, str]:
    if path.exists():
        return "FOUND", str(path)
    return "OPTIONAL", f"Not found yet: {path}"


def csv_row_count(path: Path) -> int:
    if not path.exists():
        return -1
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
        if not rows:
            return 0
        return max(0, len(rows) - 1)
    except Exception:
        return -1


def run_script(script_path: Path) -> tuple[str, str]:
    if not script_path.exists():
        return "MISSING", str(script_path)
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "ERROR", "Timed out after 120 seconds"
    except Exception as exc:
        return "ERROR", str(exc)

    combined_output = (result.stdout or "") + "\n" + (result.stderr or "")
    last_lines = "\n".join(combined_output.strip().splitlines()[-8:])
    if result.returncode == 0:
        return "PASS", last_lines
    return "FAIL", last_lines


def file_contains(path: Path, text: str) -> bool:
    if not path.exists():
        return False
    try:
        return text in path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False


def write_report(recorder: CheckRecorder, final_status: str) -> None:
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "Phase 3C rich payoff integration-readiness report",
        "=" * 80,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Project root: {PROJECT_ROOT}",
        "",
    ]
    for status, label, detail in recorder.rows:
        lines.append(f"{status:<10} {label:<48} {detail}")
    lines.extend([
        "",
        "=" * 80,
        f"Overall Phase 3C integration-readiness status: {final_status}",
    ])
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    recorder = CheckRecorder()

    print("=" * 96)
    print("Phase 3C rich payoff integration-readiness check")
    print("=" * 96)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {PROJECT_ROOT}")

    required_files = [
        ("Phase 3C rich payoff viewer", PAID_APP_DIR / "phase3c_rich_payoff_viewer.py"),
        ("Phase 3C viewer launcher", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer.py"),
        ("Phase 3C viewer check", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer_check.py"),
        ("Phase 3C pipeline check", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_pipeline_check.py"),
        ("Phase 3C dashboard-tab check", APP_DIR / "run_paid_simulator_phase3c_dashboard_tab_check.py"),
        ("Main dashboard app", PAID_APP_DIR / "config_form_app.py"),
        ("Phase 3C viewer documentation", DOCS_DIR / "paid_simulator_phase3c_rich_payoff_viewer.md"),
        ("Phase 3C pipeline documentation", DOCS_DIR / "paid_simulator_phase3c_rich_payoff_pipeline_check.md"),
        ("Phase 3C dashboard-tab documentation", DOCS_DIR / "paid_simulator_phase3c_dashboard_tab.md"),
    ]

    recorder.print_section("Required Phase 3C files")
    for label, path in required_files:
        status, detail = path_status(path)
        recorder.add_and_print(status, label, detail)

    recorder.print_section("Executing Phase 3C checks")
    scripts_to_run = [
        ("Phase 3C viewer check", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_viewer_check.py"),
        ("Phase 3C pipeline check", APP_DIR / "run_paid_simulator_phase3c_rich_payoff_pipeline_check.py"),
        ("Phase 3C dashboard-tab check", APP_DIR / "run_paid_simulator_phase3c_dashboard_tab_check.py"),
    ]
    for label, script in scripts_to_run:
        status, detail = run_script(script)
        recorder.add_and_print(status, label, detail.replace("\n", " | "))

    recorder.print_section("Main dashboard Phase 3C tab markers")
    dashboard = PAID_APP_DIR / "config_form_app.py"
    markers = [
        "Phase 3 interactive payoff",
        "Phase 3B scenario overlay",
        "Phase 3C rich payoff",
        "phase3c_rich_payoff_viewer",
        "run_paid_simulator_phase3c_rich_payoff_pipeline_check.py",
    ]
    for marker in markers:
        if file_contains(dashboard, marker):
            recorder.add_and_print("PASS", f"Dashboard marker '{marker}'", marker)
        else:
            recorder.add_and_print("MISSING", f"Dashboard marker '{marker}'", marker)

    recorder.print_section("Expected or optional Phase 3C outputs")
    optional_outputs = [
        ("Phase 3C rich payoff snapshot CSV", OUTPUT_TABLES_DIR / "phase3c_rich_payoff_snapshot.csv"),
        ("Phase 3C rich payoff snapshot HTML", OUTPUT_REPORTS_DIR / "phase3c_rich_payoff_snapshot.html"),
    ]
    for label, path in optional_outputs:
        status, detail = optional_path_status(path)
        recorder.add_and_print(status, label, detail)

    if (OUTPUT_TABLES_DIR / "phase3c_rich_payoff_snapshot.csv").exists():
        rows = csv_row_count(OUTPUT_TABLES_DIR / "phase3c_rich_payoff_snapshot.csv")
        if rows > 0:
            recorder.add_and_print("PASS", "phase3c_rich_payoff_snapshot.csv", f"rows={rows}")
        else:
            recorder.add_and_print("REVIEW", "phase3c_rich_payoff_snapshot.csv", f"rows={rows}")

    final_status = recorder.final_status()
    print("\n" + "=" * 96)
    print(f"Overall Phase 3C integration-readiness status: {final_status}")
    if final_status == "PASS WITH OPTIONAL SNAPSHOT REVIEW":
        print("Only optional snapshot items require review. This is acceptable if no Phase 3C setup has been saved yet.")
    elif final_status == "REVIEW":
        print("One or more Phase 3C integration items need attention.")
    print("=" * 96)

    write_report(recorder, final_status)
    print(f"\nSaved integration-readiness report: {REPORT_PATH}")

    return 1 if final_status == "REVIEW" else 0


if __name__ == "__main__":
    raise SystemExit(main())
