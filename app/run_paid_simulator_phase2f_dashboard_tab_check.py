"""
run_paid_simulator_phase2f_dashboard_tab_check.py

Checks that the Developer-view-only Phase 2F model-decision tab is
installed in the main paid-simulator dashboard and that the key Phase 2F
outputs are present.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

REQUIRED_FILES = [
    ("Main dashboard", DASHBOARD_PATH),
    ("Phase 2F model-decision module", PROJECT_ROOT / "app" / "paid_simulator" / "model_decision_summary.py"),
    ("Phase 2F model-decision viewer", PROJECT_ROOT / "app" / "paid_simulator" / "phase2f_model_decision_viewer.py"),
    ("Phase 2F model-decision summary checker", PROJECT_ROOT / "app" / "run_paid_simulator_model_decision_summary_check.py"),
    ("Phase 2F model-decision pipeline checker", PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_model_decision_pipeline_check.py"),
    ("Phase 2F model-decision viewer launcher", PROJECT_ROOT / "app" / "run_paid_simulator_phase2f_model_decision_viewer.py"),
    ("Model-decision CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "model_decision_summary.csv"),
    ("Model-decision HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_decision_summary.html"),
    ("Model-decision text summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_decision_summary.txt"),
]

REQUIRED_MARKERS = [
    "Phase 2F model decision",
    "show_phase2f_model_decision_tab",
    "PHASE2F_MODEL_DECISION_CSV_PATH",
    "PHASE2F_MODEL_DECISION_PIPELINE_CHECK_PATH",
    "run_paid_simulator_phase2f_model_decision_pipeline_check.py",
    "phase2f_model_decision_viewer",
]

OPTIONAL_CONTEXT_MARKERS = [
    "Phase 2D tuning",
    "Phase 2E adjustment",
]


def print_line(label: str, status: str, detail: str = "") -> None:
    print(f"{status:<10} {label:<60} {detail}")


def main() -> int:
    print("=" * 100)
    print("Phase 2F model-decision dashboard-tab check")
    print("=" * 100)
    print(f"Project root: {PROJECT_ROOT}")
    print()

    all_ok = True

    print("Required files")
    print("-" * 100)
    for label, path in REQUIRED_FILES:
        if path.exists():
            print_line(label, "FOUND", str(path))
        else:
            print_line(label, "MISSING", str(path))
            all_ok = False
    print()

    print("Dashboard source markers")
    print("-" * 100)
    if DASHBOARD_PATH.exists():
        text = DASHBOARD_PATH.read_text(encoding="utf-8", errors="replace")
        for marker in REQUIRED_MARKERS:
            if marker in text:
                print_line(f"Marker '{marker}'", "PASS")
            else:
                print_line(f"Marker '{marker}'", "REVIEW")
                all_ok = False
        for marker in OPTIONAL_CONTEXT_MARKERS:
            if marker in text:
                print_line(f"Context marker '{marker}'", "PASS")
            else:
                print_line(f"Context marker '{marker}'", "REVIEW")
                all_ok = False
    else:
        print_line("Dashboard source", "MISSING", str(DASHBOARD_PATH))
        all_ok = False
    print()

    print("=" * 100)
    if all_ok:
        print("PASS: The Developer-view-only Phase 2F model-decision tab is installed and the Phase 2F outputs are present.")
        print("=" * 100)
        return 0

    print("REVIEW: One or more Phase 2F dashboard-tab items need attention.")
    print("=" * 100)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
