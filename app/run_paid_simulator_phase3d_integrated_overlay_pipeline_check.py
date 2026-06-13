"""
run_paid_simulator_phase3d_integrated_overlay_pipeline_check.py

Phase 3D integrated payoff-overlay pipeline checker for the Covered Call
Strategy Stress Test project.

This script verifies that the Phase 3D integrated payoff-overlay viewer is
installed, that the required Phase 3B/3C context is available, and that the
Phase 3D viewer check passes. Snapshot outputs are treated as optional because
they are only created after a user opens the Streamlit viewer and saves a setup.
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
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"

REPORT_PATH = OUTPUT_REPORT_DIR / "phase3d_integrated_overlay_pipeline_report.txt"


class CheckRecorder:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.failures: int = 0
        self.optional_reviews: int = 0

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


def path_detail(path: Path) -> str:
    try:
        return str(path)
    except Exception:
        return repr(path)


def check_exists(rec: CheckRecorder, label: str, path: Path, optional: bool = False) -> bool:
    if path.exists():
        rec.status("FOUND", label, path_detail(path))
        return True
    if optional:
        rec.status("OPTIONAL", label, path_detail(path))
    else:
        rec.status("MISSING", label, path_detail(path))
    return False


def check_csv_rows(rec: CheckRecorder, label: str, path: Path, optional: bool = False) -> bool:
    if not path.exists():
        if optional:
            rec.status("OPTIONAL", label, "file not available or unreadable")
        else:
            rec.status("MISSING", label, path_detail(path))
        return False
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        data_rows = max(len(rows) - 1, 0)
        if data_rows > 0:
            rec.status("PASS", label, f"rows={data_rows}")
            return True
        rec.status("REVIEW", label, "file exists but has no data rows")
        return False
    except Exception as exc:  # pragma: no cover - defensive diagnostic
        if optional:
            rec.status("OPTIONAL", label, f"file not available or unreadable: {exc}")
        else:
            rec.status("ERROR", label, str(exc))
        return False


def run_child_check(rec: CheckRecorder, label: str, script_path: Path) -> bool:
    if not script_path.exists():
        rec.status("MISSING", label, path_detail(script_path))
        return False

    rec.status("RUN", label, path_detail(script_path))
    try:
        completed = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive diagnostic
        rec.status("ERROR", label, str(exc))
        return False

    if completed.stdout.strip():
        for line in completed.stdout.strip().splitlines()[-8:]:
            rec.emit(f"  stdout: {line}")
    if completed.stderr.strip():
        for line in completed.stderr.strip().splitlines()[-8:]:
            rec.emit(f"  stderr: {line}")

    if completed.returncode == 0:
        rec.status("PASS", label, f"exit code {completed.returncode}")
        return True

    rec.status("FAIL", label, f"exit code {completed.returncode}")
    return False


def source_contains_any(path: Path, markers: Iterable[str]) -> Optional[str]:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    text_lower = text.lower()
    for marker in markers:
        if marker.lower() in text_lower:
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

    rec.emit("=" * 96)
    rec.emit("Phase 3D integrated payoff-overlay pipeline check")
    rec.emit("=" * 96)
    rec.emit(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    rec.emit(f"Project root: {PROJECT_ROOT}")

    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rec.section("Required Phase 3D files")
    check_exists(rec, "Phase 3D integrated viewer app", PAID_SIMULATOR_DIR / "phase3d_integrated_payoff_overlay_viewer.py")
    check_exists(rec, "Phase 3D integrated viewer launcher", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer.py")
    check_exists(rec, "Phase 3D integrated viewer check", APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer_check.py")
    check_exists(rec, "Phase 3D integrated viewer documentation", DOCS_DIR / "paid_simulator_phase3d_integrated_payoff_overlay_viewer.md")

    rec.section("Required Phase 3B / Phase 3C context")
    check_exists(rec, "Phase 3B scenario-overlay CSV", OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv")
    check_exists(rec, "Phase 3B scenario-overlay HTML", OUTPUT_REPORT_DIR / "phase3_scenario_overlay.html")
    check_exists(rec, "Phase 3B scenario-overlay summary", OUTPUT_REPORT_DIR / "phase3_scenario_overlay_summary.txt")
    check_exists(rec, "Phase 3B checkpoint report", OUTPUT_REPORT_DIR / "phase3b_checkpoint_report.txt")
    check_exists(rec, "Phase 3C checkpoint report", OUTPUT_REPORT_DIR / "phase3c_checkpoint_report.txt")

    rec.section("Run Phase 3D viewer check")
    run_child_check(
        rec,
        "Phase 3D integrated viewer check execution",
        APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer_check.py",
    )

    rec.section("CSV row checks")
    check_csv_rows(rec, "phase3_scenario_overlay.csv", OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv")
    check_csv_rows(
        rec,
        "phase3d_integrated_payoff_overlay_snapshot.csv",
        OUTPUT_TABLE_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv",
        optional=True,
    )

    rec.section("Optional Phase 3D saved snapshot outputs")
    check_exists(
        rec,
        "Phase 3D integrated snapshot CSV",
        OUTPUT_TABLE_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv",
        optional=True,
    )
    check_exists(
        rec,
        "Phase 3D integrated snapshot HTML",
        OUTPUT_REPORT_DIR / "phase3d_integrated_payoff_overlay_snapshot.html",
        optional=True,
    )

    rec.section("Viewer source markers")
    viewer_path = PAID_SIMULATOR_DIR / "phase3d_integrated_payoff_overlay_viewer.py"
    check_source_marker(rec, "Viewer marker 'Phase 3D'", viewer_path, ["Phase 3D", "phase3d"])
    check_source_marker(rec, "Viewer marker 'Integrated payoff'", viewer_path, ["Integrated payoff", "integrated payoff"])
    check_source_marker(rec, "Viewer marker 'Scenario overlay'", viewer_path, ["Scenario overlay", "scenario_overlay"])
    check_source_marker(rec, "Viewer marker 'Covered-call payoff'", viewer_path, ["Covered-call payoff", "covered call payoff", "covered_call"])
    check_source_marker(rec, "Viewer marker 'Buy-and-hold'", viewer_path, ["Buy-and-hold", "buy and hold", "buy_and_hold"])
    check_source_marker(rec, "Viewer marker 'Breakeven'", viewer_path, ["Breakeven", "break-even", "break_even"])

    rec.emit("\n" + "=" * 96)
    if rec.failures == 0:
        if rec.optional_reviews > 0:
            rec.emit("Overall Phase 3D integrated overlay pipeline status: PASS WITH OPTIONAL SNAPSHOT REVIEW")
            rec.emit("Only optional snapshot items require review. This is acceptable if no setup has been saved yet.")
        else:
            rec.emit("Overall Phase 3D integrated overlay pipeline status: PASS")
    else:
        rec.emit("Overall Phase 3D integrated overlay pipeline status: REVIEW")
        rec.emit("One or more required Phase 3D pipeline items need attention.")
    rec.emit("=" * 96)

    REPORT_PATH.write_text("\n".join(rec.lines) + "\n", encoding="utf-8")
    rec.emit(f"\nSaved pipeline report: {REPORT_PATH}")

    return 0 if rec.failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
