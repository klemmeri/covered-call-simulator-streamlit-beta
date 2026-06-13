"""
run_paid_simulator_phase3d_checkpoint_check.py

Checkpoint checker for Phase 3D: Integrated payoff-overlay interface.

This script verifies that the Phase 3D integrated payoff-overlay viewer layer
is installed, that the supporting Phase 3B/3C context is present, that the
pipeline/integration checks have produced reports, and that the main dashboard
contains the Phase 3D Developer-view markers.

Saved Phase 3D snapshot files are optional because they are created only after
opening the Phase 3D viewer and saving/exporting a setup.

Exit codes:
    0 = PASS or PASS WITH OPTIONAL SNAPSHOT REVIEW
    1 = required checkpoint item missing or unreadable
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORTS_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

REPORT_PATH = OUTPUT_REPORTS_DIR / "phase3d_checkpoint_report.txt"


REQUIRED_SOURCE_FILES = [
    ("Phase 3 interactive payoff viewer", PAID_SIMULATOR_DIR / "phase3_interactive_payoff_viewer.py"),
    ("Phase 3B scenario-overlay model", PAID_SIMULATOR_DIR / "phase3_scenario_overlay_model.py"),
    ("Phase 3B scenario-overlay viewer", PAID_SIMULATOR_DIR / "phase3_scenario_overlay_viewer.py"),
    ("Phase 3C rich payoff viewer", PAID_SIMULATOR_DIR / "phase3c_rich_payoff_viewer.py"),
    ("Phase 3D integrated payoff-overlay viewer", PAID_SIMULATOR_DIR / "phase3d_integrated_payoff_overlay_viewer.py"),
    ("Main dashboard app", PAID_SIMULATOR_DIR / "config_form_app.py"),
    ("Main dashboard launcher", APP_DIR / "run_paid_simulator_form.py"),
]

REQUIRED_RUNNER_FILES = [
    ("Phase 3D viewer launcher", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer.py"),
    ("Phase 3D viewer check", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer_check.py"),
    ("Phase 3D pipeline check", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py"),
    ("Phase 3D dashboard-tab check", APP_DIR / "run_paid_simulator_phase3d_dashboard_tab_check.py"),
    ("Phase 3D integration-readiness check", APP_DIR / "run_paid_simulator_phase3d_integration_readiness_check.py"),
]

REQUIRED_CONTEXT_OUTPUTS = [
    ("Phase 3B scenario-overlay CSV", OUTPUT_TABLES_DIR / "phase3_scenario_overlay.csv"),
    ("Phase 3B scenario-overlay HTML", OUTPUT_REPORTS_DIR / "phase3_scenario_overlay.html"),
    ("Phase 3B scenario-overlay summary", OUTPUT_REPORTS_DIR / "phase3_scenario_overlay_summary.txt"),
    ("Phase 3B checkpoint report", OUTPUT_REPORTS_DIR / "phase3b_checkpoint_report.txt"),
    ("Phase 3C checkpoint report", OUTPUT_REPORTS_DIR / "phase3c_checkpoint_report.txt"),
    ("Phase 3D viewer check report", OUTPUT_REPORTS_DIR / "phase3d_integrated_overlay_viewer_check_report.txt"),
    ("Phase 3D pipeline report", OUTPUT_REPORTS_DIR / "phase3d_integrated_overlay_pipeline_report.txt"),
    ("Phase 3D dashboard-tab check report", OUTPUT_REPORTS_DIR / "phase3d_dashboard_tab_check_report.txt"),
    ("Phase 3D integration-readiness report", OUTPUT_REPORTS_DIR / "phase3d_integration_readiness_report.txt"),
]

OPTIONAL_PHASE3D_SNAPSHOTS = [
    ("Phase 3D integrated snapshot CSV", OUTPUT_TABLES_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv"),
    ("Phase 3D integrated snapshot HTML", OUTPUT_REPORTS_DIR / "phase3d_integrated_payoff_overlay_snapshot.html"),
]

REQUIRED_DOCS = [
    ("Phase 3 interactive payoff viewer", DOCS_DIR / "paid_simulator_phase3_interactive_payoff_viewer.md"),
    ("Phase 3 checkpoint summary", DOCS_DIR / "paid_simulator_phase3_checkpoint_summary.md"),
    ("Phase 3B scenario-overlay model", DOCS_DIR / "paid_simulator_phase3_scenario_overlay_model.md"),
    ("Phase 3B scenario-overlay viewer", DOCS_DIR / "paid_simulator_phase3_scenario_overlay_viewer.md"),
    ("Phase 3B checkpoint summary", DOCS_DIR / "paid_simulator_phase3b_checkpoint_summary.md"),
    ("Phase 3C rich payoff viewer", DOCS_DIR / "paid_simulator_phase3c_rich_payoff_viewer.md"),
    ("Phase 3C checkpoint summary", DOCS_DIR / "paid_simulator_phase3c_checkpoint_summary.md"),
    ("Phase 3D integrated viewer", DOCS_DIR / "paid_simulator_phase3d_integrated_payoff_overlay_viewer.md"),
    ("Phase 3D pipeline", DOCS_DIR / "paid_simulator_phase3d_integrated_overlay_pipeline_check.md"),
    ("Phase 3D dashboard tab", DOCS_DIR / "paid_simulator_phase3d_dashboard_tab.md"),
    ("Phase 3D integration readiness", DOCS_DIR / "paid_simulator_phase3d_integration_readiness.md"),
    ("Phase 3D checkpoint summary", DOCS_DIR / "paid_simulator_phase3d_checkpoint_summary.md"),
]

DASHBOARD_MARKERS = [
    ("Dashboard marker 'Phase 3 interactive payoff'", ["Phase 3 interactive payoff"]),
    ("Dashboard marker 'Phase 3B scenario overlay'", ["Phase 3B scenario overlay"]),
    ("Dashboard marker 'Phase 3C rich payoff'", ["Phase 3C rich payoff"]),
    ("Dashboard marker 'Phase 3D integrated overlay'", ["Phase 3D integrated overlay"]),
    (
        "Dashboard marker 'Phase 3D viewer launcher'",
        [
            "phase3d_integrated_payoff_overlay_viewer",
            "run_paid_simulator_phase3d_integrated_overlay_viewer.py",
            "Phase 3D integrated viewer",
            "Open standalone Phase 3D",
            "integrated overlay viewer",
        ],
    ),
    (
        "Dashboard marker 'Phase 3D pipeline check'",
        ["run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py"],
    ),
]

VIEWER_MARKERS = [
    ("Viewer marker 'Phase 3D integrated payoff'", ["Phase 3D integrated payoff", "Phase 3D"]),
    ("Viewer marker 'Integrated payoff graph'", ["Integrated payoff graph", "integrated payoff"]),
    ("Viewer marker 'Scenario overlay'", ["Scenario overlay", "scenario_overlay"]),
    ("Viewer marker 'Covered-call payoff concept'", ["Covered-call payoff", "covered_call", "covered call"]),
    ("Viewer marker 'Buy-and-hold concept'", ["Buy-and-hold", "Buy and hold", "buy_and_hold", "buy hold"]),
    ("Viewer marker 'Breakeven'", ["Breakeven", "break-even", "breakeven"]),
    ("Viewer marker 'Snapshot output'", ["phase3d_integrated_payoff_overlay_snapshot.csv"]),
]


def line(char: str = "=", width: int = 96) -> str:
    return char * width


def check_exists(label: str, path: Path, optional: bool = False) -> tuple[str, str]:
    if path.exists():
        status = "FOUND"
    else:
        status = "OPTIONAL" if optional else "MISSING"
    return status, f"{status:<10} {label:<62} {path}"


def count_csv_rows(path: Path) -> int | None:
    if not path.exists():
        return None
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle))
        if not rows:
            return 0
        return max(len(rows) - 1, 0)
    except Exception:
        return None


def check_csv_has_rows(label: str, path: Path, optional: bool = False) -> tuple[str, str]:
    rows = count_csv_rows(path)
    if rows is None:
        status = "OPTIONAL" if optional else "REVIEW"
        suffix = "file not available or unreadable"
    elif rows > 0:
        status = "PASS"
        suffix = f"rows={rows}"
    else:
        status = "OPTIONAL" if optional else "REVIEW"
        suffix = "rows=0"
    return status, f"{status:<10} {label:<62} {suffix}"


def source_contains_any(path: Path, markers: Iterable[str]) -> str | None:
    if not path.exists():
        return None
    try:
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
    except Exception:
        return None
    for marker in markers:
        if marker.lower() in text:
            return marker
    return None


def check_source_marker(label: str, path: Path, markers: Iterable[str], optional: bool = False) -> tuple[str, str]:
    found = source_contains_any(path, markers)
    if found:
        return "PASS", f"{'PASS':<10} {label:<62} {found}"
    status = "OPTIONAL" if optional else "REVIEW"
    return status, f"{status:<10} {label:<62} none of the accepted markers were found"


def main() -> int:
    OUTPUT_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    required_problem = False
    optional_review = False

    def add(text: str = "") -> None:
        lines.append(text)
        print(text)

    def add_section(title: str) -> None:
        add("")
        add(title)
        add(line("-"))

    add(line())
    add("Phase 3D integrated payoff-overlay checkpoint check")
    add(line())
    add(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    add(f"Project root: {PROJECT_ROOT}")

    add_section("Required Phase 3 / 3B / 3C / 3D source files")
    for label, path in REQUIRED_SOURCE_FILES:
        status, msg = check_exists(label, path)
        add(msg)
        if status != "FOUND":
            required_problem = True

    add_section("Required Phase 3D runner/check files")
    for label, path in REQUIRED_RUNNER_FILES:
        status, msg = check_exists(label, path)
        add(msg)
        if status != "FOUND":
            required_problem = True

    add_section("Required Phase 3B / 3C / 3D context outputs")
    for label, path in REQUIRED_CONTEXT_OUTPUTS:
        status, msg = check_exists(label, path)
        add(msg)
        if status != "FOUND":
            required_problem = True

    add_section("Optional Phase 3D saved snapshot outputs")
    for label, path in OPTIONAL_PHASE3D_SNAPSHOTS:
        status, msg = check_exists(label, path, optional=True)
        add(msg)
        if status == "OPTIONAL":
            optional_review = True

    add_section("Phase 3 / 3B / 3C / 3D documentation")
    for label, path in REQUIRED_DOCS:
        status, msg = check_exists(label, path)
        add(msg)
        if status != "FOUND":
            required_problem = True

    add_section("CSV row checks")
    required_csvs = [
        ("phase3_scenario_overlay.csv", OUTPUT_TABLES_DIR / "phase3_scenario_overlay.csv"),
    ]
    for label, path in required_csvs:
        status, msg = check_csv_has_rows(label, path)
        add(msg)
        if status != "PASS":
            required_problem = True

    optional_csvs = [
        (
            "phase3d_integrated_payoff_overlay_snapshot.csv",
            OUTPUT_TABLES_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv",
        ),
    ]
    for label, path in optional_csvs:
        status, msg = check_csv_has_rows(label, path, optional=True)
        add(msg)
        if status != "PASS":
            optional_review = True

    add_section("Main dashboard Phase 3D tab markers")
    dashboard_path = PAID_SIMULATOR_DIR / "config_form_app.py"
    for label, markers in DASHBOARD_MARKERS:
        status, msg = check_source_marker(label, dashboard_path, markers)
        add(msg)
        if status != "PASS":
            required_problem = True

    add_section("Phase 3D viewer source markers")
    viewer_path = PAID_SIMULATOR_DIR / "phase3d_integrated_payoff_overlay_viewer.py"
    for label, markers in VIEWER_MARKERS:
        status, msg = check_source_marker(label, viewer_path, markers)
        add(msg)
        if status != "PASS":
            required_problem = True

    add("")
    add(line())
    if required_problem:
        add("Overall Phase 3D checkpoint status: REVIEW")
        add("One or more required Phase 3D checkpoint items need attention.")
        exit_code = 1
    elif optional_review:
        add("Overall Phase 3D checkpoint status: PASS WITH OPTIONAL SNAPSHOT REVIEW")
        add("Only optional snapshot items require review. This is acceptable if no Phase 3D setup has been saved yet.")
        exit_code = 0
    else:
        add("Overall Phase 3D checkpoint status: PASS")
        add("The Phase 3D integrated payoff-overlay milestone is installed and connected.")
        exit_code = 0
    add(line())
    add("")
    add(f"Saved checkpoint report: {REPORT_PATH}")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
