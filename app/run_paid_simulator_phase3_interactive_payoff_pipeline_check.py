"""
run_paid_simulator_phase3_interactive_payoff_pipeline_check.py

Phase 3 interactive covered-call payoff pipeline checker.

This script verifies that the first Phase 3 graphical payoff prototype is
installed and that its checker can run successfully. It intentionally treats
interactive output snapshots as optional, because those files are created only
after the user opens the Streamlit viewer and enters/saves a setup.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

REPORT_PATH = OUTPUT_REPORTS_DIR / "phase3_interactive_payoff_pipeline_report.txt"


class CheckLog:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures = 0
        self.reviews = 0

    def add(self, line: str = "") -> None:
        self.lines.append(line)
        print(line)

    def section(self, title: str) -> None:
        self.add("")
        self.add(title)
        self.add("-" * 96)

    def item(self, status: str, label: str, detail: str = "") -> None:
        if status == "FAIL":
            self.failures += 1
        elif status == "REVIEW":
            self.reviews += 1
        self.add(f"{status:<10} {label:<55} {detail}")


def row_count_csv(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            rows = list(reader)
    except Exception:
        return -1
    if not rows:
        return 0
    return max(len(rows) - 1, 0)


def run_script(script_path: Path, log: CheckLog, label: str) -> None:
    if not script_path.exists():
        log.item("FAIL", label, f"Missing: {script_path}")
        return

    log.item("FOUND", label, str(script_path))
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        log.item("FAIL", f"{label} execution", "Timed out after 180 seconds")
        return
    except Exception as exc:
        log.item("FAIL", f"{label} execution", str(exc))
        return

    if result.returncode == 0:
        log.item("PASS", f"{label} execution", "Exit code 0")
    else:
        log.item("FAIL", f"{label} execution", f"Exit code {result.returncode}")
        tail = (result.stdout + "\n" + result.stderr).strip().splitlines()[-8:]
        for line in tail:
            log.add(f"    {line}")


def require_file(log: CheckLog, label: str, path: Path) -> None:
    if path.exists():
        log.item("FOUND", label, str(path))
    else:
        log.item("FAIL", label, f"Missing: {path}")


def optional_file(log: CheckLog, label: str, path: Path) -> None:
    if path.exists():
        log.item("FOUND", label, str(path))
    else:
        log.item("INFO", label, f"Optional file not created yet: {path}")


def check_csv_rows(log: CheckLog, label: str, path: Path, required: bool) -> None:
    if not path.exists():
        if required:
            log.item("FAIL", label, f"Missing: {path}")
        else:
            log.item("INFO", label, "Optional CSV not created yet")
        return

    rows = row_count_csv(path)
    if rows > 0:
        log.item("PASS", label, f"rows={rows}")
    elif rows == 0:
        status = "REVIEW" if required else "INFO"
        log.item(status, label, "CSV exists but has no data rows")
    else:
        status = "FAIL" if required else "INFO"
        log.item(status, label, "CSV exists but could not be read")


def main() -> int:
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    log = CheckLog()
    log.add("=" * 96)
    log.add("Phase 3 interactive covered-call payoff pipeline check")
    log.add("=" * 96)
    log.add(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.add(f"Project root: {PROJECT_ROOT}")

    log.section("Required Phase 3 interactive payoff files")
    require_file(
        log,
        "Phase 3 interactive payoff viewer",
        PAID_SIMULATOR_DIR / "phase3_interactive_payoff_viewer.py",
    )
    require_file(
        log,
        "Phase 3 viewer launcher",
        APP_DIR / "run_paid_simulator_phase3_interactive_payoff_viewer.py",
    )
    require_file(
        log,
        "Phase 3 viewer check",
        APP_DIR / "run_paid_simulator_phase3_interactive_payoff_viewer_check.py",
    )
    require_file(
        log,
        "Phase 3 viewer documentation",
        DOCS_DIR / "paid_simulator_phase3_interactive_payoff_viewer.md",
    )

    log.section("Pipeline dependency checks")
    run_script(
        APP_DIR / "run_paid_simulator_phase2g_checkpoint_check.py",
        log,
        "Phase 2G checkpoint check",
    )
    run_script(
        APP_DIR / "run_paid_simulator_phase3_interactive_payoff_viewer_check.py",
        log,
        "Phase 3 interactive payoff viewer check",
    )

    log.section("Optional interactive viewer outputs")
    snapshot_csv = OUTPUT_TABLES_DIR / "phase3_interactive_payoff_snapshot.csv"
    snapshot_html = OUTPUT_REPORTS_DIR / "phase3_interactive_payoff_snapshot.html"
    optional_file(log, "Interactive payoff snapshot CSV", snapshot_csv)
    optional_file(log, "Interactive payoff snapshot HTML", snapshot_html)
    check_csv_rows(log, "phase3_interactive_payoff_snapshot.csv", snapshot_csv, required=False)

    log.section("Phase 3 pipeline documentation")
    require_file(
        log,
        "Phase 3 pipeline documentation",
        DOCS_DIR / "paid_simulator_phase3_interactive_payoff_pipeline_check.md",
    )

    log.add("")
    log.add("=" * 96)
    if log.failures == 0 and log.reviews == 0:
        log.add("Overall Phase 3 interactive payoff pipeline status: PASS")
        exit_code = 0
    elif log.failures == 0:
        log.add("Overall Phase 3 interactive payoff pipeline status: REVIEW")
        exit_code = 1
    else:
        log.add("Overall Phase 3 interactive payoff pipeline status: FAIL")
        exit_code = 1
    log.add("=" * 96)

    REPORT_PATH.write_text("\n".join(log.lines) + "\n", encoding="utf-8")
    log.add(f"Saved pipeline report: {REPORT_PATH}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
