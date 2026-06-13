"""
run_paid_simulator_phase3_checkpoint_check.py

Phase 3 interactive payoff checkpoint check for the Covered Call Strategy
Stress Test paid simulator project.

This script verifies that the first Phase 3 interactive payoff layer is
installed, connected, and ready for the next development step.
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

OUTPUT_REPORT = (
    PROJECT_ROOT
    / "outputs"
    / "reports"
    / "paid_simulator"
    / "phase3_checkpoint_report.txt"
)


class CheckLog:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failure_count = 0
        self.review_count = 0

    def add(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def header(self, title: str) -> None:
        line = "=" * 96
        self.add(line)
        self.add(title)
        self.add(line)

    def section(self, title: str) -> None:
        self.add("")
        self.add(title)
        self.add("-" * 96)

    def status(self, status: str, label: str, detail: str = "") -> None:
        status = status.upper()
        if status in {"MISSING", "FAIL", "ERROR"}:
            self.failure_count += 1
        elif status == "REVIEW":
            self.review_count += 1
        self.add(f"{status:<10} {label:<52} {detail}")


def exists_file(path: Path) -> bool:
    return path.exists() and path.is_file()


def csv_row_count(path: Path) -> int:
    if not exists_file(path):
        return 0
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        if not rows:
            return 0
        return max(len(rows) - 1, 0)
    except Exception:
        return 0


def read_text_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def run_script(script: Path, log: CheckLog, label: str) -> None:
    if not exists_file(script):
        log.status("MISSING", label, str(script))
        return

    try:
        completed = subprocess.run(
            [sys.executable, str(script)],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except Exception as exc:
        log.status("ERROR", label, f"Could not run script: {exc}")
        return

    if completed.returncode == 0:
        log.status("PASS", label, "exit code 0")
    else:
        detail = f"exit code {completed.returncode}"
        if completed.stderr.strip():
            detail += f" | stderr: {completed.stderr.strip().splitlines()[-1]}"
        log.status("FAIL", label, detail)


def check_required_files(log: CheckLog, items: list[tuple[str, Path]]) -> None:
    for label, path in items:
        if exists_file(path):
            log.status("FOUND", label, str(path))
        else:
            log.status("MISSING", label, str(path))


def main() -> int:
    log = CheckLog()
    log.header("Phase 3 interactive payoff checkpoint check")
    log.add(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.add(f"Project root: {PROJECT_ROOT}")

    app = PROJECT_ROOT / "app"
    paid = app / "paid_simulator"
    docs = PROJECT_ROOT / "docs"
    outputs_tables = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
    outputs_reports = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

    log.section("Required Phase 3 source files")
    required_sources = [
        ("Phase 3 interactive payoff viewer", paid / "phase3_interactive_payoff_viewer.py"),
        ("Main dashboard app", paid / "config_form_app.py"),
        ("Main dashboard launcher", app / "run_paid_simulator_form.py"),
    ]
    check_required_files(log, required_sources)

    log.section("Required Phase 3 runner/check files")
    required_runners = [
        ("Phase 3 viewer launcher", app / "run_paid_simulator_phase3_interactive_payoff_viewer.py"),
        ("Phase 3 viewer check", app / "run_paid_simulator_phase3_interactive_payoff_viewer_check.py"),
        ("Phase 3 pipeline check", app / "run_paid_simulator_phase3_interactive_payoff_pipeline_check.py"),
        ("Phase 3 dashboard-tab check", app / "run_paid_simulator_phase3_dashboard_tab_check.py"),
        ("Phase 3 integration-readiness check", app / "run_paid_simulator_phase3_integration_readiness_check.py"),
        ("Phase 2G checkpoint context", app / "run_paid_simulator_phase2g_checkpoint_check.py"),
    ]
    check_required_files(log, required_runners)

    log.section("Phase 3 documentation")
    required_docs = [
        ("Interactive payoff viewer", docs / "paid_simulator_phase3_interactive_payoff_viewer.md"),
        ("Interactive payoff pipeline", docs / "paid_simulator_phase3_interactive_payoff_pipeline_check.md"),
        ("Phase 3 dashboard tab", docs / "paid_simulator_phase3_dashboard_tab.md"),
        ("Phase 3 integration readiness", docs / "paid_simulator_phase3_integration_readiness.md"),
        ("Phase 3 checkpoint summary", docs / "paid_simulator_phase3_checkpoint_summary.md"),
    ]
    check_required_files(log, required_docs)

    log.section("Execute Phase 3 checks")
    run_script(app / "run_paid_simulator_phase3_interactive_payoff_viewer_check.py", log, "Run Phase 3 viewer check")
    run_script(app / "run_paid_simulator_phase3_interactive_payoff_pipeline_check.py", log, "Run Phase 3 pipeline check")
    run_script(app / "run_paid_simulator_phase3_dashboard_tab_check.py", log, "Run Phase 3 dashboard-tab check")
    run_script(app / "run_paid_simulator_phase3_integration_readiness_check.py", log, "Run Phase 3 integration-readiness check")

    log.section("Optional Phase 3 saved payoff snapshot outputs")
    optional_outputs = [
        ("Interactive payoff snapshot CSV", outputs_tables / "phase3_interactive_payoff_snapshot.csv"),
        ("Interactive payoff snapshot HTML", outputs_reports / "phase3_interactive_payoff_snapshot.html"),
    ]
    for label, path in optional_outputs:
        if exists_file(path):
            log.status("FOUND", label, str(path))
        else:
            log.status("REVIEW", label, "Optional. Created after saving/exporting a setup in the Phase 3 viewer.")

    log.section("Optional snapshot row checks")
    snapshot_csv = outputs_tables / "phase3_interactive_payoff_snapshot.csv"
    if exists_file(snapshot_csv):
        rows = csv_row_count(snapshot_csv)
        if rows > 0:
            log.status("PASS", "phase3_interactive_payoff_snapshot.csv", f"rows={rows}")
        else:
            log.status("REVIEW", "phase3_interactive_payoff_snapshot.csv", "File exists but has no data rows.")
    else:
        log.status("REVIEW", "phase3_interactive_payoff_snapshot.csv", "Optional snapshot has not been created yet.")

    log.section("Main dashboard Phase 3 tab markers")
    dashboard_text = read_text_safe(paid / "config_form_app.py")
    markers = [
        "Phase 3 interactive payoff",
        "phase3_interactive_payoff_viewer",
        "run_paid_simulator_phase3_interactive_payoff_pipeline_check.py",
    ]
    for marker in markers:
        if marker in dashboard_text:
            log.status("PASS", f"Dashboard marker '{marker}'", marker)
        else:
            log.status("MISSING", f"Dashboard marker '{marker}'", "Not found in config_form_app.py")

    log.add("")
    log.header("Phase 3 checkpoint result")
    if log.failure_count > 0:
        log.add("Overall Phase 3 checkpoint status: FAIL")
        exit_code = 1
    else:
        if log.review_count > 0:
            log.add("Overall Phase 3 checkpoint status: PASS WITH OPTIONAL SNAPSHOT REVIEW")
            log.add("Only optional snapshot items require review. This is acceptable if no setup has been saved yet.")
        else:
            log.add("Overall Phase 3 checkpoint status: PASS")
        exit_code = 0

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text("\n".join(log.lines), encoding="utf-8")
    log.add("")
    log.add(f"Saved checkpoint report: {OUTPUT_REPORT}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
