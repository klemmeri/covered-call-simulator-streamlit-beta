"""
run_paid_simulator_phase3b_dashboard_tab_check.py

Checks that the Developer-view-only Phase 3B scenario-overlay tab is installed
in the main paid simulator dashboard.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
MODEL_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_check.py"
VIEWER_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer.py"
VIEWER_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_viewer_check.py"
PIPELINE_CHECK_PATH = PROJECT_ROOT / "app" / "run_paid_simulator_phase3_scenario_overlay_pipeline_check.py"
DOC_PATH = PROJECT_ROOT / "docs" / "paid_simulator_phase3b_dashboard_tab.md"
OUTPUT_REPORT = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase3b_dashboard_tab_check_report.txt"

REQUIRED_FILES = [
    ("Main dashboard app", DASHBOARD_PATH),
    ("Phase 3B scenario-overlay model check", MODEL_CHECK_PATH),
    ("Phase 3B standalone viewer", VIEWER_PATH),
    ("Phase 3B standalone viewer check", VIEWER_CHECK_PATH),
    ("Phase 3B pipeline check", PIPELINE_CHECK_PATH),
    ("Phase 3B dashboard-tab documentation", DOC_PATH),
]

REQUIRED_MARKERS = [
    "Phase 3B scenario overlay",
    "show_phase3b_scenario_overlay_tab",
    "phase3_scenario_overlay_viewer",
    "run_paid_simulator_phase3_scenario_overlay_pipeline_check.py",
    "PHASE3B_SCENARIO_OVERLAY_CSV_PATH",
]


def format_line(status: str, label: str, detail: str = "") -> str:
    return f"{status:<10} {label:<55} {detail}"


def main() -> int:
    lines: list[str] = []
    lines.append("=" * 96)
    lines.append("Phase 3B scenario-overlay dashboard-tab check")
    lines.append("=" * 96)
    lines.append(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    all_ok = True

    lines.append("Required files")
    lines.append("-" * 96)
    for label, path in REQUIRED_FILES:
        exists = path.exists()
        status = "FOUND" if exists else "MISSING"
        if not exists:
            all_ok = False
        lines.append(format_line(status, label, str(path)))
    lines.append("")

    lines.append("Main dashboard Phase 3B markers")
    lines.append("-" * 96)
    dashboard_text = DASHBOARD_PATH.read_text(encoding="utf-8", errors="replace") if DASHBOARD_PATH.exists() else ""
    for marker in REQUIRED_MARKERS:
        ok = marker in dashboard_text
        status = "PASS" if ok else "MISSING"
        if not ok:
            all_ok = False
        lines.append(format_line(status, f"Dashboard marker '{marker}'", marker if ok else ""))
    lines.append("")

    status_text = "PASS" if all_ok else "REVIEW"
    lines.append("=" * 96)
    lines.append(f"Overall Phase 3B dashboard-tab status: {status_text}")
    if all_ok:
        lines.append("The Developer-view-only Phase 3B scenario-overlay tab is installed.")
    else:
        lines.append("One or more Phase 3B dashboard-tab items need attention.")
    lines.append("=" * 96)

    OUTPUT_REPORT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nSaved check report: {OUTPUT_REPORT}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
