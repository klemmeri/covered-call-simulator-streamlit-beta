"""
Check script for the Phase 3D integrated payoff-overlay viewer.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
APP_DIR = PROJECT_ROOT / "app"
PAID_SIMULATOR_DIR = APP_DIR / "paid_simulator"
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_TABLE_DIR = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator"
OUTPUT_REPORT_DIR = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator"

VIEWER_APP = PAID_SIMULATOR_DIR / "phase3d_integrated_payoff_overlay_viewer.py"
VIEWER_LAUNCHER = APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer.py"
VIEWER_CHECK = APP_DIR / "run_paid_simulator_phase3d_integrated_overlay_viewer_check.py"
DOC_FILE = DOCS_DIR / "paid_simulator_phase3d_integrated_payoff_overlay_viewer.md"

PHASE3B_OVERLAY_CSV = OUTPUT_TABLE_DIR / "phase3_scenario_overlay.csv"
PHASE3B_OVERLAY_HTML = OUTPUT_REPORT_DIR / "phase3_scenario_overlay.html"
PHASE3B_CHECKPOINT = OUTPUT_REPORT_DIR / "phase3b_checkpoint_report.txt"
PHASE3C_CHECKPOINT = OUTPUT_REPORT_DIR / "phase3c_checkpoint_report.txt"
PHASE3D_SNAPSHOT_CSV = OUTPUT_TABLE_DIR / "phase3d_integrated_payoff_overlay_snapshot.csv"
PHASE3D_SNAPSHOT_HTML = OUTPUT_REPORT_DIR / "phase3d_integrated_payoff_overlay_snapshot.html"
REPORT_FILE = OUTPUT_REPORT_DIR / "phase3d_integrated_overlay_viewer_check_report.txt"


class CheckReport:
    def __init__(self) -> None:
        self.lines: list[str] = []
        self.errors = 0
        self.optional_reviews = 0

    def write(self, text: str = "") -> None:
        print(text)
        self.lines.append(text)

    def section(self, title: str) -> None:
        self.write()
        self.write(title)
        self.write("-" * 96)

    def item(self, status: str, label: str, detail: str = "") -> None:
        self.write(f"{status:<10} {label:<55} {detail}")
        if status == "MISSING" or status == "REVIEW":
            self.errors += 1
        if status == "OPTIONAL":
            self.optional_reviews += 1


def file_contains_any(path: Path, markers: list[str]) -> tuple[bool, str]:
    """Return True when the source contains any acceptable marker variation.

    The viewer text is intentionally allowed to use natural UI wording,
    so this checker should not fail only because a label is written as
    buy_and_hold_pl, covered_call_pl, or "covered-call payoff" instead
    of one exact phrase.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return False, ""

    text_lower = text.lower()
    for marker in markers:
        if marker.lower() in text_lower:
            return True, marker
    return False, ""


def check_file(report: CheckReport, label: str, path: Path, optional: bool = False) -> None:
    if path.exists():
        report.item("FOUND", label, str(path))
    elif optional:
        report.item("OPTIONAL", label, str(path))
    else:
        report.item("MISSING", label, str(path))


def main() -> int:
    report = CheckReport()
    report.write("=" * 96)
    report.write("Phase 3D integrated payoff-overlay viewer check")
    report.write("=" * 96)
    report.write(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
    report.write(f"Project root: {PROJECT_ROOT}")

    report.section("Required Phase 3D files")
    check_file(report, "Phase 3D viewer app", VIEWER_APP)
    check_file(report, "Phase 3D viewer launcher", VIEWER_LAUNCHER)
    check_file(report, "Phase 3D viewer check", VIEWER_CHECK)
    check_file(report, "Phase 3D documentation", DOC_FILE)

    report.section("Required Phase 3B / Phase 3C context")
    check_file(report, "Phase 3B scenario-overlay CSV", PHASE3B_OVERLAY_CSV)
    check_file(report, "Phase 3B scenario-overlay HTML", PHASE3B_OVERLAY_HTML)
    check_file(report, "Phase 3B checkpoint report", PHASE3B_CHECKPOINT)
    check_file(report, "Phase 3C checkpoint report", PHASE3C_CHECKPOINT)

    report.section("Optional Phase 3D saved snapshot outputs")
    check_file(report, "Phase 3D integrated snapshot CSV", PHASE3D_SNAPSHOT_CSV, optional=True)
    check_file(report, "Phase 3D integrated snapshot HTML", PHASE3D_SNAPSHOT_HTML, optional=True)

    report.section("Viewer source markers")
    marker_groups = [
        ("Phase 3D integrated payoff", ["Phase 3D integrated payoff", "Phase 3D integrated payoff and scenario overlay"]),
        ("Integrated payoff graph", ["Integrated payoff graph", "Integrated payoff"]),
        ("Scenario overlay", ["Scenario overlay", "scenario-overlay", "overlay_df"]),
        ("Covered-call payoff", ["Covered-call payoff", "covered-call payoff", "covered_call_pl", "Covered call"]),
        ("Buy-and-hold", ["Buy-and-hold", "buy-and-hold", "buy_and_hold_pl", "buy hold"]),
        ("Breakeven", ["Breakeven", "break-even", "break_even"]),
        ("phase3d_integrated_payoff_overlay_snapshot.csv", ["phase3d_integrated_payoff_overlay_snapshot.csv"]),
    ]
    for label, markers in marker_groups:
        found, matched = file_contains_any(VIEWER_APP, markers)
        if found:
            report.item("PASS", f"Viewer marker '{label}'", matched)
        else:
            report.item("REVIEW", f"Viewer marker '{label}'", f"no accepted marker found: {', '.join(markers)}")

    OUTPUT_REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text("\n".join(report.lines), encoding="utf-8")

    report.write()
    report.write("=" * 96)
    if report.errors == 0:
        if report.optional_reviews:
            report.write("Overall Phase 3D integrated viewer status: PASS WITH OPTIONAL SNAPSHOT REVIEW")
            report.write("Only optional snapshot files are missing. This is acceptable until a setup is saved.")
        else:
            report.write("Overall Phase 3D integrated viewer status: PASS")
        exit_code = 0
    else:
        report.write("Overall Phase 3D integrated viewer status: REVIEW")
        report.write("One or more required Phase 3D viewer items need attention.")
        exit_code = 1
    report.write("=" * 96)
    report.write(f"Saved check report: {REPORT_FILE}")
    REPORT_FILE.write_text("\n".join(report.lines), encoding="utf-8")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
