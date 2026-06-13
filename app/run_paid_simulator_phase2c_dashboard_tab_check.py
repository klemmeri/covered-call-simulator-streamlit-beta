"""
run_paid_simulator_phase2c_dashboard_tab_check.py

Checks that the main paid-simulator dashboard contains the Developer-view-only
Phase 2C premium-model validation tab and that the supporting Phase 2C files
and validation outputs are present.
"""

from __future__ import annotations

import py_compile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_PATH = PROJECT_ROOT / "app" / "paid_simulator" / "config_form_app.py"

REQUIRED_SUPPORT_FILES = [
    PROJECT_ROOT / "app" / "run_paid_simulator_premium_model_validation_check.py",
    PROJECT_ROOT / "app" / "run_paid_simulator_phase2c_validation_pipeline_check.py",
    PROJECT_ROOT / "app" / "run_paid_simulator_phase2c_premium_validation_viewer.py",
    PROJECT_ROOT / "app" / "paid_simulator" / "premium_model_validation.py",
    PROJECT_ROOT / "app" / "paid_simulator" / "phase2c_premium_validation_viewer.py",
]

REQUIRED_OUTPUT_FILES = [
    PROJECT_ROOT / "outputs" / "tables" / "paid_simulator" / "premium_model_validation_scaffold.csv",
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_scaffold.html",
    PROJECT_ROOT / "outputs" / "reports" / "paid_simulator" / "premium_model_validation_summary.txt",
]

REQUIRED_TEXT_MARKERS = [
    "PHASE2C_VALIDATION_CSV_PATH",
    "PHASE2C_VALIDATION_HTML_PATH",
    "PHASE2C_VALIDATION_SUMMARY_PATH",
    "PHASE2C_VALIDATION_PIPELINE_CHECK_PATH",
    "PHASE2C_VALIDATION_VIEWER_PATH",
    "def show_phase2c_validation_file_status",
    "def show_phase2c_validation_tab",
    '"Phase 2C validation"',
    "Run Phase 2C validation pipeline",
    "Open standalone Phase 2C validation viewer",
]


def print_header(title: str) -> None:
    print("=" * 92)
    print(title)
    print("=" * 92)


def check_file(path: Path, label: str) -> bool:
    status = "FOUND" if path.exists() else "MISSING"
    print(f"{status:<8} {label:<42} {path}")
    return path.exists()


def file_has_content(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return len(path.read_text(encoding="utf-8", errors="replace").strip()) > 0
    except Exception:
        return False


def csv_has_data_rows(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return False
    return len([line for line in lines if line.strip()]) >= 2


def main() -> int:
    print_header("Phase 2C premium-validation dashboard-tab check")
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
    print("Supporting Phase 2C files")
    print("-" * 92)
    for file_path in REQUIRED_SUPPORT_FILES:
        all_pass = check_file(file_path, file_path.name) and all_pass

    print()
    print("Current Phase 2C validation output files")
    print("-" * 92)
    for file_path in REQUIRED_OUTPUT_FILES:
        exists = file_path.exists()
        if file_path.suffix.lower() == ".csv":
            ok = csv_has_data_rows(file_path)
            detail = f"exists={exists}, has_data_rows={ok}"
        else:
            ok = file_has_content(file_path)
            detail = f"exists={exists}, has_content={ok}"
        status = "PASS" if exists and ok else "REVIEW"
        print(f"{status:<8} {file_path.name:<42} {detail}")
        all_pass = all_pass and exists and ok

    print()
    print("Interpretation")
    print("-" * 92)
    if all_pass:
        print("PASS: The Developer-view-only Phase 2C validation tab is installed and the Phase 2C validation outputs are present.")
        print("Next: open the main dashboard, switch to Developer view, and inspect the Phase 2C validation tab.")
        return 0

    print("REVIEW: One or more checks did not pass.")
    print("If output files are missing, run app\\run_paid_simulator_phase2c_validation_pipeline_check.py first.")
    print("If dashboard markers are missing, re-extract the Phase 2C dashboard-tab package into the project root.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
