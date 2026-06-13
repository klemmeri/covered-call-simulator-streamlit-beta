"""
run_paid_simulator_phase3b_integration_readiness_check.py

Integration-readiness checker for Phase 3B of the Covered Call Simulator.

Phase 3B adds scenario-overlay analysis to the Phase 3 interactive payoff
prototype. This checker verifies that the model, viewer, pipeline checker,
dashboard tab, outputs, reports, and documentation are present and connected.

This script is intentionally read/check oriented. It does not modify the main
simulator logic. It may run existing Phase 3B check scripts to refresh outputs.
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
REPORT_PATH = REPORT_DIR / "phase3b_integration_readiness_report.txt"


class CheckLog:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.blocking_failures = 0
        self.optional_reviews = 0

    def add(self, line: str = "") -> None:
        self.lines.append(line)
        print(line)

    def section(self, title: str) -> None:
        self.add("")
        self.add(title)
        self.add("-" * 96)

    def item(self, status: str, label: str, detail: str = "", blocking: bool = True) -> None:
        if status == "FAIL" and blocking:
            self.blocking_failures += 1
        if status == "REVIEW":
            self.optional_reviews += 1
        self.add(f"{status:<10} {label:<52} {detail}")


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def count_csv_rows(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return 0
        return max(0, len(rows) - 1)
    except Exception:
        return 0


def run_script(log: CheckLog, label: str, script_path: Path) -> None:
    if not script_path.exists():
        log.item("FAIL", label, f"Missing: {script_path}")
        return

    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        log.item("PASS", label, f"Exit code {result.returncode}")
    else:
        combined = (result.stdout or "") + "\n" + (result.stderr or "")
        if "PASS WITH OPTIONAL SNAPSHOT REVIEW" in combined:
            log.item("REVIEW", label, "Optional snapshot review only; acceptable before saved setup", blocking=False)
        else:
            log.item("FAIL", label, f"Exit code {result.returncode}")


def check_file(log: CheckLog, label: str, path: Path, optional: bool = False) -> None:
    if path.exists():
        log.item("FOUND", label, str(path), blocking=not optional)
    else:
        if optional:
            log.item("REVIEW", label, f"Optional missing: {path}", blocking=False)
        else:
            log.item("FAIL", label, f"Missing: {path}")


def check_csv(log: CheckLog, label: str, path: Path, optional: bool = False) -> None:
    if not path.exists():
        if optional:
            log.item("REVIEW", label, f"Optional missing: {path}", blocking=False)
        else:
            log.item("FAIL", label, f"Missing: {path}")
        return

    rows = count_csv_rows(path)
    if rows > 0:
        log.item("PASS", label, f"rows={rows}")
    else:
        if optional:
            log.item("REVIEW", label, "Optional CSV exists but has no data rows", blocking=False)
        else:
            log.item("FAIL", label, "CSV has no data rows")


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    log = CheckLog()
    log.add("=" * 96)
    log.add("Phase 3B scenario-overlay integration-readiness check")
    log.add("=" * 96)
    log.add(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.add(f"Project root: {PROJECT_ROOT}")

    log.section("Required Phase 3B source/viewer files")
    required_files = [
        ("Scenario-overlay model", PROJECT_ROOT / "app" / "paid_simulator" / "phase3_scenario_overlay_model.py"),
        ("Scenario-overlay viewer", PROJECT_ROOT / "app" / "paid_simulator" / "phase3_scenario_overlay_viewer.py"),
        ("Main dashboard app", PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"),
        ("Main dashboard launcher", PROJECT_ROOT / "app" / "run_paid_simulator_form.py"),
    ]
    for label, path in required_files:
        check_file(log, label, path)

    log.section("Required Phase 3B runner/check files")
    runner_files = [
        ("Scenario-overlay model check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_check.py"),
        ("Scenario-overlay viewer launcher", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer.py"),
        ("Scenario-overlay viewer check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer_check.py"),
        ("Scenario-overlay pipeline check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_pipeline_check.py"),
        ("Scenario-overlay dashboard-tab check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3b_dashboard_tab_check.py"),
    ]
    for label, path in runner_files:
        check_file(log, label, path)

    log.section("Run Phase 3B checks")
    run_script(log, "Scenario-overlay model check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_check.py")
    run_script(log, "Scenario-overlay viewer check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer_check.py")
    run_script(log, "Scenario-overlay pipeline check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_pipeline_check.py")
    run_script(log, "Scenario-overlay dashboard-tab check", PROJECT_ROOT / "app" / "run_paid_simulator_phase3b_dashboard_tab_check.py")

    log.section("Expected Phase 3B generated outputs")
    check_csv(log, "Scenario-overlay CSV", TABLE_DIR / "phase3_scenario_overlay.csv")
    check_file(log, "Scenario-overlay HTML", REPORT_DIR / "phase3_scenario_overlay.html")
    check_file(log, "Scenario-overlay text summary", REPORT_DIR / "phase3_scenario_overlay_summary.txt")
    check_file(log, "Scenario-overlay pipeline report", REPORT_DIR / "phase3b_scenario_overlay_pipeline_report.txt")
    check_csv(log, "Interactive payoff snapshot CSV", TABLE_DIR / "phase3_interactive_payoff_snapshot.csv", optional=True)
    check_file(log, "Interactive payoff snapshot HTML", REPORT_DIR / "phase3_interactive_payoff_snapshot.html", optional=True)

    log.section("Phase 3B documentation")
    docs = [
        ("Scenario-overlay model", PROJECT_ROOT / "docs" / "paid_simulator_phase3_scenario_overlay_model.md"),
        ("Scenario-overlay viewer", PROJECT_ROOT / "docs" / "paid_simulator_phase3_scenario_overlay_viewer.md"),
        ("Scenario-overlay pipeline", PROJECT_ROOT / "docs" / "paid_simulator_phase3_scenario_overlay_pipeline_check.md"),
        ("Scenario-overlay dashboard tab", PROJECT_ROOT / "docs" / "paid_simulator_phase3b_dashboard_tab.md"),
        ("Scenario-overlay integration readiness", PROJECT_ROOT / "docs" / "paid_simulator_phase3b_integration_readiness.md"),
    ]
    for label, path in docs:
        check_file(log, label, path)

    log.section("Main dashboard Phase 3B tab markers")
    dashboard_path = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
    dashboard_text = read_text_safe(dashboard_path)
    markers = [
        "Phase 3B scenario overlay",
        "phase3_scenario_overlay_viewer",
        "run_paid_simulator_phase3_scenario_overlay_pipeline_check.py",
        "phase3_scenario_overlay.csv",
    ]
    for marker in markers:
        if marker in dashboard_text:
            log.item("PASS", f"Dashboard marker '{marker}'", marker)
        else:
            log.item("FAIL", f"Dashboard marker '{marker}'", "Missing from main dashboard source")

    log.add("")
    log.add("=" * 96)
    if log.blocking_failures == 0 and log.optional_reviews == 0:
        status = "PASS"
        log.add("Overall Phase 3B integration-readiness status: PASS")
    elif log.blocking_failures == 0:
        status = "PASS WITH OPTIONAL SNAPSHOT REVIEW"
        log.add("Overall Phase 3B integration-readiness status: PASS WITH OPTIONAL SNAPSHOT REVIEW")
        log.add("Only optional snapshot items require review. This is acceptable if no setup has been saved yet.")
    else:
        status = "FAIL"
        log.add("Overall Phase 3B integration-readiness status: FAIL")
        log.add("One or more required Phase 3B integration items are missing or failed.")
    log.add("=" * 96)

    REPORT_PATH.write_text("\n".join(log.lines), encoding="utf-8")
    log.add(f"\nSaved integration-readiness report: {REPORT_PATH}")

    return 0 if status in {"PASS", "PASS WITH OPTIONAL SNAPSHOT REVIEW"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
