"""
run_paid_simulator_phase2g_dashboard_tab_check.py

Checks that the Developer-view-only Phase 2G model-promotion tab is
installed in the main paid-simulator dashboard and that the key Phase 2G
outputs are present.
"""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

REQUIRED_FILES = [
    ("Main dashboard", DASHBOARD_PATH),
    ("Phase 2G model-promotion module", PROJECT_ROOT / "app" / "paid_simulator" / "model_promotion_planning.py"),
    ("Phase 2G model-promotion viewer", PROJECT_ROOT / "app" / "paid_simulator" / "phase2g_model_promotion_viewer.py"),
    ("Phase 2G model-promotion planning checker", PROJECT_ROOT / "app" / "run_paid_simulator_model_promotion_planning_check.py"),
    ("Phase 2G model-promotion pipeline checker", PROJECT_ROOT / "app" / "run_paid_simulator_phase2g_model_promotion_pipeline_check.py"),
    ("Phase 2G model-promotion viewer launcher", PROJECT_ROOT / "app" / "run_paid_simulator_phase2g_model_promotion_viewer.py"),
    ("Model-promotion plan CSV", PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "model_promotion_plan.csv"),
    ("Model-promotion plan HTML", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_promotion_plan.html"),
    ("Model-promotion plan text summary", PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "model_promotion_plan.txt"),
]

REQUIRED_MARKERS = [
    "Phase 2G model promotion",
    "show_phase2g_model_promotion_tab",
    "PHASE2G_MODEL_PROMOTION_PLAN_CSV_PATH",
    "PHASE2G_MODEL_PROMOTION_PIPELINE_CHECK_PATH",
    "run_paid_simulator_phase2g_model_promotion_pipeline_check.py",
    "phase2g_model_promotion_viewer",
]

CONTEXT_MARKERS = [
    "Phase 2B premium model",
    "Phase 2C validation",
    "Phase 2D tuning",
    "Phase 2E adjustment",
    "Phase 2F model decision",
]


def print_line(label: str, status: str, detail: str = "") -> None:
    print(f"{status:<10} {label:<62} {detail}")


def main() -> int:
    print("=" * 100)
    print("Phase 2G model-promotion dashboard-tab check")
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
        for marker in CONTEXT_MARKERS:
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
        print("PASS: The Developer-view-only Phase 2G model-promotion tab is installed and the Phase 2G outputs are present.")
        print("=" * 100)
        return 0

    print("REVIEW: One or more Phase 2G dashboard-tab items need attention.")
    print("=" * 100)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
