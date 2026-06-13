"""
run_paid_simulator_phase2b_dashboard_tab_check.py

Checks that the main paid-simulator dashboard contains the Developer-view-only
Phase 2B premium-model tab and that the supporting Phase 2B files are present.
"""

from __future__ import annotations

import py_compile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

REQUIRED_SUPPORT_FILES = [
    PROJECT_ROOT / "app" / "run_paid_simulator_phase2b_pipeline_check.py",
    PROJECT_ROOT / "app" / "run_paid_simulator_phase2b_premium_viewer.py",
    PROJECT_ROOT / "app" / "paid_simulator" / "phase2b_premium_viewer.py",
]

REQUIRED_OUTPUT_FILES = [
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "option_premium_scaffold.csv",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_aware_payoff_scaffold.csv",
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_vs_scaffold_comparison.csv",
]

REQUIRED_TEXT_MARKERS = [
    "PHASE2B_OPTION_PREMIUM_PATH",
    "PHASE2B_PREMIUM_AWARE_PAYOFF_PATH",
    "PHASE2B_PREMIUM_VS_SCAFFOLD_PATH",
    "PHASE2B_PIPELINE_CHECK_PATH",
    "PHASE2B_PREMIUM_VIEWER_PATH",
    "def show_phase2b_premium_file_status",
    "def show_phase2b_premium_model_tab",
    '"Phase 2B premium model"',
    "Run Phase 2B pipeline check",
    "Open standalone Phase 2B premium viewer",
]


def print_header(title: str) -> None:
    print("=" * 92)
    print(title)
    print("=" * 92)


def check_file(path: Path, label: str) -> bool:
    status = "FOUND" if path.exists() else "MISSING"
    print(f"{status:<8} {label:<42} {path}")
    return path.exists()


def csv_has_data_rows(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return False
    return len([line for line in lines if line.strip()]) >= 2


def main() -> int:
    print_header("Phase 2B premium-model dashboard-tab check")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    all_pass = True

    print("Dashboard file")
    print("-" * 92)
    all_pass = check_file(DASHBOARD_PATH, "Main dashboard") and all_pass

    if DASHBOARD_PATH.exists():
        try:
            py_compile.compile(str(DASHBOARD_PATH), doraise=True)
            print(f"PASS     {'Dashboard syntax':<42} Python syntax check passed")
        except Exception as exc:
            all_pass = False
            print(f"FAIL     {'Dashboard syntax':<42} {exc}")

        text = DASHBOARD_PATH.read_text(encoding="utf-8", errors="replace")
        print()
        print("Dashboard markers")
        print("-" * 92)
        for marker in REQUIRED_TEXT_MARKERS:
            found = marker in text
            print(f"{'FOUND' if found else 'MISSING':<8} {marker}")
            all_pass = all_pass and found

    print()
    print("Supporting Phase 2B files")
    print("-" * 92)
    for file_path in REQUIRED_SUPPORT_FILES:
        all_pass = check_file(file_path, file_path.name) and all_pass

    print()
    print("Current Phase 2B output files")
    print("-" * 92)
    for file_path in REQUIRED_OUTPUT_FILES:
        exists = file_path.exists()
        has_rows = csv_has_data_rows(file_path)
        status = "PASS" if exists and has_rows else "REVIEW"
        print(f"{status:<8} {file_path.name:<42} exists={exists}, has_data_rows={has_rows}")
        all_pass = all_pass and exists and has_rows

    print()
    print("Interpretation")
    print("-" * 92)
    if all_pass:
        print("PASS: The Developer-view-only Phase 2B premium-model tab is installed and the Phase 2B outputs are present.")
        print("Next: open the main dashboard, switch to Developer view, and inspect the new Phase 2B premium model tab.")
        return 0

    print("REVIEW: One or more checks did not pass.")
    print("If output CSVs are missing, run app\\run_paid_simulator_phase2b_pipeline_check.py first.")
    print("If dashboard markers are missing, re-extract the Phase 2B dashboard-tab package into the project root.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
