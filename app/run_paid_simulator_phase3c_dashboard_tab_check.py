"""
run_paid_simulator_phase3c_dashboard_tab_check.py

Checks that the Developer-view-only Phase 3C rich payoff tab is installed
in the main paid simulator dashboard.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3c_rich_payoff_viewer.py"
VIEWER_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3c_rich_payoff_viewer_check.py"
PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3c_rich_payoff_pipeline_check.py"
DOC_PATH = PROJECT_ROOT / "docs" / "paid_simulator_phase3c_dashboard_tab.md"
OUTPUT_REPORT = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3c_dashboard_tab_check_report.txt"
SNAPSHOT_CSV = PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "phase3c_rich_payoff_snapshot.csv"
SNAPSHOT_HTML = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3c_rich_payoff_snapshot.html"

REQUIRED_FILES = [
    ("Main dashboard app", DASHBOARD_PATH),
    ("Phase 3C standalone viewer", VIEWER_PATH),
    ("Phase 3C standalone viewer check", VIEWER_CHECK_PATH),
    ("Phase 3C pipeline check", PIPELINE_CHECK_PATH),
    ("Phase 3C dashboard-tab documentation", DOC_PATH),
]

OPTIONAL_FILES = [
    ("Phase 3C saved payoff snapshot CSV", SNAPSHOT_CSV),
    ("Phase 3C saved payoff snapshot HTML", SNAPSHOT_HTML),
]

REQUIRED_MARKERS = [
    "Phase 3 interactive payoff",
    "Phase 3B scenario overlay",
    "Phase 3C rich payoff",
    "show_phase3c_rich_payoff_tab",
    "phase3c_rich_payoff_viewer",
    "run_paid_simulator_phase3c_rich_payoff_pipeline_check.py",
    "PHASE3C_RICH_PAYOFF_SNAPSHOT_CSV_PATH",
]


def format_line(status: str, label: str, detail: str = "") -> str:
    return f"{status:<12} {label:<60} {detail}"


def main() -> int:
    lines: list[str] = []
    lines.append("=" * 100)
    lines.append("Phase 3C rich payoff dashboard-tab check")
    lines.append("=" * 100)
    lines.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    all_ok = True

    lines.append("Required files")
    lines.append("-" * 100)
    for label, path in REQUIRED_FILES:
        exists = path.exists()
        status = "FOUND" if exists else "MISSING"
        if not exists:
            all_ok = False
        lines.append(format_line(status, label, str(path)))
    lines.append("")

    lines.append("Optional Phase 3C snapshot files")
    lines.append("-" * 100)
    for label, path in OPTIONAL_FILES:
        exists = path.exists()
        status = "OPTIONAL/FOUND" if exists else "OPTIONAL/MISSING"
        lines.append(format_line(status, label, str(path)))
    lines.append("")

    lines.append("Main dashboard Phase 3C markers")
    lines.append("-" * 100)
    dashboard_text = DASHBOARD_PATH.read_text(encoding="utf-8", errors="replace") if DASHBOARD_PATH.exists() else ""
    for marker in REQUIRED_MARKERS:
        ok = marker in dashboard_text
        status = "PASS" if ok else "MISSING"
        if not ok:
            all_ok = False
        lines.append(format_line(status, f"Dashboard marker '{marker}'", marker if ok else ""))
    lines.append("")

    status_text = "PASS" if all_ok else "REVIEW"
    lines.append("=" * 100)
    lines.append(f"Overall Phase 3C dashboard-tab status: {status_text}")
    if all_ok:
        lines.append("The Developer-view-only Phase 3C rich payoff tab is installed.")
        lines.append("Optional snapshot files are not required until a setup is saved from the standalone viewer.")
    else:
        lines.append("One or more Phase 3C dashboard-tab items need attention.")
    lines.append("=" * 100)

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nSaved check report: {OUTPUT_REPORT}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
