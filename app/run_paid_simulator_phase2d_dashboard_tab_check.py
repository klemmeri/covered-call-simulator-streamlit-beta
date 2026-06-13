"""
run_paid_simulator_phase2d_dashboard_tab_check.py

Checks that the Developer-view-only Phase 2D tuning tab has been installed
in the main Streamlit dashboard and that the Phase 2D tuning artifacts are present.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys


CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]

DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"
REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2d_dashboard_tab_check_report.txt"

REQUIRED_FILES = [
    ("Main dashboard app", DASHBOARD_PATH),
    ("Phase 2D tuning module", PROJECT_ROOT / "app" / "paid_simulator" / "premium_model_tuning.py"),
    ("Phase 2D tuning viewer", PROJECT_ROOT / "app" / "paid_simulator" / "phase2d_premium_tuning_viewer.py"),
    ("Phase 2D tuning check", PROJECT_ROOT / "app" / "run_paid_simulator_premium_model_tuning_check.py"),
    ("Phase 2D tuning viewer launcher", PROJECT_ROOT / "app" / "run_paid_simulator_phase2d_premium_tuning_viewer.py"),
    ("Phase 2D tuning viewer check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2d_premium_tuning_viewer_check.py"),
    ("Phase 2D tuning pipeline check", PROJECT_ROOT / "app" / "run_paid_simulator_phase2d_tuning_pipeline_check.py"),
    ("Phase 2D tuning config", PROJECT_ROOT / "config" / "premium_model_tuning_config.json"),
    ("Phase 2D tuning recommendations CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_tuning_recommendations.csv"),
    ("Phase 2D tuning recommendations HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_tuning_recommendations.html"),
    ("Phase 2D tuning summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_tuning_summary.txt"),
    ("Phase 2D tuning pipeline report", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "phase2d_tuning_pipeline_report.txt"),
    ("Phase 2D dashboard-tab docs", PROJECT_ROOT / "docs" / "paid_simulator_phase2d_dashboard_tab.md"),
]

REQUIRED_MARKERS = [
    "Phase 2D tuning",
    "show_phase2d_tuning_tab",
    "PHASE2D_TUNING_RECOMMENDATIONS_PATH",
    "run_paid_simulator_phase2d_tuning_pipeline_check.py",
    "phase2d_premium_tuning_viewer",
]


def line(label: str = "", char: str = "=") -> str:
    if label:
        return f"{label}\n" + char * 96
    return char * 96


def main() -> int:
    lines: list[str] = []
    lines.append(line("Phase 2D tuning dashboard-tab check"))
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"Project root: {PROJECT_ROOT}")
    lines.append("")

    overall_ok = True

    lines.append(line("Required files", "-"))
    for label, path in REQUIRED_FILES:
        exists = path.exists()
        status = "FOUND" if exists else "MISSING"
        if not exists:
            overall_ok = False
        lines.append(f"{status:<10} {label:<45} {path}")

    lines.append("")
    lines.append(line("Dashboard tab markers", "-"))
    dashboard_text = ""
    if DASHBOARD_PATH.exists():
        dashboard_text = DASHBOARD_PATH.read_text(encoding="utf-8", errors="replace")
    for marker in REQUIRED_MARKERS:
        found = marker in dashboard_text
        status = "PASS" if found else "MISSING"
        if not found:
            overall_ok = False
        lines.append(f"{status:<10} Dashboard marker '{marker}'")

    lines.append("")
    if overall_ok:
        lines.append("PASS: The Developer-view-only Phase 2D tuning tab is installed and the Phase 2D tuning outputs are present.")
    else:
        lines.append("REVIEW: One or more Phase 2D dashboard-tab items are missing.")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    print("\n".join(lines))
    print(f"\nSaved dashboard-tab check report: {REPORT_PATH}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
