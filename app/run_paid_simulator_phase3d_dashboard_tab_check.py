"""
run_paid_simulator_phase3d_dashboard_tab_check.py

Developer-view dashboard-tab checker for the Phase 3D integrated payoff-overlay
prototype in the Covered Call Strategy Stress Test project.

The checker verifies that the main dashboard contains the Phase 3D Developer-view
markers and that the standalone Phase 3D integrated viewer/pipeline files are
installed. Snapshot outputs are optional because they are created only after a
user saves a setup from the viewer.
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
REPORT_PATH = OUTPUT_REPORT_DIR / "phase3d_dashboard_tab_check_report.txt"


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
        self.emit(f"{status:<10} {label:<55} {detail}")
        if status in {"MISSING", "FAIL", "ERROR", "REVIEW"}:
            self.failures += 1
        elif status == "OPTIONAL":
            self.optional_reviews += 1


def check_exists(rec: CheckRecorder, label: str, path: Path, optional: bool = False) -> bool:
    if path.exists():
        rec.status("FOUND", label, str(path))
        return True
    if optional:
        rec.status("OPTIONAL", label, str(path))
    else:
        rec.status("MISSING", label, str(path))
    return False


def check_csv_rows(rec: CheckRecorder, label: str, path: Path, optional: bool = False) -> bool:
    if not path.exists():
        if optional:
            rec.status("OPTIONAL", label, "file not available or unreadable")
        else:
            rec.status("MISSING", label, str(path))
        return False
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            rows = list(csv.reader(handle))
        data_rows = max(len(rows) - 1, 0)
        if data_rows > 0:
            rec.status("PASS", label, f"rows={data_rows}")
            return True
        rec.status("REVIEW", label, "file exists but has no data rows")
        return False
    except Exception as exc:  # pragma: no cover - diagnostic only
        if optional:
            rec.status("OPTIONAL", label, f"file not available or unreadable: {exc}")
        else:
            rec.status("ERROR", label, str(exc))
        return False


def check_source_marker(rec: CheckRecorder, label: str, path: Path, markers: list[str]) -> bool:
    if not path.exists():
        rec.status("MISSING", label, str(path))
        return False
    text = path.read_text(encoding="utf-8", errors="ignore").lower()
    for marker in markers:
        if marker.lower() in text:
            rec.status("PASS", label, marker)
            return True
    rec.status("REVIEW", label, "none of the accepted markers were found")
    return False


def main() -> int:
    rec = CheckRecorder()
    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rec.emit("=" * 96)
    rec.emit("Phase 3D integrated overlay dashboard-tab check")
    rec.emit("=" * 96)
    rec.emit(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rec.emit(f"Project root: {PROJECT_ROOT}")

    rec.section("Required Phase 3D dashboard/source files")
    check_exists(rec, "Main dashboard app", PAID_SIMULATOR_DIR / "config_form_app.py")
    check_exists(rec, "Phase 3D integrated viewer app", PAID_SIMULATOR_DIR / "phase3d_integrated_payoff_overlay_viewer.py")
    check_exists(rec, "Phase 3D integrated viewer launcher", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer.py")
    check_exists(rec, "Phase 3D integrated viewer check", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer_check.py")
    check_exists(rec, "Phase 3D integrated overlay pipeline check", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py")
    check_exists(rec, "Phase 3D dashboard-tab check", APP_DIR / "run_paid_simulator_phase3d_dashboard_tab_check.py")

    rec.section("Phase 3D documentation")
    check_exists(rec, "Phase 3D integrated viewer documentation", DOCS_DIR / "paid_simulator_phase3d_integrated_payoff_overlay_viewer.md")
    check_exists(rec, "Phase 3D pipeline documentation", DOCS_DIR / "paid_simulator_phase3d_integrated_overlay_pipeline_check.md")
    check_exists(rec, "Phase 3D dashboard-tab documentation", DOCS_DIR / "paid_simulator_phase3d_dashboard_tab.md")

    rec.section("Required Phase 3B / Phase 3C context")
    check_exists(rec, "Phase 3B scenario-overlay CSV", OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv")
    check_exists(rec, "Phase 3B scenario-overlay HTML", OUTPUT_REPORT_DIR / "phase3_scenario_overlay.html")
    check_exists(rec, "Phase 3B scenario-overlay summary", OUTPUT_REPORT_DIR / "phase3_scenario_overlay_summary.txt")
    check_exists(rec, "Phase 3C checkpoint report", OUTPUT_REPORT_DIR / "phase3c_checkpoint_report.txt")
    check_exists(rec, "Phase 3D pipeline report", OUTPUT_REPORT_DIR / "phase3d_integrated_overlay_pipeline_report.txt", optional=True)

    rec.section("Optional Phase 3D saved snapshot outputs")
    check_exists(rec, "Phase 3D integrated snapshot CSV", OUTPUT_TABLE_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv", optional=True)
    check_exists(rec, "Phase 3D integrated snapshot HTML", OUTPUT_REPORT_DIR / "phase3d_integrated_payoff_overlay_snapshot.html", optional=True)

    rec.section("CSV row checks")
    check_csv_rows(rec, "phase3_scenario_overlay.csv", OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv")
    check_csv_rows(
        rec,
        "phase3d_integrated_payoff_overlay_snapshot.csv",
        OUTPUT_TABLE_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv",
        optional=True,
    )

    rec.section("Main dashboard Phase 3D tab markers")
    dashboard_path = PAID_SIMULATOR_DIR / "config_form_app.py"
    check_source_marker(rec, "Dashboard marker 'Phase 3 interactive payoff'", dashboard_path, ["Phase 3 interactive payoff"])
    check_source_marker(rec, "Dashboard marker 'Phase 3B scenario overlay'", dashboard_path, ["Phase 3B scenario overlay"])
    check_source_marker(rec, "Dashboard marker 'Phase 3C rich payoff'", dashboard_path, ["Phase 3C rich payoff"])
    check_source_marker(rec, "Dashboard marker 'Phase 3D integrated overlay'", dashboard_path, ["Phase 3D integrated overlay"])
    check_source_marker(
        rec,
        "Dashboard marker 'Phase 3D integrated viewer launcher'",
        dashboard_path,
        [
            "phase3d_integrated_payoff_overlay_viewer",
            "run_paid_simulator_phase3d_integrated_overlay_viewer.py",
            "Phase 3D integrated viewer",
            "Open standalone Phase 3D",
            "integrated overlay viewer",
        ],
    )
    check_source_marker(
        rec,
        "Dashboard marker 'run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py'",
        dashboard_path,
        ["run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py"],
    )

    rec.emit("\n" + "=" * 96)
    if rec.failures == 0:
        if rec.optional_reviews:
            rec.emit("Overall Phase 3D dashboard-tab status: PASS WITH OPTIONAL SNAPSHOT REVIEW")
            rec.emit("Only optional snapshot items require review. This is acceptable if no setup has been saved yet.")
        else:
            rec.emit("Overall Phase 3D dashboard-tab status: PASS")
        exit_code = 0
    else:
        rec.emit("Overall Phase 3D dashboard-tab status: REVIEW")
        rec.emit("One or more required Phase 3D dashboard-tab items need attention.")
        exit_code = 1
    rec.emit("=" * 96)

    REPORT_PATH.write_text("\n".join(rec.lines) + "\n", encoding="utf-8")
    rec.emit(f"\nSaved check report: {REPORT_PATH}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
