"""
run_paid_simulator_phase3d_integration_readiness_check.py

Phase 3D integrated payoff-overlay integration-readiness checker for the
Covered Call Strategy Stress Test project.

This checker verifies that the Phase 3D standalone integrated payoff-overlay
viewer, pipeline checker, Developer-view dashboard tab, supporting context, and
project documentation are connected. Saved Phase 3D snapshot outputs are treated
as optional because they are created only after opening the viewer and saving a
setup.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = OUTPUT_REPORT_DIR / "phase3d_integration_readiness_report.txt"


class CheckRecorder:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures = 0
        self.optional_reviews = 0

    def emit(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def section(self, title: str) -> None:
        self.emit("\n" + title)
        self.emit("-" * 96)

    def status(self, status: str, label: str, detail: str = "") -> None:
        status = status.upper()
        self.emit(f"{status:<10} {label:<60} {detail}")
        if status in {"MISSING", "FAIL", "ERROR", "REVIEW"}:
            self.failures += 1
        elif status == "OPTIONAL":
            self.optional_reviews += 1


def path_label(path: Path) -> str:
    return str(path)


def check_exists(rec: CheckRecorder, label: str, path: Path, optional: bool = False) -> bool:
    if path.exists():
        rec.status("FOUND", label, path_label(path))
        return True
    if optional:
        rec.status("OPTIONAL", label, path_label(path))
    else:
        rec.status("MISSING", label, path_label(path))
    return False


def check_csv_rows(rec: CheckRecorder, label: str, path: Path, optional: bool = False) -> bool:
    if not path.exists():
        if optional:
            rec.status("OPTIONAL", label, "file not available or unreadable")
        else:
            rec.status("MISSING", label, path_label(path))
        return False
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle))
        data_rows = max(len(rows) - 1, 0)
        if data_rows > 0:
            rec.status("PASS", label, f"rows={data_rows}")
            return True
        if optional:
            rec.status("OPTIONAL", label, "file exists but has no data rows")
        else:
            rec.status("REVIEW", label, "file exists but has no data rows")
        return False
    except Exception as exc:
        if optional:
            rec.status("OPTIONAL", label, f"file not available or unreadable: {exc}")
        else:
            rec.status("ERROR", label, str(exc))
        return False


def run_child_check(rec: CheckRecorder, label: str, script_path: Path) -> bool:
    if not script_path.exists():
        rec.status("MISSING", label, path_label(script_path))
        return False

    rec.status("RUN", label, path_label(script_path))
    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
            check=False,
            timeout=180,
        )
    except subprocess.TimeoutExpired:
        rec.status("ERROR", label, "Timed out after 180 seconds")
        return False
    except Exception as exc:
        rec.status("ERROR", label, str(exc))
        return False

    combined = (completed.stdout or "") + "\n" + (completed.stderr or "")
    for line in combined.strip().splitlines()[-10:]:
        rec.emit(f"  output: {line}")

    if completed.returncode == 0:
        rec.status("PASS", label, f"exit code {completed.returncode}")
        return True

    rec.status("FAIL", label, f"exit code {completed.returncode}")
    return False


def source_contains_any(path: Path, markers: Iterable[str]) -> Optional[str]:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    for marker in markers:
        if marker.lower() in text:
            return marker
    return None


def check_source_marker(rec: CheckRecorder, label: str, path: Path, markers: Iterable[str]) -> bool:
    found = source_contains_any(path, markers)
    if found:
        rec.status("PASS", label, found)
        return True
    rec.status("REVIEW", label, "none of the accepted markers were found")
    return False


def main() -> int:
    rec = CheckRecorder()
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rec.emit("=" * 96)
    rec.emit("Phase 3D integrated overlay integration-readiness check")
    rec.emit("=" * 96)
    rec.emit(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rec.emit(f"Project root: {PROJECT_ROOT}")

    rec.section("Required Phase 3D files")
    required_files = [
        ("Phase 3D integrated viewer app", PAID_SIMULATOR_DIR / "phase3d_integrated_payoff_overlay_viewer.py"),
        ("Phase 3D integrated viewer launcher", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer.py"),
        ("Phase 3D integrated viewer check", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer_check.py"),
        ("Phase 3D integrated overlay pipeline check", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py"),
        ("Phase 3D dashboard-tab check", APP_DIR / "run_paid_simulator_phase3d_dashboard_tab_check.py"),
        ("Main dashboard app", PAID_SIMULATOR_DIR / "config_form_app.py"),
        ("Main dashboard launcher", APP_DIR / "run_paid_simulator_form.py"),
    ]
    for label, path in required_files:
        check_exists(rec, label, path)

    rec.section("Phase 3D documentation")
    docs = [
        ("Phase 3D integrated viewer documentation", DOCS_DIR / "paid_simulator_phase3d_integrated_payoff_overlay_viewer.md"),
        ("Phase 3D pipeline documentation", DOCS_DIR / "paid_simulator_phase3d_integrated_overlay_pipeline_check.md"),
        ("Phase 3D dashboard-tab documentation", DOCS_DIR / "paid_simulator_phase3d_dashboard_tab.md"),
    ]
    for label, path in docs:
        check_exists(rec, label, path)

    rec.section("Required Phase 3B / Phase 3C context")
    context_files = [
        ("Phase 3B scenario-overlay CSV", OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv"),
        ("Phase 3B scenario-overlay HTML", OUTPUT_REPORT_DIR / "phase3_scenario_overlay.html"),
        ("Phase 3B scenario-overlay summary", OUTPUT_REPORT_DIR / "phase3_scenario_overlay_summary.txt"),
        ("Phase 3B checkpoint report", OUTPUT_REPORT_DIR / "phase3b_checkpoint_report.txt"),
        ("Phase 3C checkpoint report", OUTPUT_REPORT_DIR / "phase3c_checkpoint_report.txt"),
    ]
    for label, path in context_files:
        check_exists(rec, label, path)

    rec.section("Executing Phase 3D checks")
    scripts = [
        ("Phase 3D integrated viewer check", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer_check.py"),
        ("Phase 3D integrated overlay pipeline check", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py"),
        ("Phase 3D dashboard-tab check", APP_DIR / "run_paid_simulator_phase3d_dashboard_tab_check.py"),
    ]
    for label, script_path in scripts:
        run_child_check(rec, label, script_path)

    rec.section("CSV row checks")
    check_csv_rows(rec, "phase3_scenario_overlay.csv", OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv")
    check_csv_rows(
        rec,
        "phase3d_integrated_payoff_overlay_snapshot.csv",
        OUTPUT_TABLE_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv",
        optional=True,
    )

    rec.section("Optional Phase 3D saved snapshot outputs")
    optional_files = [
        ("Phase 3D integrated snapshot CSV", OUTPUT_TABLE_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv"),
        ("Phase 3D integrated snapshot HTML", OUTPUT_REPORT_DIR / "phase3d_integrated_payoff_overlay_snapshot.html"),
    ]
    for label, path in optional_files:
        check_exists(rec, label, path, optional=True)

    rec.section("Main dashboard Phase 3D tab markers")
    dashboard_path = PAID_SIMULATOR_DIR / "config_form_app.py"
    dashboard_markers = [
        ("Dashboard marker 'Phase 3 interactive payoff'", ["Phase 3 interactive payoff"]),
        ("Dashboard marker 'Phase 3B scenario overlay'", ["Phase 3B scenario overlay"]),
        ("Dashboard marker 'Phase 3C rich payoff'", ["Phase 3C rich payoff"]),
        ("Dashboard marker 'Phase 3D integrated overlay'", ["Phase 3D integrated overlay"]),
        (
            "Dashboard marker 'Phase 3D integrated viewer launcher'",
            [
                "phase3d_integrated_payoff_overlay_viewer",
                "run_paid_simulator_phase3d_integrated_overlay_viewer.py",
                "Phase 3D integrated viewer",
                "Open standalone Phase 3D",
                "integrated overlay viewer",
            ],
        ),
        (
            "Dashboard marker 'run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py'",
            ["run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py"],
        ),
    ]
    for label, markers in dashboard_markers:
        check_source_marker(rec, label, dashboard_path, markers)

    rec.emit("\n" + "=" * 96)
    if rec.failures == 0:
        if rec.optional_reviews:
            final_status = "PASS WITH OPTIONAL SNAPSHOT REVIEW"
            rec.emit(f"Overall Phase 3D integration-readiness status: {final_status}")
            rec.emit("Only optional snapshot items require review. This is acceptable if no Phase 3D setup has been saved yet.")
        else:
            final_status = "PASS"
            rec.emit(f"Overall Phase 3D integration-readiness status: {final_status}")
        exit_code = 0
    else:
        final_status = "REVIEW"
        rec.emit(f"Overall Phase 3D integration-readiness status: {final_status}")
        rec.emit("One or more required Phase 3D integration-readiness items need attention.")
        exit_code = 1
    rec.emit("=" * 96)

    REPORT_PATH.write_text("\n".join(rec.lines) + "\n", encoding="utf-8")
    rec.emit(f"\nSaved integration-readiness report: {REPORT_PATH}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
